# ═══════════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY — الإصدار 13.0 النهائي
# للإنتاج الحيواني وتغذية الحيوان
# إشراف: م. عبدالقادر إسماعيل تاور
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, time, re, io, sqlite3, hashlib, secrets, warnings
import urllib.parse, urllib.request, smtplib, math
from datetime import datetime, timedelta, date
from functools import lru_cache
from typing import Optional, List, Dict
from dataclasses import dataclass, field

warnings.filterwarnings('ignore')

try:
    from scipy.optimize import linprog, minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pytesseract
    import cv2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer,
                                     Image as RLImage, SimpleDocTemplate,
                                     HRFlowable, PageBreak)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_AVAILABLE = True
except ImportError:
    ARABIC_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام، وأسكنهما فسيح جناته"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
DUA_VISITOR_BANNER = """🕌 <b>إلى زوارنا الكرام:</b><br>هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.<br>نسألكم بظهر الغيب أن تشاركونا الدعاء لهما. 🤲"""


APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
APP_VERSION = "13.0"
SUPERVISOR = "م. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
OWNER_CODE = "202687"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
DB_FILE = "tawor_nology_v13.db"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG"]
LOGO_OPTIONS = ["logo.png", "logo.jpg"]

st.set_page_config(page_title=f"{APP_NAME} | {APP_TAGLINE}", page_icon="🌾", layout="wide", initial_sidebar_state="collapsed")


# ═══════════════════════════════════════════════════════════════════════════
# قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════

class DatabaseManager:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self._init_db()
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL"); conn.execute("PRAGMA synchronous=NORMAL")
        return conn
    def _init_db(self):
        conn = self._get_conn(); c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT DEFAULT 'guest', full_name TEXT, email TEXT, phone TEXT, created_date TEXT, last_login TEXT, login_count INTEGER DEFAULT 0, is_active INTEGER DEFAULT 1)''')
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, user_id TEXT, username TEXT, role TEXT, full_name TEXT, phone TEXT, email TEXT, ip_address TEXT, user_agent TEXT, login_time TEXT, last_activity TEXT, activities_count INTEGER DEFAULT 0, actions_log TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS activity_log (log_id TEXT PRIMARY KEY, session_id TEXT, user_id TEXT, username TEXT, action TEXT, details TEXT, timestamp TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (formula_id TEXT PRIMARY KEY, session_id TEXT, username TEXT, animal_type TEXT, production_type TEXT, target_dp REAL, target_se REAL, ingredients TEXT, total_cost REAL, actual_nutrients TEXT, requester_name TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS lab_analyses (analysis_id TEXT PRIMARY KEY, session_id TEXT, username TEXT, animal_type TEXT, state TEXT, sample_id TEXT, ingredients TEXT, actual_nutrients TEXT, standard_nutrients TEXT, overall_score REAL, requester TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS milk_replacers (id TEXT PRIMARY KEY, session_id TEXT, username TEXT, animal_type TEXT, formula TEXT, cost_per_kg REAL, requester TEXT, created_date TEXT)''')
        conn.commit(); conn.close()
    def create_session(self, session_id, user_data, ip_address="", user_agent=""):
        conn = self._get_conn(); c = conn.cursor()
        try:
            c.execute("""INSERT OR REPLACE INTO sessions (session_id, user_id, username, role, full_name, phone, email, ip_address, user_agent, login_time, last_activity, activities_count, actions_log) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '')""", (session_id, user_data.get('user_id', session_id), user_data.get('username', 'زائر'), user_data.get('role', 'guest'), user_data.get('full_name', 'زائر'), user_data.get('phone', ''), user_data.get('email', ''), ip_address, user_agent[:500] if user_agent else '', datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
        except Exception: pass
        conn.close()
    def update_session_activity(self, session_id, action="", details=""):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("SELECT actions_log, activities_count FROM sessions WHERE session_id=?", (session_id,))
        row = c.fetchone()
        if row:
            current_log = row[0] or ""; count = (row[1] or 0) + 1
            new_entry = f"[{datetime.now():%H:%M:%S}] {action}"
            if details: new_entry += f": {details[:100]}"
            updated_log = (current_log + " | " + new_entry)[-2000:]
            c.execute("UPDATE sessions SET last_activity=?, activities_count=?, actions_log=? WHERE session_id=?", (datetime.now().isoformat(), count, updated_log, session_id))
        else:
            c.execute("INSERT OR IGNORE INTO sessions (session_id, username, login_time, last_activity, activities_count, actions_log) VALUES (?, ?, ?, ?, 1, ?)", (session_id, 'زائر', datetime.now().isoformat(), datetime.now().isoformat(), f"[{datetime.now():%H:%M:%S}] {action}"))
        conn.commit(); conn.close()
    def log_activity(self, session_id, user_id, username, action, details=""):
        log_id = secrets.token_hex(12); conn = self._get_conn(); c = conn.cursor()
        c.execute("INSERT INTO activity_log (log_id, session_id, user_id, username, action, details, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", (log_id, session_id, user_id, username, action, details[:500], datetime.now().isoformat()))
        conn.commit(); conn.close()
    def get_all_sessions(self, limit=500):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("SELECT session_id, username, role, full_name, phone, login_time, last_activity, activities_count, ip_address, user_agent FROM sessions ORDER BY last_activity DESC LIMIT ?", (limit,))
        rows = c.fetchall(); conn.close(); return rows
    def get_session_stats(self):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM sessions"); total = c.fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute("SELECT COUNT(*) FROM sessions WHERE login_time LIKE ?", (f"{today}%",)); today_count = c.fetchone()[0]
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        c.execute("SELECT COUNT(*) FROM sessions WHERE login_time > ?", (week_ago,)); week_count = c.fetchone()[0]
        active_30 = (datetime.now() - timedelta(minutes=30)).isoformat()
        c.execute("SELECT COUNT(*) FROM sessions WHERE last_activity > ?", (active_30,)); active = c.fetchone()[0]
        conn.close()
        return {"total": total, "today": today_count, "week": week_count, "active_30min": active}
    def save_formula(self, session_id, username, animal, state, target_dp, target_se, ingredients, cost, actual, requester):
        fid = secrets.token_hex(12); conn = self._get_conn(); c = conn.cursor()
        c.execute("INSERT INTO feed_formulas (formula_id, session_id, username, animal_type, production_type, target_dp, target_se, ingredients, total_cost, actual_nutrients, requester_name, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (fid, session_id, username, animal, state, target_dp, target_se, json.dumps(ingredients, ensure_ascii=False), cost, json.dumps(actual, ensure_ascii=False), requester, datetime.now().isoformat()))
        conn.commit(); conn.close(); return fid
    def save_lab_analysis(self, session_id, username, animal, state, sample_id, ingredients, actual, standard, score, requester):
        aid = secrets.token_hex(12); conn = self._get_conn(); c = conn.cursor()
        c.execute("INSERT INTO lab_analyses (analysis_id, session_id, username, animal_type, state, sample_id, ingredients, actual_nutrients, standard_nutrients, overall_score, requester, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (aid, session_id, username, animal, state, sample_id, json.dumps(ingredients, ensure_ascii=False), json.dumps(actual, ensure_ascii=False), json.dumps(standard, ensure_ascii=False), score, requester, datetime.now().isoformat()))
        conn.commit(); conn.close(); return aid
    def save_milk_replacer(self, session_id, username, animal, formula, cost_kg, requester):
        mid = secrets.token_hex(12); conn = self._get_conn(); c = conn.cursor()
        c.execute("INSERT INTO milk_replacers (id, session_id, username, animal_type, formula, cost_per_kg, requester, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (mid, session_id, username, animal, json.dumps(formula, ensure_ascii=False), cost_kg, requester, datetime.now().isoformat()))
        conn.commit(); conn.close(); return mid
    def get_user_activity_summary(self):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("SELECT username, COUNT(DISTINCT session_id) as sessions, SUM(activities_count) as total_actions, MAX(last_activity) as last_seen, MIN(login_time) as first_seen FROM sessions GROUP BY username ORDER BY last_seen DESC")
        rows = c.fetchall(); conn.close(); return rows
    def get_all_formulas(self, limit=100):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("SELECT username, animal_type, production_type, total_cost, requester_name, created_date FROM feed_formulas ORDER BY created_date DESC LIMIT ?", (limit,))
        rows = c.fetchall(); conn.close(); return rows
    def get_all_lab_analyses(self, limit=100):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("SELECT username, animal_type, state, sample_id, overall_score, requester, created_date FROM lab_analyses ORDER BY created_date DESC LIMIT ?", (limit,))
        rows = c.fetchall(); conn.close(); return rows
    def get_stats(self):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM feed_formulas"); formulas = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM lab_analyses"); labs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM milk_replacers"); milk = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM sessions"); users = c.fetchone()[0]
        conn.close(); return {"formulas": formulas, "labs": labs, "milk": milk, "users": users}

db_manager = DatabaseManager()


# ═══════════════════════════════════════════════════════════════════════════
# الخطوط العربية
# ═══════════════════════════════════════════════════════════════════════════

FONT_DIR = "fonts"; os.makedirs(FONT_DIR, exist_ok=True)
ARABIC_FONT_URLS = [("https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf", "Amiri-Regular.ttf")]

class ArabicFontManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls); cls._instance._init()
        return cls._instance
    def _init(self):
        self.font_name = 'Helvetica'; self.font_bold = 'Helvetica-Bold'; self.ready = False
        if not REPORTLAB_AVAILABLE: return
        paths = [os.path.join(FONT_DIR, "Amiri-Regular.ttf"), "Amiri-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for p in paths:
            if os.path.exists(p):
                if self._register(p): return
        for url, fn in ARABIC_FONT_URLS:
            try:
                target = os.path.join(FONT_DIR, fn)
                if not os.path.exists(target): urllib.request.urlretrieve(url, target)
                if self._register(target): return
            except Exception: continue
    def _register(self, path):
        try:
            pdfmetrics.registerFont(TTFont('TaworArabic', path))
            self.font_name = 'TaworArabic'; self.font_bold = 'TaworArabic'; self.ready = True
            return True
        except Exception: return False

font_mgr = ArabicFontManager()

class ArabicProcessor:
    @staticmethod
    @lru_cache(maxsize=5000)
    def fix(text):
        if text is None or text == "": return ""
        text = str(text)
        if not ARABIC_AVAILABLE: return text
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped, base_dir='R')
        except Exception: return text

arp = ArabicProcessor()
def ar(text): return arp.fix(text)


# ═══════════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف الشاملة (مثل الأصل)
# ═══════════════════════════════════════════════════════════════════════════

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.27},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.26},
        "ذرة شامية": {"CP": 8.3, "DC": 0.86, "SE": 82.0, "NDF": 9.0, "ADF": 3.0, "EE": 4.0, "ASH": 1.2, "Ca": 0.02, "P": 0.28},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35},
        "شعير كامل": {"CP": 10.8, "DC": 0.75, "SE": 68.0, "NDF": 22.0, "ADF": 9.0, "EE": 2.0, "ASH": 2.8, "Ca": 0.05, "P": 0.33},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32},
        "قمح مستورد": {"CP": 11.5, "DC": 0.87, "SE": 78.0, "NDF": 11.0, "ADF": 3.5, "EE": 1.9, "ASH": 1.5, "Ca": 0.04, "P": 0.33},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.06, "P": 0.30},
        "دخن محلي": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Ca": 0.05, "P": 0.31},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.35},
        "كسرة خبز": {"CP": 10.5, "DC": 0.82, "SE": 75.0, "NDF": 8.0, "ADF": 3.5, "EE": 5.5, "ASH": 3.5, "Ca": 0.10, "P": 0.20},
        "بسكويت مكسر": {"CP": 8.5, "DC": 0.85, "SE": 85.0, "NDF": 4.0, "ADF": 2.0, "EE": 12.0, "ASH": 2.5, "Ca": 0.08, "P": 0.18},
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 46%": {"CP": 46.0, "DC": 0.905, "SE": 75.0, "NDF": 12.5, "ADF": 7.5, "EE": 1.6, "ASH": 6.1, "Ca": 0.35, "P": 0.65},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 1.00},
        "كسب عباد الشمس 32%": {"CP": 32.0, "DC": 0.72, "SE": 38.0, "NDF": 42.0, "ADF": 28.0, "EE": 2.0, "ASH": 7.0, "Ca": 0.42, "P": 0.95},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.20, "P": 1.10},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.35, "P": 0.85},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 2.00, "P": 1.20},
        "كسب جلوتين 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.15, "P": 0.50},
        "كسب جلوتين 40%": {"CP": 40.0, "DC": 0.88, "SE": 72.0, "NDF": 15.0, "ADF": 8.0, "EE": 3.0, "ASH": 5.0, "Ca": 0.18, "P": 0.55},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.30, "P": 0.55},
        "كسب الكانولا": {"CP": 36.0, "DC": 0.82, "SE": 60.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 6.5, "Ca": 0.65, "P": 1.10},
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.12, "P": 1.10},
        "نخالة ذرة": {"CP": 9.5, "DC": 0.65, "SE": 40.0, "NDF": 40.0, "ADF": 15.0, "EE": 4.0, "ASH": 2.0, "Ca": 0.10, "P": 0.75},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.50, "P": 0.25},
        "برسيم حجازي": {"CP": 18.0, "DC": 0.62, "SE": 38.0, "NDF": 40.0, "ADF": 30.0, "EE": 2.2, "ASH": 11.0, "Ca": 1.60, "P": 0.26},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.70, "P": 0.05},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.08},
        "تبن فول": {"CP": 4.5, "DC": 0.40, "SE": 22.0, "NDF": 68.0, "ADF": 42.0, "EE": 1.2, "ASH": 7.5, "Ca": 0.35, "P": 0.10},
        "قشر فول سوداني": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5, "Ca": 0.25, "P": 0.10},
        "سرسة الأرز": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08},
        "قش أرز": {"CP": 3.5, "DC": 0.30, "SE": 15.0, "NDF": 70.0, "ADF": 45.0, "EE": 1.5, "ASH": 12.0, "Ca": 0.20, "P": 0.06},
        "مخلفات النخيل": {"CP": 6.5, "DC": 0.70, "SE": 60.0, "NDF": 25.0, "ADF": 15.0, "EE": 5.0, "ASH": 3.5, "Ca": 0.15, "P": 0.15},
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.50, "P": 3.20},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 4.80, "P": 2.80},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 9.00, "P": 4.50},
        "مسحوق الدم": {"CP": 80.0, "DC": 0.65, "SE": 55.0, "NDF": 1.0, "ADF": 0.5, "EE": 1.5, "ASH": 6.0, "Ca": 0.30, "P": 0.30},
        "مسحوق ريش": {"CP": 82.0, "DC": 0.70, "SE": 60.0, "NDF": 1.5, "ADF": 1.0, "EE": 3.0, "ASH": 4.0, "Ca": 0.25, "P": 0.35},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.20},
        "مركزات مواشي": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 3.00, "P": 1.50},
    },
    "🌿 الأعلاف الخضراء المائية": {
        "أزولا مجففة": {"CP": 24.0, "DC": 0.65, "SE": 45.0, "NDF": 38.0, "ADF": 25.0, "EE": 3.5, "ASH": 18.0, "Ca": 2.00, "P": 0.60},
        "سبيرولينا": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 5.0, "ADF": 3.0, "EE": 6.0, "ASH": 10.0, "Ca": 1.20, "P": 0.90},
        "كلوريلا": {"CP": 55.0, "DC": 0.80, "SE": 60.0, "NDF": 6.0, "ADF": 3.5, "EE": 8.0, "ASH": 12.0, "Ca": 0.50, "P": 1.20},
    },
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": {"CP": 0.0, "DC": 0.0, "SE": 220.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة عالية 9000 kcal/kg - NRC 2012", "max_poultry": 6.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت فول الصويا": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "أشهر زيوت الأعلاف - 8800 kcal/kg", "max_poultry": 8.0, "max_ruminant": 5.0, "source": "Ross 308"},
        "زيت عباد الشمس": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بأوميغا 6", "max_poultry": 6.0, "max_ruminant": 4.0, "source": "NRC 2007"},
        "زيت بذرة القطن": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "يحتوي جوسيبول", "max_poultry": 3.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت الكتان": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بأوميغا 3 - ممتاز للخيول", "max_poultry": 3.0, "max_ruminant": 3.0, "source": "NRC 2007"},
        "زيت جوز الهند": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "دهون متوسطة MCT - مضاد بكتيري", "max_poultry": 5.0, "max_ruminant": 3.0, "source": "NRC 2012"},
        "زيت النخيل": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "مقاوم للأكسدة", "max_poultry": 6.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت الكانولا": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "متوازن أوميغا 3 و6", "max_poultry": 5.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت السمسم": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بمضادات الأكسدة", "max_poultry": 4.0, "max_ruminant": 3.0, "source": "NRC 2007"},
        "زيت الزيتون": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بأوميغا 9", "max_poultry": 4.0, "max_ruminant": 4.0, "source": "INRA 2018"},
        "زيت الأفوكادو": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بفيتامين E", "max_poultry": 3.0, "max_ruminant": 3.0, "source": "NRC 2012"},
        "زيت الفول السوداني": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة عالية - 8900 kcal/kg", "max_poultry": 5.0, "max_ruminant": 4.0, "source": "NRC 2012"},
        "شحم حيواني (Tallow)": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة 9500 kcal/kg", "max_poultry": 6.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "دهن الدجاج": {"CP": 0.0, "DC": 0.0, "SE": 225.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "شحم الدواجن المعاد تدويره", "max_poultry": 6.0, "max_ruminant": 0.0, "source": "NRC 2012"},
        "زيت السمك": {"CP": 0.0, "DC": 0.0, "SE": 235.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني EPA/DHA", "max_poultry": 2.0, "max_ruminant": 2.0, "source": "NRC Fish"},
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "تريبتوفان نقي": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "فالين نقي": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 22.0, "P": 7.0},
        "بريمكس أبقار": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس مجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 9.0},
        "بريمكس خيول": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0},
        "بريمكس إبل": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "إنزيم فايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0},
        "كبريتات الحديدوز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0},
        "مستخلص الخمائر MOS": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.10, "P": 0.20},
        "خمائر حية": {"CP": 45.0, "DC": 0.75, "SE": 30.0, "NDF": 8.0, "ADF": 4.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.15, "P": 1.20},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0},
        "فوسفات أحادي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 17.0, "P": 22.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.0, "P": 0.0},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0},
        "مضاد أكسدة BHT": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0},
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# ✅✅✅ التعديل الجديد 1: كل الدول العربية + أسعار الصرف ✅✅✅
# ═══════════════════════════════════════════════════════════════════════════

EXCHANGE_RATES = {
    "السودان":       {"rate": 600.0,    "sym": "SDG"},
    "ليبيا":         {"rate": 4.85,     "sym": "LYD"},
    "مصر":           {"rate": 48.5,     "sym": "EGP"},
    "السعودية":      {"rate": 3.75,     "sym": "SAR"},
    "الإمارات":      {"rate": 3.67,     "sym": "AED"},
    "الكويت":        {"rate": 0.308,    "sym": "KWD"},
    "قطر":           {"rate": 3.64,     "sym": "QAR"},
    "البحرين":       {"rate": 0.376,    "sym": "BHD"},
    "عمان":          {"rate": 0.385,    "sym": "OMR"},
    "اليمن":         {"rate": 530.0,    "sym": "YER"},
    "الأردن":        {"rate": 0.71,     "sym": "JOD"},
    "لبنان":         {"rate": 89500.0,  "sym": "LBP"},
    "سوريا":         {"rate": 13000.0,  "sym": "SYP"},
    "العراق":        {"rate": 1310.0,   "sym": "IQD"},
    "فلسطين":        {"rate": 3.75,     "sym": "ILS"},
    "الجزائر":       {"rate": 134.0,    "sym": "DZD"},
    "المغرب":        {"rate": 10.05,    "sym": "MAD"},
    "تونس":          {"rate": 3.15,     "sym": "TND"},
    "موريتانيا":     {"rate": 39.8,     "sym": "MRU"},
    "الصومال":       {"rate": 571.0,    "sym": "SOS"},
    "جيبوتي":        {"rate": 177.7,    "sym": "DJF"},
    "جزر القمر":     {"rate": 452.0,    "sym": "KMF"},
    "باقي دول العالم": {"rate": 1.0,    "sym": "USD"},
}

# ═══════════════════════════════════════════════════════════════════════════
# ✅✅✅ التعديل الجديد 2: توفّر المواد حسب كل دولة عربية ✅✅✅
# ═══════════════════════════════════════════════════════════════════════════
# آلية العمل:
# - كل دولة لها قائمة "available" للمواد المتوفرة.
# - التركيب الآلي يستخدم فقط المواد المتوفرة في الدولة المختارة.
# - ليبيا مثال رئيسي: لا صويا، لا أمباز فول سوداني، لا ليسين/ميثيونين نقي.

_ALL_INGREDIENTS = [name for cat in BIG_FEEDS_LIBRARY.values() for name in cat.keys()]

# مواد أساسية متوفرة في كل الدول العربية
_BASE_AVAILABLE = [
    "شعير مطحون", "شعير كامل", "ذرة صفراء", "ذرة بيضاء", "سورجم (فتريتة)",
    "نخالة قمح (ردة)", "نخالة ذرة", "البرسيم الجاف", "برسيم حجازي",
    "تبن قمح", "مولاس قصب السكر", "مخلفات النخيل", "دخن محلي",
    "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام",
    "بيكربونات الصوديوم", "أكسيد المغنيسيوم", "مضاد سموم فطرية",
    "يوريا علفية",
]

COUNTRY_AVAILABILITY = {
    # ─── ليبيا (المثال الرئيسي — ندرة مصادر البروتين) ───
    "ليبيا": _BASE_AVAILABLE + [
        "كسب عباد الشمس 36%", "كسب عباد الشمس 32%",
        "كسب بذور القطن", "كسب الكانولا", "كسب جلوتين 40%",
        "مسحوق أسماك 60%", "مسحوق اللحم والعظم",
        "قش أرز", "سرسة الأرز", "تبن فول",
        "شوفان علفي", "كسرة خبز",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "بريمكس خيول", "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت النخيل", "زيت الزيتون",
        "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── مصر ───
    "مصر": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 46%", "كسب فول صويا 48%",
        "أمباز الفول السوداني", "كسب عباد الشمس 36%", "كسب بذور القطن",
        "كسب جلوتين 60%", "كسب جلوتين 40%", "كسب السمسم", "كسب بذور الكتان",
        "مسحوق أسماك 60%", "مسحوق أسماك 72%", "مسحوق الدم", "مسحوق ريش",
        "مركزات دواجن", "مركزات مواشي",
        "قش أرز", "سرسة الأرز", "جريش أرز",
        "قمح محلي", "قمح مستورد", "شوفان علفي", "كسرة خبز", "بسكويت مكسر",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل", "بريمكس خيول",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت فول الصويا", "زيت ذرة", "زيت عباد الشمس", "زيت النخيل",
        "زيت بذرة القطن", "زيت السمسم",
        "ليسين نقي", "ميثيونين نقي", "ثريونين نقي", "تريبتوفان نقي", "فالين نقي",
        "إنزيم فايتيز", "إنزيم NSP", "مستخلص الخمائر MOS", "خمائر حية",
        "مضاد أكسدة BHT",
    ],
    # ─── السودان ───
    "السودان": _BASE_AVAILABLE + [
        "أمباز الفول السوداني", "كسب السمسم", "كسب بذور القطن",
        "كسب عباد الشمس 36%", "كسب بذور الكتان",
        "مسحوق أسماك 60%", "مسحوق اللحم والعظم",
        "مركزات دواجن", "مركزات مواشي",
        "قشر فول سوداني", "تبن فول",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت السمسم", "زيت النخيل", "زيت الفول السوداني",
        "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── السعودية ───
    "السعودية": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 46%", "كسب فول صويا 48%",
        "كسب عباد الشمس 36%", "كسب جلوتين 60%", "كسب جلوتين 40%",
        "مسحوق أسماك 60%", "مسحوق أسماك 72%", "مسحوق الدم", "مسحوق ريش",
        "مركزات دواجن", "مركزات مواشي",
        "قمح محلي", "قمح مستورد",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل", "بريمكس خيول",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت فول الصويا", "زيت ذرة", "زيت النخيل", "زيت عباد الشمس",
        "ليسين نقي", "ميثيونين نقي", "ثريونين نقي",
        "إنزيم فايتيز", "إنزيم NSP", "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── الإمارات ───
    "الإمارات": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 46%", "كسب فول صويا 48%",
        "كسب عباد الشمس 36%", "كسب جلوتين 60%",
        "مسحوق أسماك 60%", "مسحوق أسماك 72%",
        "مركزات دواجن", "مركزات مواشي",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت فول الصويا", "زيت ذرة", "زيت النخيل",
        "ليسين نقي", "ميثيونين نقي",
        "إنزيم فايتيز", "إنزيم NSP", "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── الكويت / قطر / البحرين / عمان (خليج مصغّر) ───
    "الكويت": _BASE_AVAILABLE + ["كسب فول صويا 44%", "كسب فول صويا 48%", "كسب جلوتين 60%", "مسحوق أسماك 60%", "مركزات دواجن", "بريمكس مجترات", "بريمكس أبقار", "بريمكس تسمين دواجن", "بريمكس بياض", "زيت فول الصويا", "زيت ذرة", "ليسين نقي", "ميثيونين نقي", "إنزيم فايتيز"],
    "قطر": _BASE_AVAILABLE + ["كسب فول صويا 44%", "كسب فول صويا 48%", "كسب جلوتين 60%", "مسحوق أسماك 60%", "مركزات دواجن", "بريمكس مجترات", "بريمكس أبقار", "بريمكس تسمين دواجن", "بريمكس بياض", "زيت فول الصويا", "ليسين نقي", "ميثيونين نقي", "إنزيم فايتيز"],
    "البحرين": _BASE_AVAILABLE + ["كسب فول صويا 44%", "كسب فول صويا 48%", "مسحوق أسماك 60%", "مركزات دواجن", "بريمكس مجترات", "بريمكس تسمين دواجن", "بريمكس بياض", "زيت فول الصويا", "ليسين نقي", "ميثيونين نقي"],
    "عمان": _BASE_AVAILABLE + ["كسب فول صويا 44%", "كسب فول صويا 48%", "كسب عباد الشمس 36%", "مسحوق أسماك 60%", "مركزات دواجن", "مركزات مواشي", "بريمكس مجترات", "بريمكس أبقار", "بريمكس تسمين دواجن", "بريمكس بياض", "زيت فول الصويا", "زيت النخيل", "ليسين نقي", "ميثيونين نقي", "إنزيم فايتيز"],
    # ─── اليمن ───
    "اليمن": _BASE_AVAILABLE + [
        "كسب عباد الشمس 36%", "كسب بذور القطن", "كسب السمسم", "كسب الكانولا",
        "مسحوق أسماك 60%", "مسحوق اللحم والعظم",
        "مركزات مواشي", "قشر فول سوداني",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس تسمين دواجن",
        "زيت النخيل", "زيت السمسم",
    ],
    # ─── الأردن ───
    "الأردن": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 46%", "كسب فول صويا 48%",
        "كسب عباد الشمس 36%", "كسب جلوتين 60%", "كسب جلوتين 40%",
        "مسحوق أسماك 60%", "مسحوق الدم", "مسحوق ريش",
        "مركزات دواجن", "مركزات مواشي",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت فول الصويا", "زيت ذرة", "زيت عباد الشمس",
        "ليسين نقي", "ميثيونين نقي", "ثريونين نقي",
        "إنزيم فايتيز", "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── لبنان ───
    "لبنان": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 46%", "كسب فول صويا 48%",
        "كسب عباد الشمس 36%", "كسب جلوتين 60%",
        "مسحوق أسماك 60%", "مسحوق اللحم والعظم",
        "مركزات دواجن",
        "بريمكس مجترات", "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت فول الصويا", "زيت ذرة", "زيت الزيتون",
        "ليسين نقي", "ميثيونين نقي", "إنزيم فايتيز",
    ],
    # ─── سوريا ───
    "سوريا": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب عباد الشمس 36%", "كسب بذور القطن",
        "كسب جلوتين 40%", "مسحوق أسماك 60%", "مسحوق اللحم والعظم",
        "مركزات دواجن", "مركزات مواشي",
        "قشر فول سوداني", "تبن فول", "سرسة الأرز",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت النخيل", "زيت الزيتون", "زيت بذرة القطن",
        "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── العراق ───
    "العراق": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 46%", "كسب عباد الشمس 36%",
        "كسب بذور القطن", "كسب جلوتين 40%",
        "مسحوق أسماك 60%", "مسحوق اللحم والعظم",
        "مركزات دواجن", "مركزات مواشي",
        "قمح محلي", "قش أرز", "سرسة الأرز", "جريش أرز",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت النخيل", "زيت بذرة القطن", "زيت عباد الشمس",
        "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── فلسطين ───
    "فلسطين": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 48%", "كسب عباد الشمس 36%",
        "مسحوق أسماك 60%", "مركزات دواجن",
        "بريمكس مجترات", "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت فول الصويا", "زيت الزيتون",
        "ليسين نقي", "ميثيونين نقي", "إنزيم فايتيز",
    ],
    # ─── الجزائر ───
    "الجزائر": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 48%", "كسب عباد الشمس 36%",
        "كسب جلوتين 40%", "مسحوق أسماك 60%",
        "مركزات دواجن", "مركزات مواشي",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت فول الصويا", "زيت عباد الشمس", "زيت الزيتون",
        "ليسين نقي", "ميثيونين نقي", "إنزيم فايتيز",
        "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── المغرب ───
    "المغرب": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 46%", "كسب فول صويا 48%",
        "كسب عباد الشمس 36%", "كسب جلوتين 60%", "كسب جلوتين 40%",
        "مسحوق أسماك 60%", "مسحوق أسماك 72%", "مسحوق الدم",
        "مركزات دواجن", "مركزات مواشي",
        "قمح محلي", "كسرة خبز",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت فول الصويا", "زيت النخيل", "زيت عباد الشمس",
        "ليسين نقي", "ميثيونين نقي", "ثريونين نقي",
        "إنزيم فايتيز", "إنزيم NSP", "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── تونس ───
    "تونس": _BASE_AVAILABLE + [
        "كسب فول صويا 44%", "كسب فول صويا 48%",
        "كسب عباد الشمس 36%", "كسب جلوتين 40%",
        "مسحوق أسماك 60%", "مسحوق اللحم والعظم",
        "مركزات دواجن", "مركزات مواشي",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "بريمكس تسمين دواجن", "بريمكس بياض",
        "زيت فول الصويا", "زيت الزيتون",
        "ليسين نقي", "ميثيونين نقي", "إنزيم فايتيز",
        "مستخلص الخمائر MOS", "خمائر حية",
    ],
    # ─── موريتانيا ───
    "موريتانيا": _BASE_AVAILABLE + [
        "كسب عباد الشمس 36%", "كسب الكانولا",
        "مسحوق أسماك 60%", "مسحوق أسماك 72%", "مسحوق اللحم والعظم",
        "مركزات مواشي",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "زيت النخيل", "زيت السمك",
    ],
    # ─── الصومال ───
    "الصومال": _BASE_AVAILABLE + [
        "كسب عباد الشمس 36%", "كسب السمسم", "كسب الكانولا",
        "مسحوق أسماك 60%", "مسحوق اللحم والعظم",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "زيت النخيل", "زيت السمسم",
    ],
    # ─── جيبوتي ───
    "جيبوتي": _BASE_AVAILABLE + [
        "كسب عباد الشمس 36%", "مسحوق أسماك 60%", "مسحوق أسماك 72%",
        "بريمكس مجترات", "بريمكس أبقار", "بريمكس إبل",
        "زيت النخيل", "زيت السمك",
    ],
    # ─── جزر القمر ───
    "جزر القمر": _BASE_AVAILABLE + [
        "كسب عباد الشمس 36%", "مسحوق أسماك 60%",
        "بريمكس مجترات", "زيت النخيل", "زيت جوز الهند",
    ],
    # ─── باقي دول العالم ───
    "باقي دول العالم": _ALL_INGREDIENTS,
}

def get_country_available_ingredients(country):
    """يُرجع مجموعة أسماء المواد المتوفرة في الدولة المختارة"""
    if country in COUNTRY_AVAILABILITY:
        return set(COUNTRY_AVAILABILITY[country])
    return set(_ALL_INGREDIENTS)

def is_ingredient_available(country, ingredient):
    return ingredient in get_country_available_ingredients(country)


# ═══════════════════════════════════════════════════════════════════════════
# معايير الزيوت (مثل الأصل)
# ═══════════════════════════════════════════════════════════════════════════

MAX_OIL_PERCENTAGE = {
    "أبقار_حليب_عالي": {"max": 6.0, "optimal": 4.0, "source": "NRC 2001"},
    "أبقار_حليب_متوسط": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_حليب_منخفض": {"max": 5.0, "optimal": 3.0, "source": "NRC 2001"},
    "أبقار_تسمين_مكثف": {"max": 6.0, "optimal": 4.5, "source": "NRC 2001"},
    "أبقار_تسمين_عادي": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_حمل_أخير": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_صيانة": {"max": 4.0, "optimal": 2.5, "source": "NRC 2001"},
    "أغنام_تسمين_مكثف": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_تسمين_عادي": {"max": 4.5, "optimal": 3.0, "source": "NRC 2007"},
    "أغنام_حملان_تيد": {"max": 4.0, "optimal": 2.5, "source": "NRC 2007"},
    "أغنام_مرضعات": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_حامل_أخير": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_حامل_متوسط": {"max": 4.0, "optimal": 2.5, "source": "NRC 2007"},
    "أغنام_صيانة": {"max": 3.5, "optimal": 2.0, "source": "NRC 2007"},
    "ماعز_تسمين_جديان": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_تيوس": {"max": 4.5, "optimal": 3.0, "source": "NRC 2007"},
    "ماعز_حلابة_عالي": {"max": 5.5, "optimal": 4.0, "source": "NRC 2007"},
    "ماعز_حلابة_متوسط": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_حامل_أخير": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_صيانة": {"max": 3.5, "optimal": 2.0, "source": "NRC 2007"},
    "إبل_نمو": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "إبل_تسمين": {"max": 6.0, "optimal": 4.0, "source": "FAO 2010"},
    "إبل_حليب": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "إبل_سباق": {"max": 8.0, "optimal": 6.0, "source": "FAO 2010"},
    "إبل_صيانة": {"max": 3.5, "optimal": 2.0, "source": "FAO 2010"},
    "خيول_رياضة_مكثف": {"max": 10.0, "optimal": 7.0, "source": "NRC 2007"},
    "خيول_رياضة_عادي": {"max": 8.0, "optimal": 5.0, "source": "NRC 2007"},
    "خيول_نمو_أمهار": {"max": 8.0, "optimal": 5.0, "source": "NRC 2007"},
    "خيول_مرضعات": {"max": 8.0, "optimal": 5.5, "source": "NRC 2007"},
    "خيول_صيانة": {"max": 5.0, "optimal": 3.0, "source": "NRC 2007"},
    "دواجن_لاحم_بادي": {"max": 8.0, "optimal": 5.0, "source": "Ross 308"},
    "دواجن_لاحم_نامي": {"max": 7.0, "optimal": 4.5, "source": "Ross 308"},
    "دواجن_لاحم_ناهي": {"max": 7.0, "optimal": 4.0, "source": "Ross 308"},
    "دواجن_بياض_بادي": {"max": 5.0, "optimal": 2.5, "source": "NRC 1994"},
    "دواجن_بياض_نامي": {"max": 5.0, "optimal": 2.5, "source": "NRC 1994"},
    "دواجن_بياض_إنتاج": {"max": 5.0, "optimal": 3.0, "source": "NRC 1994"},
    "سمان_تسمين": {"max": 6.0, "optimal": 4.0, "source": "NRC Quail"},
    "سمان_بياض": {"max": 5.0, "optimal": 2.5, "source": "NRC Quail"},
    "أسماك_بادئ_زريعة": {"max": 15.0, "optimal": 10.0, "source": "NRC Fish"},
    "أسماك_نمو": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish"},
    "أسماك_تسمين": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish"},
}

def get_oil_standard(standard_key):
    return MAX_OIL_PERCENTAGE.get(standard_key, {"max": 5.0, "optimal": 3.0, "source": "معيار عام - NRC"})

def get_oil_ingredients():
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


# ═══════════════════════════════════════════════════════════════════════════
# الاحتياجات المتخصصة (كما الأصل)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AnimalRequirement:
    DP: float; CP: float; SE: float; NDF: float; ADF: float
    EE: float; ASH: float; Ca: float; P: float
    name_ar: str = ""; note: str = ""

def get_cattle_requirements(production_type, milk_yield=20.0, weight_kg=500.0):
    if production_type == "حليب_عالي":
        dp = 12.5 + (milk_yield * 0.30); cp = dp / 0.70
        return AnimalRequirement(round(dp,2), round(cp,2), round(60+milk_yield*0.35,1), 30.0, 19.0, 5.5, 8.0, round(0.55+milk_yield*0.003,3), round(0.33+milk_yield*0.0015,3), "أبقار حلابة عالية", f"إنتاج {milk_yield} كجم/يوم | {weight_kg} كجم")
    elif production_type == "حليب_متوسط":
        dp = 11.0 + (milk_yield * 0.25); cp = dp / 0.72
        return AnimalRequirement(round(dp,2), round(cp,2), round(55+milk_yield*0.30,1), 33.0, 21.0, 4.5, 8.0, round(0.50+milk_yield*0.0025,3), round(0.30+milk_yield*0.0012,3), "أبقار حلابة متوسطة")
    elif production_type == "حليب_منخفض":
        dp = 9.5 + (milk_yield * 0.20); cp = dp / 0.75
        return AnimalRequirement(round(dp,2), round(cp,2), round(50+milk_yield*0.25,1), 38.0, 24.0, 4.0, 8.5, round(0.45+milk_yield*0.002,3), round(0.28+milk_yield*0.001,3), "أبقار حلابة منخفضة")
    elif production_type == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72.0, 32.0, 20.0, 4.5, 7.5, 0.65, 0.38, "تسمين عجول مكثف")
    elif production_type == "تسمين_عادي":
        return AnimalRequirement(9.5, 12.0, 65.0, 38.0, 24.0, 4.0, 7.5, 0.55, 0.32, "تسمين عجول عادي")
    elif production_type == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67.0, 35.0, 22.0, 4.2, 8.0, 0.70, 0.42, "حمل آخر")
    else:
        return AnimalRequirement(7.5, 10.0, 53.0, 45.0, 28.0, 3.0, 8.5, 0.42, 0.26, "أبقار صيانة")

def get_sheep_requirements(production_type, is_male=True, weight_kg=50.0, litter_size=1):
    if is_male:
        if production_type == "تسمين_مكثف": return AnimalRequirement(11.5, 14.5, 64.0, 28.0, 17.0, 4.0, 8.0, 0.65, 0.36, "تسمين حملان مكثف")
        elif production_type == "تسمين_عادي": return AnimalRequirement(9.5, 12.0, 59.0, 33.0, 21.0, 3.6, 8.0, 0.55, 0.32, "تسمين حملان عادي")
        else: return AnimalRequirement(8.5, 11.0, 55.0, 38.0, 24.0, 3.2, 8.5, 0.50, 0.30, "حملان تيد")
    else:
        if production_type == "مرضعات":
            dp = 10.5 + (litter_size-1)*1.5; cp = dp/0.72
            return AnimalRequirement(round(dp,2), round(cp,2), round(60+(litter_size-1)*5,1), 30.0, 19.0, 4.5, 8.5, round(0.65+(litter_size-1)*0.10,3), round(0.38+(litter_size-1)*0.05,3), f"نعاج مرضعات ({litter_size})")
        elif production_type == "حامل_أخير": return AnimalRequirement(10.5, 13.5, 62.0, 32.0, 20.0, 3.8, 8.0, 0.60, 0.35, "نعاج حامل (4-5)")
        elif production_type == "حامل_متوسط": return AnimalRequirement(8.5, 11.0, 55.0, 38.0, 24.0, 3.4, 8.0, 0.50, 0.30, "نعاج حامل (1-3)")
        else: return AnimalRequirement(7.2, 9.5, 48.0, 45.0, 28.0, 3.0, 8.5, 0.42, 0.26, "نعاج صيانة")

def get_goat_requirements(production_type, is_male=True, milk_yield=2.0):
    if is_male:
        if production_type == "تسمين_جديان": return AnimalRequirement(11.0, 14.0, 62.0, 30.0, 19.0, 3.8, 8.0, 0.62, 0.34, "تسمين جديان")
        else: return AnimalRequirement(9.0, 11.5, 57.0, 36.0, 22.0, 3.5, 8.0, 0.55, 0.30, "تيوس تسمين")
    else:
        if production_type == "حلابة_عالي":
            dp = 11.5 + (milk_yield*0.45); cp = dp/0.70
            return AnimalRequirement(round(dp,2), round(cp,2), round(58+milk_yield*0.45,1), 29.0, 18.0, 4.5, 8.5, round(0.60+milk_yield*0.008,3), round(0.35+milk_yield*0.004,3), f"عنزات حلابة عالي ({milk_yield})")
        elif production_type == "حلابة_متوسط":
            dp = 10.0 + (milk_yield*0.35); cp = dp/0.72
            return AnimalRequirement(round(dp,2), round(cp,2), round(55+milk_yield*0.40,1), 32.0, 20.0, 4.0, 8.5, round(0.55+milk_yield*0.006,3), round(0.32+milk_yield*0.003,3), f"عنزات حلابة متوسط ({milk_yield})")
        elif production_type == "حامل_أخير": return AnimalRequirement(10.0, 13.0, 60.0, 33.0, 21.0, 3.8, 8.0, 0.60, 0.35, "عنزات حامل")
        else: return AnimalRequirement(6.8, 9.0, 46.0, 46.0, 28.0, 3.0, 8.5, 0.42, 0.26, "عنزات صيانة")

def get_camel_requirements(production_type, weight_kg=400.0, milk_yield=5.0):
    dm_kg = weight_kg * 0.025
    if production_type == "نمو": return AnimalRequirement(10.5, 13.5, 60.0, 38.0, 24.0, 4.0, 8.0, 0.65, 0.38, "إبل نمو", f"وزن {weight_kg} كجم | DM {dm_kg:.1f}")
    elif production_type == "تسمين": return AnimalRequirement(9.5, 12.0, 65.0, 35.0, 22.0, 4.5, 7.5, 0.60, 0.35, "إبل تسمين")
    elif production_type == "حليب":
        dp = 12.0 + (milk_yield*0.25); cp = dp/0.70
        return AnimalRequirement(round(dp,2), round(cp,2), round(62+milk_yield*0.40,1), 32.0, 20.0, 5.0, 8.5, round(0.70+milk_yield*0.006,3), round(0.40+milk_yield*0.003,3), f"إبل حلابة ({milk_yield} لتر)")
    elif production_type == "سباق": return AnimalRequirement(14.0, 17.0, 72.0, 28.0, 17.0, 6.0, 9.0, 0.85, 0.50, "إبل سباق")
    else: return AnimalRequirement(7.0, 9.0, 48.0, 48.0, 30.0, 3.5, 9.0, 0.42, 0.26, "إبل صيانة")

def get_horse_requirements(production_type, weight_kg=450.0):
    if production_type == "رياضة_مكثف": return AnimalRequirement(10.5, 13.5, 70.0, 30.0, 18.0, 7.0, 7.5, 0.70, 0.40, "خيول رياضة مكثف")
    elif production_type == "رياضة_عادي": return AnimalRequirement(9.0, 11.5, 63.0, 36.0, 22.0, 5.0, 7.5, 0.55, 0.32, "خيول رياضة عادي")
    elif production_type == "نمو_أمهار": return AnimalRequirement(12.0, 15.0, 65.0, 30.0, 18.0, 5.0, 8.0, 0.75, 0.42, "أمهار نمو")
    elif production_type == "مرضعات": return AnimalRequirement(12.5, 16.0, 68.0, 32.0, 20.0, 5.5, 8.0, 0.80, 0.45, "فرسات مرضعات")
    else: return AnimalRequirement(7.2, 9.5, 53.0, 46.0, 29.0, 3.5, 8.0, 0.45, 0.28, "خيول صيانة")

def get_poultry_requirements(strain, age_weeks=1):
    if strain == "لاحم":
        if age_weeks <= 1: return AnimalRequirement(20.0, 23.0, 76.0, 8.0, 4.0, 5.0, 6.5, 1.00, 0.50, "بادي لاحم")
        elif age_weeks <= 3: return AnimalRequirement(18.5, 21.0, 74.0, 9.0, 5.0, 5.0, 6.0, 0.90, 0.45, "نامي لاحم")
        elif age_weeks <= 5: return AnimalRequirement(17.0, 19.5, 75.0, 10.0, 5.5, 4.5, 6.0, 0.87, 0.43, "ناهي لاحم")
        else: return AnimalRequirement(16.5, 19.0, 75.0, 10.0, 5.5, 4.5, 6.0, 0.85, 0.42, "ناهي لاحم")
    else:
        if age_weeks <= 6: return AnimalRequirement(17.0, 20.0, 72.0, 10.0, 5.5, 4.0, 7.0, 1.00, 0.50, "بادي بياض")
        elif age_weeks <= 18: return AnimalRequirement(14.5, 17.0, 70.0, 12.0, 6.5, 4.0, 9.0, 1.50, 0.45, "نامي بياض")
        else: return AnimalRequirement(15.5, 18.0, 72.0, 11.0, 6.0, 4.2, 11.5, 3.80, 0.45, "بياض إنتاجي")

def get_quail_requirements(strain, age_weeks=1):
    if strain == "بياض": return AnimalRequirement(15.0, 18.0, 68.0, 11.0, 5.5, 4.5, 9.0, 2.50, 0.45, "سمان بياض")
    else:
        if age_weeks <= 2: return AnimalRequirement(20.5, 24.0, 74.0, 8.0, 4.0, 5.5, 6.5, 1.00, 0.55, "سمان بادي")
        elif age_weeks <= 4: return AnimalRequirement(18.5, 22.0, 72.0, 9.0, 4.5, 5.0, 6.0, 0.90, 0.50, "سمان نامي")
        else: return AnimalRequirement(17.0, 20.0, 70.0, 10.0, 5.0, 4.5, 6.0, 0.85, 0.45, "سمان ناهي")

def get_fish_requirements(species, stage):
    if "زريعة" in stage or "بادئ" in stage: return AnimalRequirement(32.0, 40.0, 72.0, 8.0, 4.0, 10.0, 11.0, 1.50, 0.90, f"{species} — بادئ")
    elif "نمو" in stage: return AnimalRequirement(25.0, 32.0, 70.0, 12.0, 6.0, 8.0, 9.0, 1.00, 0.70, f"{species} — نمو")
    else: return AnimalRequirement(22.0, 28.0, 68.0, 13.0, 7.0, 8.0, 9.5, 0.90, 0.65, f"{species} — تسمين")

def requirement_to_standard(req):
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE, "NDF": req.NDF, "ADF": req.ADF, "EE": req.EE, "ASH": req.ASH, "Ca": req.Ca, "P": req.P}


# ═══════════════════════════════════════════════════════════════════════════
# دوال المختبر
# ═══════════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula):
    totals = {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0}
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                d = cat[ing]; f = pct / 100.0
                totals["CP"] += f * d.get("CP", 0.0)
                totals["DP"] += f * d.get("CP", 0.0) * d.get("DC", 0.0)
                totals["SE"] += f * d.get("SE", 0.0)
                totals["NDF"] += f * d.get("NDF", 0.0)
                totals["ADF"] += f * d.get("ADF", 0.0)
                totals["EE"] += f * d.get("EE", 0.0)
                totals["ASH"] += f * d.get("ASH", 0.0)
                totals["Ca"] += f * d.get("Ca", 0.0)
                totals["P"] += f * d.get("P", 0.0)
                break
    return totals

def compute_total_oil_percentage(formula):
    oils = set(get_oil_ingredients().keys())
    return sum(pct for ing, pct in formula.items() if ing in oils)

def evaluate_difference(pct_diff):
    a = abs(pct_diff)
    if a <= 0.5: return {"label": "🎯 مطابق تماماً", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
    elif a <= 2.0: return {"label": "🌟 ممتاز", "color": "#1b5e20", "bg": "#dcedc8", "score": 95}
    elif a <= 5.0: return {"label": "✅ جيد جداً", "color": "#2e7d32", "bg": "#e8f5e9", "score": 85}
    elif a <= 10.0: return {"label": "🟢 جيد", "color": "#558b2f", "bg": "#f1f8e9", "score": 75}
    elif a <= 15.0: return {"label": "⭐ مقبول", "color": "#f9a825", "bg": "#fff8e1", "score": 65}
    elif a <= 25.0: return {"label": "⚠️ مقبول بتحفظ", "color": "#ef6c00", "bg": "#fff3e0", "score": 50}
    elif a <= 40.0: return {"label": "🟠 ضعيف", "color": "#e65100", "bg": "#ffe0b2", "score": 35}
    else: return {"label": "❌ غير مطابق", "color": "#c62828", "bg": "#ffebee", "score": 20}

def get_overall_rating(compare_rows):
    if not compare_rows: return {"label": "غير محدد", "color": "#666", "score": 0}
    scores = [r.get("score", 50) for r in compare_rows]
    avg = sum(scores) / len(scores)
    if avg >= 95: return {"label": "🏆 خلطة ممتازة", "color": "#1b5e20", "score": avg}
    elif avg >= 85: return {"label": "🌟 خلطة جيدة جداً", "color": "#2e7d32", "score": avg}
    elif avg >= 70: return {"label": "✅ خلطة جيدة", "color": "#558b2f", "score": avg}
    elif avg >= 55: return {"label": "⭐ خلطة مقبولة", "color": "#f9a825", "score": avg}
    else: return {"label": "⚠️ تحتاج تحسين", "color": "#e65100", "score": avg}

def get_animal_options_for_lab():
    return {
        "أبقار": {"states": {"حليب_عالي": "حلابة عالية", "حليب_متوسط": "حلابة متوسطة", "حليب_منخفض": "حلابة منخفضة", "تسمين_مكثف": "تسمين مكثف", "تسمين_عادي": "تسمين عادي", "حمل_أخير": "حمل آخر", "صيانة": "صيانة"}, "needs_extra": ["milk_yield", "weight_kg"], "default_extra": {"milk_yield": 20.0, "weight_kg": 500.0}},
        "أغنام": {"states": {"تسمين_مكثف": "تسمين مكثف", "تسمين_عادي": "تسمين عادي", "حملان_تيد": "حملان تيد", "مرضعات": "نعاج مرضعات", "حامل_أخير": "حامل (4-5)", "حامل_متوسط": "حامل (1-3)", "صيانة": "صيانة"}, "needs_extra": ["is_male", "weight_kg", "litter_size"], "default_extra": {"is_male": True, "weight_kg": 50.0, "litter_size": 1}},
        "ماعز": {"states": {"تسمين_جديان": "تسمين جديان", "تيوس": "تيوس", "حلابة_عالي": "حلابة عالي", "حلابة_متوسط": "حلابة متوسط", "حامل_أخير": "حامل", "صيانة": "صيانة"}, "needs_extra": ["is_male", "milk_yield"], "default_extra": {"is_male": True, "milk_yield": 2.0}},
        "إبل": {"states": {"نمو": "نمو", "تسمين": "تسمين", "حليب": "حلابة", "سباق": "سباق", "صيانة": "صيانة"}, "needs_extra": ["weight_kg", "milk_yield"], "default_extra": {"weight_kg": 400.0, "milk_yield": 5.0}},
        "خيول": {"states": {"رياضة_مكثف": "رياضة مكثف", "رياضة_عادي": "رياضة عادي", "نمو_أمهار": "أمهار", "مرضعات": "مرضعات", "صيانة": "صيانة"}, "needs_extra": ["weight_kg"], "default_extra": {"weight_kg": 450.0}},
        "دواجن": {"states": {"لاحم_بادي": "لاحم بادي", "لاحم_نامي": "لاحم نامي", "لاحم_ناهي": "لاحم ناهي", "بياض_بادي": "بياض بادي", "بياض_نامي": "بياض نامي", "بياض_إنتاج": "بياض إنتاجي"}, "needs_extra": ["age_weeks"], "default_extra": {"age_weeks": 1}},
        "سمان": {"states": {"تسمين": "تسمين", "بياض": "بياض"}, "needs_extra": ["age_weeks"], "default_extra": {"age_weeks": 1}},
        "أسماك": {"states": {"بادئ_زريعة": "بادئ زريعة", "نمو": "نمو", "تسمين": "تسمين"}, "needs_extra": ["species"], "default_extra": {"species": "البلطي النيلي"}},
    }

def build_requirement_for_lab(animal, state, extra=None):
    extra = extra or {}
    if animal == "أبقار": return get_cattle_requirements(state, milk_yield=extra.get("milk_yield", 20.0), weight_kg=extra.get("weight_kg", 500.0))
    elif animal == "أغنام": return get_sheep_requirements(state, is_male=extra.get("is_male", True), weight_kg=extra.get("weight_kg", 50.0), litter_size=extra.get("litter_size", 1))
    elif animal == "ماعز": return get_goat_requirements(state, is_male=extra.get("is_male", True), milk_yield=extra.get("milk_yield", 2.0))
    elif animal == "إبل": return get_camel_requirements(state, weight_kg=extra.get("weight_kg", 400.0), milk_yield=extra.get("milk_yield", 5.0))
    elif animal == "خيول": return get_horse_requirements(state, weight_kg=extra.get("weight_kg", 450.0))
    elif animal == "دواجن":
        strain = "بياض" if state.startswith("بياض") else "لاحم"
        return get_poultry_requirements(strain, extra.get("age_weeks", 1))
    elif animal == "سمان": return get_quail_requirements(state, extra.get("age_weeks", 1))
    elif animal == "أسماك": return get_fish_requirements(extra.get("species", "البلطي النيلي"), state)
    return None

def get_standard_key_for_lab(animal, state): return f"{animal}_{state}"

def analyze_ready_mixture(ingredients, animal, state, extra=None):
    ingredients = {k: v for k, v in ingredients.items() if v > 0}
    total_weight = sum(ingredients.values())
    if total_weight <= 0: return {"success": False, "message": "لم يتم إدخال أي وزن"}
    formula_pct = {k: (v/total_weight*100) for k, v in ingredients.items()}
    actual = compute_formula_nutrients(formula_pct)
    requirement = build_requirement_for_lab(animal, state, extra)
    if requirement is None: return {"success": False, "message": "تعذر تحديد المعيار"}
    standard = requirement_to_standard(requirement)
    compare_rows = []; scores = []
    labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP", "SE": "معادل النشاء SE", "NDF": "ألياف NDF", "ADF": "ألياف ADF", "EE": "دهن خام EE", "ASH": "رماد ASH", "Ca": "كالسيوم Ca", "P": "فسفور P"}
    units = {"CP": "%", "DP": "%", "SE": "", "NDF": "%", "ADF": "%", "EE": "%", "ASH": "%", "Ca": "%", "P": "%"}
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard: continue
        sv = standard[k]; cv = actual.get(k, 0.0)
        diff = cv - sv; pct = ((diff/sv*100) if sv > 0 else 0)
        ev = evaluate_difference(pct)
        violation = ""
        if abs(pct) > 5: violation = "زيادة" if diff > 0 else "نقص"
        compare_rows.append({"العنصر": labels.get(k,k), "المعيار": f"{sv:.2f}{units[k]}", "المحسوب": f"{cv:.2f}{units[k]}", "الفرق": f"{diff:+.3f}", "الفرق %": f"{pct:+.2f}%", "الحالة": violation if violation else "مطابق", "التقييم": ev["label"], "_score": ev["score"], "_pct": pct, "_diff": diff})
        scores.append({"score": ev["score"]})
    overall = get_overall_rating(scores)
    total_oil = compute_total_oil_percentage(formula_pct)
    oil_std = get_oil_standard(get_standard_key_for_lab(animal, state))
    oil_check = {"total": total_oil, "max": oil_std["max"], "optimal": oil_std["optimal"], "source": oil_std["source"], "status": ("exceeded" if total_oil > oil_std["max"] else ("high" if total_oil > oil_std["optimal"]*1.2 else "ok"))}
    violations = []
    for row in compare_rows:
        if abs(row["_pct"]) > 5:
            violations.append({"element": row["العنصر"], "target": row["المعيار"], "actual": row["المحسوب"], "diff": row["الفرق %"], "type": row["الحالة"]})
    return {"success": True, "total_weight": total_weight, "formula_pct": formula_pct, "actual": actual, "standard": standard, "requirement": requirement, "compare_rows": compare_rows, "overall": overall, "oil_check": oil_check, "violations": violations, "animal": animal, "state": state}

def generate_recommendations(analysis):
    recommendations = []
    for row in analysis["compare_rows"]:
        pct = row["_pct"]
        if abs(pct) <= 5: continue
        element = row["العنصر"]; diff = row["_diff"]
        if "بروتين" in element and diff < 0: recommendations.append(f"⬆️ **زيادة البروتين**: أضف كسب صويا أو أمباز الفول بمقدار {abs(diff):.2f}%")
        elif "بروتين" in element and diff > 0: recommendations.append("⬇️ **تقليل البروتين**: قلل مصادر البروتين")
        elif "النشاء" in element and diff < 0: recommendations.append(f"⬆️ **زيادة الطاقة**: أضف ذرة أو شعير أو زيوت بمقدار {abs(diff):.2f}")
        elif "النشاء" in element and diff > 0: recommendations.append("⬇️ **تقليل الطاقة**: قلل الحبوب")
        elif "NDF" in element or "ADF" in element:
            if diff > 0: recommendations.append("⬇️ **تقليل الألياف**: قلل التبن")
            else: recommendations.append("⬆️ **زيادة الألياف**: أضف دريس")
        elif "كالسيوم" in element and diff < 0: recommendations.append("⬆️ أضف الحجر الجيري")
        elif "فسفور" in element and diff < 0: recommendations.append("⬆️ أضف فوسفات ثنائي الكالسيوم")
    oil = analysis["oil_check"]
    if oil["status"] == "exceeded": recommendations.append(f"⚠️ **الزيوت تجاوزت**: {oil['total']:.2f}% > {oil['max']}%")
    elif oil["status"] == "high": recommendations.append(f"⚡ **الزيوت مرتفعة**: {oil['total']:.2f}%")
    if not recommendations: recommendations.append("✅ **الخلطة ممتازة** — جميع العناصر مطابقة")
    return recommendations


# ═══════════════════════════════════════════════════════════════════════════
# المكونات الموصى بها لكل حيوان
# ═══════════════════════════════════════════════════════════════════════════

RECOMMENDED_INGREDIENTS = {
    "أبقار": {
        "تسمين": ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 44%", "نخالة قمح (ردة)", "البرسيم الجاف", "مولاس قصب السكر", "زيت ذرة", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بيكربونات الصوديوم", "مضاد سموم فطرية", "بريمكس مجترات"],
        "حليب": ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 48%", "نخالة قمح (ردة)", "البرسيم الجاف", "كسب عباد الشمس 36%", "زيت النخيل", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بيكربونات الصوديوم", "بريمكس أبقار", "مضاد سموم فطرية"],
        "صيانة": ["سورجم (فتريتة)", "نخالة قمح (ردة)", "تبن قمح", "البرسيم الجاف", "الحجر الجيري", "ملح الطعام", "بريمكس مجترات"],
    },
    "أغنام": {
        "تسمين": ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 44%", "نخالة قمح (ردة)", "مولاس قصب السكر", "زيت ذرة", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بيكربونات الصوديوم", "بريمكس مجترات", "مضاد سموم فطرية"],
        "حليب": ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 48%", "نخالة قمح (ردة)", "البرسيم الجاف", "زيت النخيل", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بيكربونات الصوديوم", "بريمكس مجترات"],
        "صيانة": ["سورجم (فتريتة)", "نخالة قمح (ردة)", "تبن قمح", "البرسيم الجاف", "الحجر الجيري", "ملح الطعام", "بريمكس مجترات"],
    },
    "ماعز": {
        "تسمين": ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 44%", "نخالة قمح (ردة)", "البرسيم الجاف", "زيت ذرة", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بيكربونات الصوديوم", "بريمكس مجترات"],
        "حليب": ["ذرة صفراء", "كسب فول صويا 48%", "نخالة قمح (ردة)", "البرسيم الجاف", "زيت النخيل", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بيكربونات الصوديوم", "بريمكس مجترات"],
        "صيانة": ["سورجم (فتريتة)", "نخالة قمح (ردة)", "تبن قمح", "البرسيم الجاف", "الحجر الجيري", "ملح الطعام"],
    },
    "إبل": {
        "نمو": ["شعير مطحون", "ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)", "البرسيم الجاف", "مخلفات النخيل", "زيت ذرة", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بيكربونات الصوديوم", "بريمكس إبل"],
        "تسمين": ["شعير مطحون", "ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)", "مولاس قصب السكر", "زيت النخيل", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بيكربونات الصوديوم", "بريمكس إبل"],
        "حليب": ["شعير مطحون", "كسب فول صويا 48%", "نخالة قمح (ردة)", "البرسيم الجاف", "زيت النخيل", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بريمكس إبل"],
        "سباق": ["شعير مطحون", "ذرة صفراء", "كسب فول صويا 48%", "زيت فول الصويا", "زيت ذرة", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بريمكس إبل"],
        "صيانة": ["شعير مطحون", "نخالة قمح (ردة)", "تبن قمح", "مخلفات النخيل", "الحجر الجيري", "ملح الطعام", "بريمكس إبل"],
    },
    "خيول": {
        "رياضة": ["شعير مطحون", "شوفان علفي", "كسب فول صويا 44%", "البرسيم الجاف", "زيت الكتان", "زيت ذرة", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بريمكس خيول"],
        "نمو": ["شعير مطحون", "شوفان علفي", "كسب فول صويا 48%", "البرسيم الجاف", "زيت الكتان", "زيت النخيل", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بريمكس خيول"],
        "صيانة": ["شعير مطحون", "شوفان علفي", "نخالة قمح (ردة)", "البرسيم الجاف", "الحجر الجيري", "ملح الطعام", "بريمكس خيول"],
    },
    "دواجن": {
        "بادي": ["ذرة صفراء", "كسب فول صويا 48%", "كسب جلوتين 60%", "مسحوق أسماك 60%", "زيت فول الصويا", "زيت ذرة", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "ليسين نقي", "ميثيونين نقي", "بريمكس تسمين دواجن", "مضاد سموم فطرية", "إنزيم فايتيز", "إنزيم NSP"],
        "نامي": ["ذرة صفراء", "كسب فول صويا 44%", "كسب جلوتين 60%", "مسحوق أسماك 60%", "زيت فول الصويا", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "ليسين نقي", "ميثيونين نقي", "بريمكس تسمين دواجن", "مضاد سموم فطرية", "إنزيم فايتيز"],
        "ناهي": ["ذرة صفراء", "كسب فول صويا 44%", "زيت فول الصويا", "زيت النخيل", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "ليسين نقي", "ميثيونين نقي", "بريمكس تسمين دواجن", "مضاد سموم فطرية", "إنزيم فايتيز"],
        "بياض": ["ذرة صفراء", "كسب فول صويا 46%", "كسب عباد الشمس 36%", "نخالة قمح (ردة)", "زيت فول الصويا", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "ليسين نقي", "ميثيونين نقي", "بريمكس بياض"],
    },
    "سمان": {
        "تسمين": ["ذرة صفراء", "كسب فول صويا 48%", "كسب جلوتين 60%", "مسحوق أسماك 60%", "زيت فول الصويا", "زيت ذرة", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "ليسين نقي", "ميثيونين نقي", "بريمكس تسمين دواجن", "مضاد سموم فطرية", "إنزيم فايتيز"],
        "بياض": ["ذرة صفراء", "كسب فول صويا 46%", "كسب عباد الشمس 36%", "زيت فول الصويا", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "ليسين نقي", "ميثيونين نقي", "بريمكس بياض"],
    },
    "أسماك": {
        "بادئ": ["مسحوق أسماك 72%", "كسب فول صويا 48%", "كسب جلوتين 60%", "ذرة صفراء", "زيت السمك", "زيت فول الصويا", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بريمكس مجترات", "مضاد سموم فطرية"],
        "نمو": ["مسحوق أسماك 60%", "كسب فول صويا 44%", "كسب جلوتين 40%", "ذرة صفراء", "زيت السمك", "زيت فول الصويا", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام"],
        "تسمين": ["مسحوق أسماك 60%", "كسب فول صويا 44%", "كسب جلوتين 40%", "ذرة صفراء", "زيت السمك", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام"],
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# ✅✅✅ التعديل الجديد 3: auto_select_ingredients حسب الدولة ✅✅✅
# ═══════════════════════════════════════════════════════════════════════════

def auto_select_ingredients(animal_choice, production_type, stage_hint="", country="السودان"):
    """اختيار المكونات تلقائياً حسب نوع الحيوان + توفّرها في الدولة"""
    country_avail = get_country_available_ingredients(country)
    animal_key = None
    for key in RECOMMENDED_INGREDIENTS.keys():
        if key in animal_choice:
            animal_key = key
            break
    if not animal_key:
        base = [i for i in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة"].keys() if i in country_avail]
        return base[:5]
    animal_recipes = RECOMMENDED_INGREDIENTS[animal_key]
    type_key = None
    hint = (production_type + " " + stage_hint).lower()
    if "حليب" in hint or "حلابة" in hint or "مرضع" in hint: type_key = "حليب"
    elif "تسمين" in hint or "نمو" in hint or "حمل" in hint: type_key = "تسمين"
    elif "صيانة" in hint or "جاف" in hint: type_key = "صيانة"
    elif "بادي" in hint: type_key = "بادي"
    elif "نامي" in hint: type_key = "نامي"
    elif "ناهي" in hint: type_key = "ناهي"
    elif "بياض" in hint: type_key = "بياض"
    elif "رياضة" in hint: type_key = "رياضة"
    elif "سباق" in hint: type_key = "سباق"

    if type_key and type_key in animal_recipes:
        selected = animal_recipes[type_key]
    elif animal_recipes:
        selected = list(animal_recipes.values())[0]
    else:
        selected = []

    # ✅ فلترة حسب توفّر الدولة + إضافة بدائل عند الحاجة
    filtered = [i for i in selected if i in country_avail]
    filtered = _ensure_protein_source(filtered, animal_choice, country_avail)

    # إذا كان الناتج قليلاً، أضف مواد أساسية متوفرة
    if len(filtered) < 5:
        extras = [i for i in ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "البرسيم الجاف", "الحجر الجيري"] if i in country_avail and i not in filtered]
        filtered.extend(extras)
    return filtered


def _ensure_protein_source(selected, animal_choice, country_avail):
    """يضمن وجود مصدر بروتين بديل عند غياب الصويا"""
    protein_sources = ["كسب فول صويا 44%", "كسب فول صويا 46%", "كسب فول صويا 48%", "أمباز الفول السوداني", "كسب عباد الشمس 36%", "كسب عباد الشمس 32%", "كسب الكانولا", "كسب بذور القطن", "مسحوق أسماك 60%", "مسحوق أسماك 72%", "كسب جلوتين 60%", "كسب جلوتين 40%", "كسب السمسم", "مسحوق اللحم والعظم"]
    has_protein = any(p in selected for p in protein_sources)
    if has_protein: return selected
    # ابحث عن أقرب بديل متوفر
    for p in protein_sources:
        if p in country_avail:
            selected.append(p)
            return selected
    return selected


# ═══════════════════════════════════════════════════════════════════════════
# ✅✅✅ التعديل الجديد 4: محرك التركيب الآلي 100% (SLSQP) ✅✅✅
# ═══════════════════════════════════════════════════════════════════════════

def auto_formulate_100(available_ingredients, prices, custom_standard, standard_key, country="السودان"):
    """
    محرك تركيب آلي بدقة عالية جداً — يستهدف مطابقة ≥ 100% على العناصر الرئيسية.
    يستخدم SLSQP لتقليل مجموع الأخطاء النسبية الموزونة (Least Squares weighted).
    - التركيب الآلي: يمكن أن يصل إلى 100%
    - التركيب اليدوي: 75% - 99%
    """
    # ✅ فلترة المواد المتوفرة في الدولة
    country_avail = get_country_available_ingredients(country)
    available_ingredients = [i for i in available_ingredients if i in country_avail]

    # بناء بيانات المكونات
    ing_data = {}
    for ing in available_ingredients:
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                ing_data[ing] = cat[ing]
                break
    valid = [i for i in available_ingredients if i in ing_data]
    if len(valid) < 3:
        return {"success": False, "message": f"عدد المكونات المتوفرة في {country} أقل من 3"}

    n = len(valid)
    c = np.array([prices.get(i, 300.0) for i in valid])

    # مصفوفة القيم الغذائية
    nutr_keys = ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]
    M = {}
    for k in nutr_keys:
        M[k] = np.array([ing_data[i].get(k, 0) for i in valid])
    # DP = CP × DC
    M["DP"] = np.array([ing_data[i].get("CP", 0) * ing_data[i].get("DC", 0) for i in valid])

    targets = {k: custom_standard.get(k, 0) for k in ["DP", "CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]}

    # قيود الحدود لكل مكون
    oil_set = set(get_oil_ingredients().keys())
    oil_std = get_oil_standard(standard_key)
    oil_max = oil_std["max"]
    bounds = []
    for i in valid:
        if i in oil_set: bounds.append((0.0, oil_max * 0.5))
        elif "يوريا" in i: bounds.append((0.0, 1.0))
        elif "مولاس" in i: bounds.append((0.0, 10.0))
        elif "ملح الطعام" in i: bounds.append((0.20, 0.70))
        elif "بيكربونات" in i: bounds.append((0.0, 1.5))
        elif "مضاد سموم" in i: bounds.append((0.05, 0.25))
        elif "بريمكس" in i: bounds.append((0.15, 0.5))
        elif "إنزيم" in i: bounds.append((0.02, 0.10))
        elif "الحجر الجيري" in i: bounds.append((0.0, 12.0))
        elif "فوسفات" in i: bounds.append((0.0, 3.0))
        elif "سرسة" in i or "قش" in i: bounds.append((0.0, 12.0))
        elif "تبن" in i: bounds.append((0.0, 25.0))
        else: bounds.append((0.0, 100.0))

    # أوزان العناصر (الأهم = أعلى وزن)
    W = {"DP": 12.0, "CP": 6.0, "SE": 6.0, "NDF": 3.0, "ADF": 2.0, "EE": 2.0, "Ca": 2.5, "P": 2.5, "ASH": 0.5}

    # مقياس اللوغاريتم لتطبيع الانحرافات
    def objective(x):
        err = 0.0
        for k in targets:
            if targets[k] > 0 and k in M:
                actual = float(np.dot(M[k], x)) / 100.0
                rel = (actual - targets[k]) / targets[k]
                err += W.get(k, 1.0) * rel * rel
        # إضافة بسيطة لعامل التكلفة (1%)
        cost_norm = float(np.dot(c, x)) / 100.0
        err += 0.0005 * (cost_norm / 1000.0)
        return err

    # قيود: sum(x) = 100
    cons = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 100.0}]

    # نقطة انطلاق: حبوب + بروتين + أملاح
    x0 = np.zeros(n)
    for idx, i in enumerate(valid):
        if i in oil_set: x0[idx] = oil_std["optimal"] * 0.3
        elif "ملح الطعام" in i: x0[idx] = 0.4
        elif "الحجر الجيري" in i: x0[idx] = 1.5
        elif "فوسفات" in i: x0[idx] = 1.0
        elif "بريمكس" in i: x0[idx] = 0.25
        elif "مضاد سموم" in i: x0[idx] = 0.15
        elif "بيكربونات" in i: x0[idx] = 0.6
        elif "كسب فول صويا" in i or "أمباز" in i or "عباد الشمس" in i or "الكانولا" in i or "أسماك" in i: x0[idx] = 15.0
        elif "ذرة" in i or "شعير" in i: x0[idx] = 25.0
        elif "نخالة" in i: x0[idx] = 10.0
        elif "البرسيم" in i or "تبن" in i: x0[idx] = 15.0
        else: x0[idx] = 2.0
    # إعادة التوازن
    if x0.sum() > 0: x0 = x0 * (100.0 / x0.sum())
    x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])

    # جولات متعددة بمعاملات وزن مختلفة للوصول إلى 100%
    best = None
    best_score = float('inf')

    weight_configs = [
        W,  # الجولة الافتراضية
        {"DP": 20.0, "CP": 10.0, "SE": 10.0, "NDF": 4.0, "ADF": 3.0, "EE": 3.0, "Ca": 4.0, "P": 4.0, "ASH": 1.0},  # تركيز عالٍ
        {"DP": 15.0, "CP": 8.0, "SE": 8.0, "NDF": 2.0, "ADF": 1.0, "EE": 2.0, "Ca": 3.0, "P": 3.0, "ASH": 0.5},  # تركيز على البروتين والطاقة
    ]

    for wi, Wcur in enumerate(weight_configs):
        def obj_cur(x, _W=Wcur):
            err = 0.0
            for k in targets:
                if targets[k] > 0 and k in M:
                    actual = float(np.dot(M[k], x)) / 100.0
                    rel = (actual - targets[k]) / targets[k]
                    err += _W.get(k, 1.0) * rel * rel
            return err

        for method in ['SLSQP', 'trust-constr']:
            try:
                if method == 'trust-constr':
                    res = minimize(obj_cur, x0, method=method, bounds=bounds, constraints=cons, options={'maxiter': 2000, 'xtol': 1e-9, 'gtol': 1e-9})
                else:
                    res = minimize(obj_cur, x0, method=method, bounds=bounds, constraints=cons, options={'maxiter': 2000, 'ftol': 1e-12})
                if not res.success:
                    # جرّب نقطة انطلاق أخرى
                    x0_alt = np.array([np.mean([b[0], b[1]]) for b in bounds])
                    if x0_alt.sum() > 0: x0_alt = x0_alt * (100.0 / x0_alt.sum())
                    res = minimize(obj_cur, x0_alt, method=method, bounds=bounds, constraints=cons, options={'maxiter': 2000})
                if res.success or hasattr(res, 'x'):
                    formula = {valid[i]: float(res.x[i]) for i in range(n) if res.x[i] > 0.001}
                    # تصحيح المجموع
                    total_pct = sum(formula.values())
                    if total_pct > 0:
                        formula = {k: v * (100.0 / total_pct) for k, v in formula.items()}
                    actual = compute_formula_nutrients(formula)
                    # حساب درجة المطابقة
                    rel_errors = []
                    for k in targets:
                        if targets[k] > 0:
                            rel_errors.append(abs(actual.get(k, 0) - targets[k]) / targets[k])
                    avg_err = sum(rel_errors) / len(rel_errors) if rel_errors else 1.0
                    # نبحث عن أفضل حل
                    if avg_err < best_score:
                        best_score = avg_err
                        best = {"formula": formula, "actual": actual, "avg_rel_error": avg_err, "cost": sum((formula[i]/100.0)*prices.get(i, 300.0) for i in formula)}
                        if avg_err <= 0.005:  # مطابقة ~ 99.5%
                            break
            except Exception:
                continue
        if best and best.get("avg_rel_error", 1) <= 0.005:
            break
        # استخدم أفضل حل كنقطة انطلاق للجولة التالية
        if best:
            x0 = np.array([best["formula"].get(i, 0.0) for i in valid])
            if x0.sum() > 0: x0 = x0 * (100.0 / x0.sum())

    if not best:
        return {"success": False, "message": "تعذر إيجاد حل مناسب"}

    # حساب معدل المطابقة النهائي (كنسبة مئوية)
    formula = best["formula"]
    actual = best["actual"]
    match_scores = []
    for k in targets:
        if targets[k] > 0:
            rel_err_pct = abs(actual.get(k, 0) - targets[k]) / targets[k] * 100
            ev = evaluate_difference(rel_err_pct if actual.get(k, 0) >= targets[k] else -rel_err_pct)
            match_scores.append(ev["score"])
    overall_match = sum(match_scores) / len(match_scores) if match_scores else 0

    # حساب قيم الخطأ
    result = {
        "success": True,
        "formula": formula,
        "cost": best["cost"],
        "actual_nutrients": actual,
        "targets": targets,
        "overall_match_pct": overall_match,
        "avg_rel_error_pct": best["avg_rel_error"] * 100,
        "dp_error": abs(actual["DP"] - targets["DP"]),
        "se_error": abs(actual["SE"] - targets["SE"]),
        "ndf_error": abs(actual["NDF"] - targets["NDF"]),
        "adf_error": abs(actual["ADF"] - targets["ADF"]),
        "ca_error": abs(actual.get("Ca", 0) - targets["Ca"]),
        "p_error": abs(actual.get("P", 0) - targets["P"]),
        "total_oil": compute_total_oil_percentage(formula),
        "oil_std": oil_std,
        "iterations": 1,
        "log": [f"SLSQP match: {overall_match:.1f}%"],
        "perfect_match": overall_match >= 99.5,
    }
    return result


# احتفظ بالدالة القديمة كـ fallback (لا تُستخدم عند نجاح الجديدة)
def auto_formulate_smart(available_ingredients, prices, custom_standard, standard_key, tolerance=0.3, max_iterations=50, country="السودان"):
    """احتياطي: في حال عدم توفر scipy، استخدم التنسيق القديم"""
    if SCIPY_AVAILABLE:
        try:
            return auto_formulate_100(available_ingredients, prices, custom_standard, standard_key, country=country)
        except Exception:
            pass
    return {"success": False, "message": "محرك التركيب يحتاج scipy.optimize"}


def auto_add_salts_and_minerals(animal_type, requirement=None, country="السودان"):
    salt = {}
    avail = get_country_available_ingredients(country)
    if animal_type in ["أغنام", "ماعز", "أبقار", "إبل"] and "بيكربونات الصوديوم" in avail:
        salt["بيكربونات الصوديوم"] = 0.75
    if "مضاد سموم فطرية" in avail: salt["مضاد سموم فطرية"] = 0.20
    if "ملح الطعام" in avail: salt["ملح الطعام"] = 0.50
    if animal_type in ["دواجن", "سمان"]:
        if "الحجر الجيري" in avail: salt["الحجر الجيري"] = 8.0 if (requirement and requirement.Ca > 2.0) else 1.5
        if "فوسفات ثنائي الكالسيوم" in avail: salt["فوسفات ثنائي الكالسيوم"] = 1.5
        if "بريمكس تسمين دواجن" in avail: salt["بريمكس تسمين دواجن"] = 0.30
    elif animal_type == "أسماك":
        if "الحجر الجيري" in avail: salt["الحجر الجيري"] = 1.0
        if "فوسفات ثنائي الكالسيوم" in avail: salt["فوسفات ثنائي الكالسيوم"] = 1.5
    elif animal_type == "خيول":
        if "الحجر الجيري" in avail: salt["الحجر الجيري"] = 1.5
        if "فوسفات ثنائي الكالسيوم" in avail: salt["فوسفات ثنائي الكالسيوم"] = 1.5
        if "بريمكس خيول" in avail: salt["بريمكس خيول"] = 0.30
    elif animal_type == "إبل":
        if "الحجر الجيري" in avail: salt["الحجر الجيري"] = 2.0
        if "فوسفات ثنائي الكالسيوم" in avail: salt["فوسفات ثنائي الكالسيوم"] = 1.5
        if "بريمكس إبل" in avail: salt["بريمكس إبل"] = 0.30
    else:
        if "الحجر الجيري" in avail: salt["الحجر الجيري"] = 2.0
        if "فوسفات ثنائي الكالسيوم" in avail: salt["فوسفات ثنائي الكالسيوم"] = 1.5
        if "بريمكس مجترات" in avail: salt["بريمكس مجترات"] = 0.30
    return salt


def auto_run_full_analysis(animal_choice, production_type, stage_hint, standard_key, prices, country="السودان", custom_ingredients=None):
    if custom_ingredients: selected = custom_ingredients
    else: selected = auto_select_ingredients(animal_choice, production_type, stage_hint, country=country)
    requirement = None
    if "أبقار" in animal_choice: requirement = get_cattle_requirements(production_type)
    elif "أغنام" in animal_choice: requirement = get_sheep_requirements(production_type)
    elif "ماعز" in animal_choice: requirement = get_goat_requirements(production_type)
    elif "إبل" in animal_choice: requirement = get_camel_requirements(production_type)
    elif "خيول" in animal_choice: requirement = get_horse_requirements(production_type)
    elif "دواجن" in animal_choice: requirement = get_poultry_requirements(production_type)
    elif "سمان" in animal_choice: requirement = get_quail_requirements(production_type)
    elif "أسماك" in animal_choice: requirement = get_fish_requirements("البلطي النيلي", production_type)
    if not requirement:
        return {"success": False, "message": "تعذر تحديد المتطلبات"}
    auto_salts = auto_add_salts_and_minerals(animal_choice, requirement, country=country)
    for salt_name in auto_salts:
        if salt_name not in selected: selected.append(salt_name)
    custom_std = requirement_to_standard(requirement)
    result = auto_formulate_100(selected, prices, custom_std, standard_key=standard_key, country=country)
    return result


# ═══════════════════════════════════════════════════════════════════════════
# بدائل الحليب (كما الأصل)
# ═══════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24.0, "Fat": 24.0, "Lactose": 45.0, "Lysine": 2.1, "Ca": 0.75, "P": 0.70, "notes": "عمر 1-6 أسابيع، مادة جافة 12-15%"},
    "حملان (Lambs)": {"CP": 24.0, "Fat": 24.0, "Lactose": 40.0, "Lysine": 2.1, "Ca": 0.80, "P": 0.70, "notes": "≥ 24% دهن"},
    "جديان (Goat Kids)": {"CP": 24.0, "Fat": 24.0, "Lactose": 42.0, "Lysine": 2.1, "Ca": 0.80, "P": 0.70, "notes": "بديل الجديان"},
    "إبل (Camel Calves)": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "Lysine": 2.3, "Ca": 0.85, "P": 0.75, "notes": "بروتين ودهن أعلى"},
    "أمهار (Foals)": {"CP": 22.0, "Fat": 20.0, "Lactose": 45.0, "Lysine": 1.9, "Ca": 0.90, "P": 0.80, "notes": "توازن للخيول"},
}

MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34.0, "Fat": 1.0, "Lactose": 52.0, "price": 3200},
    "حليب مجفف كامل الدسم": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "price": 3800},
    "شرش حليب مجفف": {"CP": 12.0, "Fat": 1.5, "Lactose": 75.0, "price": 1800},
    "بروتين شرش WPC 80%": {"CP": 80.0, "Fat": 5.0, "Lactose": 8.0, "price": 8500},
    "كازين": {"CP": 85.0, "Fat": 2.0, "Lactose": 2.0, "price": 9000},
    "مركز بروتين صويا": {"CP": 66.0, "Fat": 1.0, "Lactose": 0.0, "price": 2800},
    "دقيق الصويا": {"CP": 38.0, "Fat": 20.0, "Lactose": 0.0, "price": 1500},
    "زيت جوز الهند": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "price": 2200},
    "زيت النخيل": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "price": 1200},
    "دهن حيواني": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "price": 1000},
    "مالتودكسترين": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 900},
    "لاكتوز نقي": {"CP": 0.0, "Fat": 0.0, "Lactose": 100.0, "price": 1400},
    "ليسين L-Lysine": {"CP": 94.0, "Fat": 0.0, "Lactose": 0.0, "price": 4200},
    "ميثيونين": {"CP": 58.0, "Fat": 0.0, "Lactose": 0.0, "price": 5800},
    "بريمكس فيتامينات": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 6500},
    "كالسيوم كربونات": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 200},
    "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 1100},
    "ملح طعام": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 150},
}

def formulate_milk_replacer(animal_type, target_volume_kg=100.0, selected_ingredients=None):
    standard = MILK_REPLACER_STANDARDS.get(animal_type)
    if not standard: return {"success": False, "message": "غير مدعوم"}
    valid = [i for i in (selected_ingredients or list(MILK_REPLACER_INGREDIENTS.keys())) if i in MILK_REPLACER_INGREDIENTS]
    if len(valid) < 3: return {"success": False, "message": "اختر 3 مكونات على الأقل"}
    n = len(valid)
    c = [MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]
    bounds = [(0.0, 100.0) for _ in range(n)]
    A_eq = [[1.0]*n, [MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid], [MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid]]
    b_eq = [100.0, standard["CP"]*100, standard["Fat"]*100]
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if not res.success: return {"success": False, "message": "تعذر التركيب"}
    formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
    actual = {"CP": 0, "Fat": 0, "Lactose": 0}
    for ing, pct in formula.items():
        d = MILK_REPLACER_INGREDIENTS[ing]
        actual["CP"] += pct/100.0 * d["CP"]
        actual["Fat"] += pct/100.0 * d["Fat"]
        actual["Lactose"] += pct/100.0 * d["Lactose"]
    return {"success": True, "formula": formula, "cost_per_100kg": res.fun/100.0, "cost_per_kg": res.fun/10000.0, "standard": standard, "actual": actual, "animal": animal_type}


# ═══════════════════════════════════════════════════════════════════════════
# OCR المختبر الذكي
# ═══════════════════════════════════════════════════════════════════════════

def match_ingredient_name(text):
    if not text: return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower(): return name
    kw = {"ذرة": "ذرة صفراء", "corn": "ذرة صفراء", "صويا": "كسب فول صويا 44%", "شعير": "شعير مطحون", "قمح": "قمح محلي", "سورجم": "سورجم (فتريتة)", "نخالة": "نخالة قمح (ردة)", "فول سوداني": "أمباز الفول السوداني", "قطن": "كسب بذور القطن", "عباد": "كسب عباد الشمس 36%", "سمسم": "كسب السمسم", "جلوتين": "كسب جلوتين 60%", "سمك": "مسحوق أسماك 60%", "لحم": "مسحوق اللحم والعظم", "دم": "مسحوق الدم", "ليسين": "ليسين نقي", "ميثيونين": "ميثيونين نقي", "ملح": "ملح الطعام", "حجر": "الحجر الجيري", "فوسفات": "فوسفات ثنائي الكالسيوم", "بيكربونات": "بيكربونات الصوديوم", "مولاس": "مولاس قصب السكر", "برسيم": "البرسيم الجاف", "تبن": "تبن قمح", "يوريا": "يوريا علفية", "زيت": "زيت فول الصويا"}
    for k, m in kw.items():
        if k in tl: return m
    return None

def extract_ingredients_from_image(image_bytes):
    if not OCR_AVAILABLE: return {"success": False, "message": "pytesseract غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return {"success": False, "message": "تعذر قراءة الصورة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        t1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        _, t2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        texts = []
        for t in [t1, t2, gray]:
            try:
                txt = pytesseract.image_to_string(t, lang='ara+eng', config=r'--oem 3 --psm 6')
                if txt.strip(): texts.append(txt)
            except Exception: continue
        if not texts: return {"success": False, "message": "لم يتم استخراج نص"}
        full = "\n".join(texts)
        ingredients = {}
        for line in full.split('\n'):
            line = line.strip()
            if len(line) < 3: continue
            for pat in [r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)[\s:\-=]+(\d+\.?\d*)\s*%', r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)\s+(\d+\.?\d*)\s*%']:
                m = re.search(pat, line)
                if m:
                    name, val = m.group(1).strip(), float(m.group(2))
                    if 0.1 < val <= 100 and len(name) > 2:
                        matched = match_ingredient_name(name)
                        if matched:
                            ingredients[matched] = val
                            break
        return {"success": True, "ingredients": ingredients, "raw_text": full, "count": len(ingredients)}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}


# ═══════════════════════════════════════════════════════════════════════════
# الرسوم البيانية
# ═══════════════════════════════════════════════════════════════════════════

def create_colorful_bar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        nutrients = [n for n in ["CP","DP","SE","NDF","ADF","EE","ASH"] if n in standard]
        if not nutrients: return None
        std_vals = [standard[n] for n in nutrients]
        act_vals = [actual.get(n, 0) for n in nutrients]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nutrients)); width = 0.35
        bars1 = ax.bar(x - width/2, std_vals, width, label='المعيار', color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        bars2 = ax.bar(x + width/2, act_vals, width, label='المحسوب', color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        for bar in bars1:
            h = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, h, f'{h:.1f}', ha='center', va='bottom', fontsize=9, color='#0d47a1', fontweight='bold')
        for bar in bars2:
            h = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, h, f'{h:.1f}', ha='center', va='bottom', fontsize=9, color='#1b5e20', fontweight='bold')
        ax.set_xlabel('العنصر'); ax.set_ylabel('القيمة')
        ax.set_title('مقارنة العناصر الغذائية', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nutrients, fontsize=10)
        ax.legend(loc='upper right'); ax.grid(axis='y', alpha=0.3, linestyle='--'); ax.set_facecolor('#fafafa')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_colorful_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2: return None
    try:
        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b','#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41','#c62828','#6a1b9a','#283593','#0277bd','#00695c','#004d40','#3e2723','#bf360c','#e65100','#ff6f00']
        names = list(formula.keys()); vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        wedges, texts, autotexts = ax.pie(vals, autopct='%1.1f%%', colors=colors[:len(names)], startangle=90, pctdistance=0.75, wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts: t.set_color('white'); t.set_fontweight('bold'); t.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9, title="المكونات")
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_radar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        nutrients = [n for n in ["CP","DP","SE","NDF","ADF","EE","Ca","P"] if n in standard and standard[n] > 0]
        if len(nutrients) < 3: return None
        std_norm = [100.0 for _ in nutrients]
        act_norm = [(actual.get(n, 0)/standard[n])*100 for n in nutrients]
        angles = np.linspace(0, 2*np.pi, len(nutrients), endpoint=False).tolist()
        std_norm += std_norm[:1]; act_norm += act_norm[:1]; angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2', label='المعيار')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047', label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(nutrients, fontsize=10)
        ax.set_ylim(0, max(max(std_norm), max(act_norm))*1.2)
        ax.set_title('المقارنة %', fontsize=12, fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True, alpha=0.3); ax.set_facecolor('#fafafa')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors_g = ['#c62828','#ef6c00','#f9a825','#7cb342','#43a047','#1b5e20']
        for i, c in enumerate(colors_g):
            theta1 = 180-(i*30); theta2 = 180-((i+1)*30)
            ax.add_patch(Wedge((0,0), 1, theta2, theta1, width=0.3, facecolor=c, edgecolor='white', linewidth=2))
        angle = 180 - (score/100)*180; rad = np.radians(angle)
        ax.plot([0, 0.85*np.cos(rad)], [0, 0.85*np.sin(rad)], color='#1a1a1a', linewidth=3, zorder=10)
        ax.add_patch(Circle((0,0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20, fontweight='bold', color='#1b5e20')
        ax.text(0, -0.5, 'التقييم', ha='center', fontsize=11, color='#666')
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2); ax.axis('off')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None


# ═══════════════════════════════════════════════════════════════════════════
# PDF Generator (كما الأصل — مختصر هنا)
# ═══════════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name; self.font_bold = font_mgr.font_bold
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp): self.logo_path = lp; break
    def _ar(self, text):
        if text is None: return ""
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped, base_dir='R')
        except Exception: return str(text)
    def _draw_page(self, canvas_obj, doc):
        canvas_obj.saveState(); w, h = doc.pagesize
        canvas_obj.setFillColor(HexColor('#e8f5e9')); canvas_obj.setFont(self.font_name, 60)
        try: canvas_obj.setFillAlpha(0.07)
        except Exception: pass
        canvas_obj.saveState(); canvas_obj.translate(w/2, h/2); canvas_obj.rotate(45)
        canvas_obj.drawCentredString(0, 0, self._ar("تاور نولجي")); canvas_obj.restoreState()
        try: canvas_obj.setFillAlpha(1)
        except Exception: pass
        canvas_obj.setFillColor(HexColor('#1b5e20')); canvas_obj.rect(0, h-90, w, 90, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37')); canvas_obj.rect(0, h-95, w, 5, fill=1, stroke=0)
        try:
            if self.logo_path: canvas_obj.drawImage(self.logo_path, 30, h-78, width=60, height=60, preserveAspectRatio=True, anchor='sw', mask='auto')
        except Exception: pass
        canvas_obj.setFillColor(white); canvas_obj.setFont(self.font_name, 22)
        canvas_obj.drawCentredString(w/2, h-38, self._ar("تاور نولجي  Tawor Nology"))
        canvas_obj.setFont(self.font_name, 12); canvas_obj.setFillColor(HexColor('#e8f5e9'))
        canvas_obj.drawCentredString(w/2, h-58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
        canvas_obj.setFont(self.font_name, 10); canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.drawCentredString(w/2, h-76, self._ar(f"إشراف: {SUPERVISOR}"))
        canvas_obj.setFillColor(HexColor('#1b5e20')); canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37')); canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#ffeb3b')); canvas_obj.setFont(self.font_name, 10)
        canvas_obj.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
        canvas_obj.setFillColor(HexColor('#c8e6c9')); canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawCentredString(w/2, 52, self._ar("اللهم اجعل قبرهما روضة من رياض الجنة"))
        canvas_obj.setFillColor(HexColor('#1b5e20')); canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
        canvas_obj.setFillColor(white); canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawCentredString(w/2, 27, self._ar("تاور نولجي Tawor Nology © 2026"))
        canvas_obj.setFont(self.font_name, 7)
        canvas_obj.drawCentredString(w/2, 12, self._ar(f"صفحة {canvas_obj.getPageNumber()}"))
        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=1); qr.add_data(PLATFORM_URL); qr.make(fit=True)
            qi = qr.make_image(fill_color="#1b5e20", back_color="white")
            buf = io.BytesIO(); qi.save(buf, format="PNG"); buf.seek(0)
            canvas_obj.drawImage(RLImage(buf), w/2-20, 46, width=40, height=40)
        except Exception: pass
        sx, sy = w - 105, 145
        canvas_obj.setStrokeColor(HexColor('#c62828')); canvas_obj.setLineWidth(3.0); canvas_obj.circle(sx, sy, 70, stroke=1, fill=0)
        canvas_obj.setLineWidth(1.5); canvas_obj.circle(sx, sy, 62, stroke=1, fill=0)
        canvas_obj.setFillColor(HexColor('#c62828')); canvas_obj.setFont(self.font_name, 9)
        canvas_obj.drawCentredString(sx, sy+40, self._ar("تاور نولجي"))
        canvas_obj.drawCentredString(sx, sy+28, self._ar("Tawor Nology"))
        canvas_obj.setFont(self.font_name, 7.5)
        canvas_obj.drawCentredString(sx, sy+10, self._ar("م. عبدالقادر"))
        canvas_obj.drawCentredString(sx, sy-1, self._ar("إسماعيل تاور"))
        canvas_obj.setFont(self.font_name, 6)
        canvas_obj.drawCentredString(sx, sy-17, self._ar("اختصاصي تغذية الحيوان"))
        canvas_obj.drawCentredString(sx, sy-30, self._ar("معتمد رسمياً"))
        canvas_obj.drawCentredString(sx, sy-42, self._ar("© 2026"))
        canvas_obj.restoreState()
    def _comparison_table(self, standard, calculated):
        labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP", "SE": "معادل النشاء SE", "NDF": "ألياف NDF", "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH", "Ca": "كالسيوم Ca", "P": "فسفور P"}
        header = [self._ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "الفرق %", "التقييم"]]
        data = [header]
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),9),('GRID',(0,0),(-1,-1),1,HexColor('#9e9e9e')),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7)]
        row = 1
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in standard: continue
            sv = standard[k]; cv = calculated.get(k, 0.0)
            diff = cv - sv; pct = (diff/sv*100) if sv else 0
            ev = evaluate_difference(pct)
            unit = "%" if k in ("CP","DP","NDF","ADF","EE","ASH","Ca","P") else ""
            data.append([self._ar(labels.get(k,k)), f"{sv:.2f}{unit}", f"{cv:.2f}{unit}", f"{diff:+.3f}", f"{pct:+.2f}%", self._ar(ev["label"])])
            cmds.append(('BACKGROUND',(0,row),(-1,row),HexColor(ev["bg"])))
            cmds.append(('TEXTCOLOR',(5,row),(5,row),HexColor(ev["color"])))
            row += 1
        t = Table(data, colWidths=[100,70,70,70,70,105]); t.setStyle(TableStyle(cmds)); return t
    def generate_report(self, formula, requirement, animal_type, breed, cost, city, local_cost, local_sym, requester_name="", protein_basis="DP", standard_key="", include_charts=True, country=""):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle('s', fontName=self.font_name, fontSize=size, alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
        story.append(P("تقرير فني رسمي — تركيب علفة", size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6)); story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37'))); story.append(Spacer(1, 12))
        client_data = [[self._ar("👤 طالب الخدمة:"), self._ar(requester_name or "........")], [self._ar("🌍 الدولة:"), self._ar(country or "—")], [self._ar("📍 المدينة:"), self._ar(city)], [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")], [self._ar("🧬 أساس الحساب:"), self._ar("DP" if protein_basis=="DP" else "CP")], [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d | %H:%M')]]
        ct = Table(client_data, colWidths=[150, 340]); ct.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),('BACKGROUND',(1,0),(1,-1),HexColor('#fafafa')),('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#c8e6c9')),('ALIGN',(0,0),(-1,-1),'RIGHT'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
        story.append(ct); story.append(Spacer(1, 15))
        standard_vals = requirement_to_standard(requirement); calculated_vals = compute_formula_nutrients(formula)
        scores = []
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in standard_vals: continue
            sv = standard_vals[k]; cv = calculated_vals.get(k, 0.0); pct = ((cv-sv)/sv*100) if sv else 0
            scores.append({"score": evaluate_difference(pct)["score"]})
        overall = get_overall_rating(scores)
        story.append(P("📊 جدول مقارنة العناصر", size=14, color='#1b5e20')); story.append(Spacer(1, 8))
        story.append(self._comparison_table(standard_vals, calculated_vals)); story.append(Spacer(1, 12))
        summary_data = [[self._ar("التقييم"), self._ar("مطابقة"), self._ar("المتوسط")], [self._ar(overall["label"]), f"{sum(1 for s in scores if s['score'] >= 85)}/{len(scores)}", f"{overall['score']:.0f}%"]]
        st_tbl = Table(summary_data, colWidths=[160,165,165]); st_tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1565c0')),('TEXTCOLOR',(0,0),(-1,0),white),('BACKGROUND',(0,1),(-1,-1),HexColor('#e3f2fd')),('GRID',(0,0),(-1,-1),1,HexColor('#1976d2')),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        story.append(st_tbl); story.append(Spacer(1, 15))
        if include_charts:
            story.append(P("📈 الرسوم البيانية", size=14, color='#1b5e20')); story.append(Spacer(1, 10))
            c1 = create_colorful_bar_chart(standard_vals, calculated_vals)
            if c1: story.append(RLImage(c1, width=450, height=250)); story.append(Spacer(1, 12))
            c2 = create_colorful_pie_chart(formula); c3 = create_radar_chart(standard_vals, calculated_vals)
            if c2 and c3:
                rt = Table([[RLImage(c2, width=210, height=200), RLImage(c3, width=210, height=200)]], colWidths=[230,230]); rt.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')])); story.append(rt); story.append(Spacer(1, 12))
            gauge = create_gauge_chart(overall["score"])
            if gauge: story.append(P("🎯 التقييم", size=12, align=TA_CENTER, color='#1b5e20')); story.append(RLImage(gauge, width=200, height=200)); story.append(Spacer(1, 12))
        story.append(PageBreak())
        story.append(P("💰 التكاليف", size=14, color='#1b5e20')); story.append(Spacer(1, 8))
        cost_data = [[self._ar("البند"), self._ar("القيمة")], [self._ar("التكلفة للطن ($)"), f"${cost:.2f}"], [self._ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"], [self._ar("البروتين المستهدف"), f"{requirement.DP if protein_basis=='DP' else requirement.CP:.2f}%"]]
        tc = Table(cost_data, colWidths=[280,210]); tc.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),('BACKGROUND',(0,1),(-1,-1),HexColor('#f5f5f5')),('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32')),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        story.append(tc); story.append(Spacer(1, 18))
        if formula:
            story.append(P("🌾 المكونات للطن", size=14, color='#1b5e20')); story.append(Spacer(1, 8))
            ing_data = [[self._ar("المكون"), self._ar("النسبة %"), self._ar("كجم/طن")]]
            for ing, pct in formula.items(): ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
            ti = Table(ing_data, colWidths=[270,110,110]); ti.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd')),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#ffffff'),HexColor('#f5f5f5')]),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.append(ti); story.append(Spacer(1, 25))
        sign = [[self._ar("توقيع الطالب"), self._ar("توقيع المختص")], [self._ar("............"), self._ar(SUPERVISOR)], [self._ar("التاريخ: ..../..../...."), self._ar(SUPERVISOR_TITLE)]]
        ts = Table(sign, colWidths=[245,245]); ts.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('BOX',(0,0),(-1,-1),1,HexColor('#bdbdbd')),('INNERGRID',(0,0),(-1,-1),0.5,HexColor('#e0e0e0')),('BACKGROUND',(0,0),(-1,0),HexColor('#e8f5e9'))]))
        story.append(ts)
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0); return buffer.getvalue()
    def generate_lab_report(self, analysis, requester_name="", sample_id="", notes=""):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle('s', fontName=self.font_name, fontSize=size, alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
        story.append(P("تقرير تحليل مختبري", size=20, align=TA_CENTER, color='#1565c0'))
        story.append(Spacer(1, 6)); story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37'))); story.append(Spacer(1, 12))
        sample_id_final = sample_id or f"LAB-{datetime.now():%Y%m%d-%H%M}"
        info = [[self._ar("🔬 رقم العينة:"), self._ar(sample_id_final)], [self._ar("👤 الطالب:"), self._ar(requester_name or "........")], [self._ar("🐾 الحيوان:"), self._ar(analysis['animal'])], [self._ar("📋 الحالة:"), self._ar(analysis['requirement'].name_ar)], [self._ar("⚖️ الوزن:"), f"{analysis['total_weight']:.2f} كجم"], [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')]]
        it = Table(info, colWidths=[160,330]); it.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),HexColor('#e3f2fd')),('BACKGROUND',(1,0),(1,-1),HexColor('#fafafa')),('BOX',(0,0),(-1,-1),1.5,HexColor('#1976d2')),('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#bbdefb')),('ALIGN',(0,0),(-1,-1),'RIGHT'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        story.append(it); story.append(Spacer(1, 15))
        story.append(P("📊 التحليل التفصيلي", size=14, color='#1b5e20')); story.append(Spacer(1, 8))
        header = [self._ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "الفرق %", "الحالة"]]
        data = [header]
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#1565c0')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),9),('GRID',(0,0),(-1,-1),1,HexColor('#9e9e9e')),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)]
        for i, row in enumerate(analysis['compare_rows'], 1):
            ev = evaluate_difference(row['_pct'])
            data.append([self._ar(row['العنصر']), row['المعيار'], row['المحسوب'], row['الفرق'], row['الفرق %'], self._ar(ev['label'])])
            cmds.append(('BACKGROUND',(0,i),(-1,i),HexColor(ev['bg']))); cmds.append(('TEXTCOLOR',(5,i),(5,i),HexColor(ev['color'])))
        t = Table(data, colWidths=[95,65,70,65,70,105]); t.setStyle(TableStyle(cmds)); story.append(t); story.append(Spacer(1, 15))
        overall = analysis['overall']
        ov = [[self._ar("🎯 التقييم"), self._ar(overall['label'])], [self._ar("النسبة"), f"{overall['score']:.0f}%"]]
        ovt = Table(ov, colWidths=[240,250]); ovt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),('BACKGROUND',(0,1),(-1,-1),HexColor('#e8f5e9')),('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32')),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
        story.append(ovt); story.append(Spacer(1, 15))
        story.append(PageBreak())
        story.append(P("💡 التوصيات", size=14, color='#1565c0')); story.append(Spacer(1, 8))
        recs = generate_recommendations(analysis)
        for i, rec in enumerate(recs, 1): story.append(P(f"{i}. {rec}", size=11))
        story.append(Spacer(1, 20))
        sign = [[self._ar("توقيع الطالب"), self._ar("توقيع المختص")], [self._ar(".........."), self._ar(SUPERVISOR)], [self._ar("التاريخ: ..../..../...."), self._ar(SUPERVISOR_TITLE)]]
        ts = Table(sign, colWidths=[245,245]); ts.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('BOX',(0,0),(-1,-1),1,HexColor('#bdbdbd')),('INNERGRID',(0,0),(-1,-1),0.5,HexColor('#e0e0e0')),('BACKGROUND',(0,0),(-1,0),HexColor('#e3f2fd'))]))
        story.append(ts)
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0); return buffer.getvalue()

pdf_gen = PDFGenerator()


# ═══════════════════════════════════════════════════════════════════════════
# Excel Export
# ═══════════════════════════════════════════════════════════════════════════

def export_comparison_to_excel(standard, calculated, requester_name="", animal="", stage="", formula=None, standard_key=""):
    if not OPENPYXL_AVAILABLE: return b""
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "مقارنة"; ws.sheet_view.rightToLeft = True
    hf = Font(name='Arial', size=12, bold=True, color='FFFFFF'); hfill = PatternFill('solid', fgColor='1B5E20')
    tf = Font(name='Arial', size=14, bold=True, color='1B5E20'); ct = Alignment(horizontal='center', vertical='center', wrap_text=True); rt = Alignment(horizontal='right', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E'); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws.merge_cells('A1:F1'); ws['A1'] = APP_NAME; ws['A1'].font = tf; ws['A1'].alignment = ct
    ws.merge_cells('A2:F2'); ws['A2'] = f"🤲 {DUA_SHORT} 🤲"; ws['A2'].font = Font(name='Arial', size=10, bold=True, color='C62828'); ws['A2'].alignment = ct
    ws['A4'] = "طالب:"; ws['A4'].font = Font(bold=True); ws['A4'].alignment = rt
    ws.merge_cells('B4:D4'); ws['B4'] = requester_name; ws['E4'] = "التاريخ:"; ws['E4'].font = Font(bold=True); ws['F4'] = datetime.now().strftime('%Y-%m-%d')
    headers = ["العنصر", "المعيار", "المحسوب", "الفرق", "% الفرق", "التقييم"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=c, value=h); cell.font = hf; cell.fill = hfill; cell.alignment = ct; cell.border = bd
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء", "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد", "Ca": "كالسيوم", "P": "فسفور"}
    row = 7
    for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
        if k not in standard: continue
        sv = standard[k]; cv = calculated.get(k, 0.0); diff = cv - sv; pct = (diff/sv*100) if sv else 0
        ev = evaluate_difference(pct)
        for c, v in enumerate([labels[k], round(sv,2), round(cv,2), round(diff,3), round(pct,2), ev["label"]], 1):
            cell = ws.cell(row=row, column=c, value=v); cell.alignment = ct; cell.border = bd; cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#',''))
        row += 1
    for c in range(1, 7): ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO(); wb.save(buf); buf.seek(0); return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# ✅✅✅ التعديل الجديد 5: أسعار السوق حسب الدولة ✅✅✅
# ═══════════════════════════════════════════════════════════════════════════

def get_market_prices(country, city, state=""):
    base = {ing: 280.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
    base.update({"ذرة صفراء": 230, "ذرة بيضاء": 225, "شعير مطحون": 210, "سورجم (فتريتة)": 195, "قمح محلي": 240, "أمباز الفول السوداني": 460, "كسب فول صويا 44%": 440, "كسب فول صويا 48%": 480, "كسب عباد الشمس 36%": 310, "كسب بذور القطن": 290, "نخالة قمح (ردة)": 150, "البرسيم الجاف": 170, "مولاس قصب السكر": 120, "مسحوق أسماك 60%": 850, "مركزات دواجن": 650, "مركزات مواشي": 600, "الحجر الجيري": 40, "فوسفات ثنائي الكالسيوم": 280, "ملح الطعام": 30, "بيكربونات الصوديوم": 340, "مضاد سموم فطرية": 950, "بريمكس تسمين دواجن": 4800, "بريمكس مجترات": 4500, "ليسين نقي": 4200, "ميثيونين نقي": 5800, "زيت ذرة": 1500, "زيت فول الصويا": 1350, "زيت عباد الشمس": 1300, "زيت بذرة القطن": 1400, "زيت الكتان": 1700, "زيت جوز الهند": 1900, "زيت النخيل": 1100, "زيت الكانولا": 1450, "زيت السمسم": 2100, "زيت الزيتون": 3500, "زيت الأفوكادو": 4200, "زيت الفول السوداني": 2200, "شحم حيواني (Tallow)": 900, "دهن الدجاج": 800, "زيت السمك": 3800})
    m = 1.0
    # معاملات حسب المنطقة/الدولة (تكلفة نقل وأسواق)
    multipliers = {
        "السودان": 1.15, "ليبيا": 1.18, "مصر": 1.04, "السعودية": 1.08,
        "الإمارات": 1.12, "الكويت": 1.10, "قطر": 1.10, "البحرين": 1.09,
        "عمان": 1.07, "اليمن": 1.25, "الأردن": 1.08, "لبنان": 1.15,
        "سوريا": 1.20, "العراق": 1.10, "فلسطين": 1.15, "الجزائر": 1.12,
        "المغرب": 1.10, "تونس": 1.12, "موريتانيا": 1.22, "الصومال": 1.28,
        "جيبوتي": 1.25, "جزر القمر": 1.30, "باقي دول العالم": 1.0,
    }
    m = multipliers.get(country, 1.0)
    if country == "السودان" and "كردفان" in state: m = 1.20
    return {k: v * m for k, v in base.items()}

ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600",
}

@st.cache_data(ttl=3600)
def get_img_b64(paths):
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
            except Exception: pass
    return None

img_base64 = get_img_b64(tuple(PHOTO_OPTIONS))


# ═══════════════════════════════════════════════════════════════════════════
# إدارة الجلسات
# ═══════════════════════════════════════════════════════════════════════════

def init_session():
    if "session_id" not in st.session_state: st.session_state["session_id"] = secrets.token_urlsafe(32)
    if "user_role" not in st.session_state: st.session_state["user_role"] = None
    if "approved" not in st.session_state: st.session_state["approved"] = False
    if "user_data" not in st.session_state: st.session_state["user_data"] = None

def register_session(user_data):
    try:
        ua = ""
        try: ua = st.context.headers.get("User-Agent", "")[:200]
        except Exception: ua = ""
        db_manager.create_session(st.session_state["session_id"], user_data, ip_address="web", user_agent=ua or "unknown")
    except Exception: pass

def log_action(action, details=""):
    try:
        user_data = st.session_state.get("user_data") or {}
        db_manager.update_session_activity(st.session_state.get("session_id", "unknown"), action, details)
        db_manager.log_activity(st.session_state.get("session_id", "unknown"), user_data.get("user_id", ""), user_data.get("username", "زائر"), action, details)
    except Exception: pass

init_session()
# ═══════════════════════════════════════════════════════════════════════════
# CSS المتقدم
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover; background-position: center; background-attachment: fixed;
}
.stApp { background: transparent; }
.main-box {
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px; border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
    margin-bottom: 60px; backdrop-filter: blur(5px);
}
h1, h2, h3, h4, h5, p, span, li, div, label { color: #1a1a1a !important; }

@keyframes duaGlow {
    0%, 100% { box-shadow: 0 15px 40px rgba(0,0,0,0.4), inset 0 0 30px rgba(212,175,55,0.2); }
    50% { box-shadow: 0 15px 40px rgba(0,0,0,0.5), inset 0 0 40px rgba(212,175,55,0.4), 0 0 80px rgba(212,175,55,0.5); }
}
@keyframes floatIcon { 0%, 100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-12px) rotate(6deg); } }
@keyframes gradientShift { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@keyframes shimmerText { 0% { background-position: -500% 0; } 100% { background-position: 500% 0; } }

.dua-main-box {
    background: linear-gradient(135deg, #0d3011 0%, #1b5e20 25%, #2e7d32 50%, #1b5e20 75%, #0d3011 100%);
    background-size: 200% 200%;
    animation: duaGlow 4s ease-in-out infinite, gradientShift 12s ease infinite;
    padding: 32px 28px; border-radius: 22px;
    border: 4px solid #d4af37;
    direction: rtl; text-align: center;
    margin: 25px 0; position: relative; overflow: hidden;
}
.dua-main-box::before { content: "🕌"; position: absolute; top: 15px; right: 25px; font-size: 3.5rem; opacity: 0.25; animation: floatIcon 4s ease-in-out infinite; }
.dua-main-box::after { content: "🕌"; position: absolute; bottom: 15px; left: 25px; font-size: 3.5rem; opacity: 0.25; animation: floatIcon 5s ease-in-out infinite reverse; }
.dua-main-box * { color: white !important; position: relative; z-index: 2; }
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem; margin-bottom: 18px; font-weight: 900; letter-spacing: 1px; text-shadow: 0 2px 10px rgba(212,175,55,0.5); }
.dua-main-box .names {
    display: inline-block;
    background: linear-gradient(90deg, rgba(212,175,55,0.15), rgba(212,175,55,0.35), rgba(212,175,55,0.15));
    background-size: 200% 100%;
    animation: shimmerText 4s linear infinite;
    font-size: 1.65rem; font-weight: 900;
    color: #ffeb3b !important;
    margin: 20px 0; padding: 16px 30px;
    border: 2px solid #d4af37; border-radius: 15px;
    text-shadow: 0 0 20px rgba(255,235,59,0.6);
    font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.2rem; color: #d4af37 !important;
    margin-top: 22px; padding: 18px 25px;
    background: rgba(0,0,0,0.25); border-radius: 12px;
    border-right: 5px solid #d4af37; border-left: 5px solid #d4af37;
}
.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 50%, #ffe082 100%);
    padding: 20px 28px; border-radius: 18px;
    border: 3px solid #d4af37;
    margin: 22px 0; direction: rtl; text-align: center;
    box-shadow: 0 6px 25px rgba(0,0,0,0.15);
}
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b { color: #c62828 !important; font-size: 1.15rem; font-family: 'Amiri', serif !important; }

@keyframes fixedDuaGlow { 0%, 100% { text-shadow: 0 0 8px rgba(255,235,59,0.6); } 50% { text-shadow: 0 0 20px rgba(255,235,59,1), 0 0 30px rgba(212,175,55,0.8); } }
.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    background-size: 200% 100%;
    animation: gradientShift 8s linear infinite;
    color: white !important;
    padding: 11px 20px; z-index: 9998; text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1.05rem; font-weight: bold;
    box-shadow: 0 -4px 25px rgba(0,0,0,0.4);
    letter-spacing: 0.5px;
}
.dua-fixed-banner * { color: #ffeb3b !important; font-family: 'Amiri', serif !important; animation: fixedDuaGlow 3s ease-in-out infinite; }

.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 12px 18px; text-align: right;
    font-size: 1.5rem; font-weight: bold;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 100%);
    padding: 15px 20px; border-radius: 12px;
    margin-bottom: 10px; font-weight: bold;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    text-align: right;
}
.oil-item {
    background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%);
    padding: 12px 18px; border-radius: 12px;
    margin-bottom: 8px; font-weight: bold;
    color: #bf360c !important;
    border-right: 5px solid #e65100;
    box-shadow: 0 4px 15px rgba(230,81,0,0.15);
    text-align: right;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px; direction: rtl; text-align: right;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px; border-radius: 12px;
    border-right: 5px solid #e65100;
    margin-bottom: 18px; direction: rtl; text-align: right;
    box-shadow: 0 4px 15px rgba(230,81,0,0.15);
}
.lab-info-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 20px; border-radius: 12px;
    border-right: 5px solid #1565c0;
    margin: 15px 0; direction: rtl; text-align: right;
}
.country-info-card {
    background: linear-gradient(135deg, #f3e5f5, #e1bee7);
    padding: 18px; border-radius: 12px;
    border-right: 5px solid #6a1b9a;
    margin: 15px 0; direction: rtl; text-align: right;
    box-shadow: 0 4px 15px rgba(106,27,154,0.15);
}
.match-100-card {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 16px; border-radius: 12px;
    border-right: 6px solid #1b5e20;
    margin: 12px 0; direction: rtl; text-align: right;
    box-shadow: 0 6px 20px rgba(27,94,32,0.25);
}
.match-good-card {
    background: linear-gradient(135deg, #fff8e1, #ffecb3);
    padding: 16px; border-radius: 12px;
    border-right: 6px solid #f9a825;
    margin: 12px 0; direction: rtl; text-align: right;
}
.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover; border: 4px solid #d4af37;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    display: block; margin: 0 auto;
}
.stButton > button {
    color: #1a1a1a !important;
    background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important;
    font-weight: bold !important;
}
.stButton > button:hover { background-color: #c8e6c9 !important; }

@keyframes sigPulse {
    0%, 100% { box-shadow: 0 4px 15px rgba(0,0,0,0.3), 0 0 20px rgba(212,175,55,0.3); }
    50% { box-shadow: 0 4px 15px rgba(0,0,0,0.3), 0 0 35px rgba(212,175,55,0.7); }
}
.mini-signature {
    position: fixed; left: 20px; bottom: 65px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 9px 22px;
    font-size: 0.88rem; border-radius: 25px;
    z-index: 9997; direction: rtl;
    border: 2px solid #d4af37;
    animation: sigPulse 3s ease-in-out infinite;
    font-weight: bold;
}
.mini-signature * { color: white !important; }

/* مكتبة الأعلاف - عرض عادي */
.library-section {
    background: #fafafa;
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    border: 2px solid #e0e0e0;
}
.library-table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    direction: rtl;
}
.library-table th {
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important;
    padding: 12px;
    text-align: center;
    font-weight: bold;
    border: 1px solid #0d3011;
}
.library-table td {
    padding: 10px;
    text-align: center;
    border: 1px solid #e0e0e0;
    background: white;
}
.library-table tr:nth-child(even) td { background: #f5f5f5; }
.library-table tr:hover td { background: #e8f5e9; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════════

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 780px; margin: 30px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important; margin-bottom:12px;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:
        </p>
        <div class="names">
        🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️
        </div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>", unsafe_allow_html=True)
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>🔐 بوابة الدخول</h3>", unsafe_allow_html=True)
    col_owner, col_guest = st.columns(2)
    with col_owner:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); padding: 20px; border-radius: 12px; border: 2px solid #2e7d32; text-align: center; margin-bottom: 10px;">
        <h4 style="color: #1b5e20;">👑 المالك</h4>
        <p style="font-size: 0.9rem; color: #555;">الدخول بكود خاص</p>
        </div>
        """, unsafe_allow_html=True)
        owner_code = st.text_input("🔑 كود المالك:", type="password", key="owner_code_input")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            if owner_code.strip() == OWNER_CODE:
                user_data = {"user_id": "owner", "username": "المالك", "role": "owner", "full_name": SUPERVISOR, "phone": WHATSAPP_NUMBER, "email": OWNER_EMAIL}
                st.session_state.update({"approved": True, "user_role": "owner", "user_data": user_data})
                register_session(user_data)
                log_action("تسجيل دخول", "المالك")
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")
    with col_guest:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff8e1, #ffecb3); padding: 20px; border-radius: 12px; border: 2px solid #d4af37; text-align: center; margin-bottom: 10px;">
        <h4 style="color: #e65100;">👥 زائر / مستخدم</h4>
        <p style="font-size: 0.9rem; color: #555;">أدخل اسمك للدخول</p>
        </div>
        """, unsafe_allow_html=True)
        guest_name = st.text_input("👤 اسمك:", placeholder="أحمد محمد", key="guest_name_input")
        guest_phone = st.text_input("📱 واتساب (اختياري):", placeholder="+249...", key="guest_phone_input")
        if st.button("👥 دخول كزائر", use_container_width=True):
            name = guest_name.strip() or "زائر"
            user_data = {"user_id": f"guest_{secrets.token_hex(4)}", "username": name, "role": "guest", "full_name": name, "phone": guest_phone.strip() if guest_phone else "", "email": ""}
            st.session_state.update({"approved": True, "user_role": "guest", "user_data": user_data})
            register_session(user_data)
            log_action("تسجيل دخول", f"زائر: {name}")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════════

def is_owner(): return st.session_state.get("user_role") == "owner"

user_data = st.session_state.get("user_data") or {}
user_name = user_data.get("full_name", "زائر")

st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = "المالك 👑" if is_owner() else f"مستخدم: {user_name} 👥"
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5; border-radius:10px;'>الحساب: <b>{role_label}</b></div>", unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        log_action("تسجيل خروج")
        for k in list(st.session_state.keys()):
            if k not in ["inventory", "session_id"]: del st.session_state[k]
        st.session_state["approved"] = False
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color: #0d3011; text-align:right; margin-bottom:0; text-shadow: 2px 2px 4px rgba(0,0,0,0.15), 0 0 20px rgba(27,94,32,0.4); font-weight: 900; font-size: 2.3rem; -webkit-text-stroke: 0.5px #1b5e20;'>🌾 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #1565C0; text-align:right; font-size: 1.25rem; font-weight: 600; margin-top: 8px;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #fff8e1, #ffe082); padding: 12px 20px; border-radius: 12px; border-right: 6px solid #c62828; border-left: 6px solid #c62828; margin-top: 10px; box-shadow: 0 4px 15px rgba(198,40,40,0.25);'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0; font-weight: 900; font-size: 1.55rem;'>👨‍🔬 {SUPERVISOR}</h3>
        <p style='color: #0d47a1; text-align:right; margin: 5px 0 0 0; font-weight: 700; font-size: 1.15rem;'>✨ {SUPERVISOR_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR_BANNER}</div>', unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# التبويبات
# ═══════════════════════════════════════════════════════════════════════════

if is_owner():
    tabs_titles = ["🔬 تركيب الأعلاف", "📚 مكتبة الأعلاف", "🧪 المختبر", "🌰 مكتبة الزيوت", "🍼 بدائل الحليب", "📷 المختبر الذكي", "👥 المستخدمون", "📊 البورصة", "🏭 المستودعات", "🧾 الفواتير", "🖨️ الديباجة", "📈 التحليلات", "🐔 مزارع الدجاج", "💬 التعليقات", "📚 المراجع", "💡 المساعدة", "📖 الدليل"]
else:
    tabs_titles = ["🔬 تركيب الأعلاف", "📚 مكتبة الأعلاف", "🧪 المختبر", "🌰 مكتبة الزيوت", "🍼 بدائل الحليب", "📷 المختبر الذكي", "📚 المراجع", "💡 المساعدة", "📖 الدليل"]

tabs = st.tabs(tabs_titles)


# ═══════════════════════════════════════════════════════════════════════════
# تبويب 1: تركيب الأعلاف
# ═══════════════════════════════════════════════════════════════════════════

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي — 22 دولة عربية</div>', unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        country = st.selectbox("🌍 الدولة:", list(EXCHANGE_RATES.keys()), key="country")
    with cc2:
        state = st.text_input("🗺️ الولاية/المحافظة:", "", key="state")
    with cc3:
        city = st.text_input("🏙️ المدينة:", "", key="city")
    rate = EXCHANGE_RATES.get(country, {"rate": 1.0, "sym": "USD"})
    local_rate, local_sym = rate["rate"], rate["sym"]
    live_prices = get_market_prices(country, city, state)

    # ✅ عرض معلومات الدولة والمواد المتوفرة فيها
    country_avail = get_country_available_ingredients(country)
    total_all = sum(len(v) for v in BIG_FEEDS_LIBRARY.values())
    st.markdown(f"""
    <div class="country-info-card">
    <b>🌍 الدولة المختارة:</b> {country}<br>
    <b>💱 سعر الصرف:</b> 1 USD = {local_rate:,.2f} {local_sym}<br>
    <b>📦 المواد المتوفرة:</b> <b>{len(country_avail)}</b> من أصل {total_all}<br>
    <small>🔧 المحرك الآلي سيستخدم فقط المواد المتوفرة في {country}</small>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"📋 عرض المواد المتوفرة في {country}"):
        avail_by_cat = {}
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            in_cat = [ing for ing in items.keys() if ing in country_avail]
            if in_cat: avail_by_cat[cat_name] = in_cat
        for cat_name, items in avail_by_cat.items():
            st.markdown(f"**{cat_name}** ({len(items)} مادة)")
            st.markdown(" • ".join([f"`{i}`" for i in items]), unsafe_allow_html=True)

    st.markdown('<div class="section-title">🧬 أساس حساب البروتين</div>', unsafe_allow_html=True)
    protein_basis_choice = st.radio("اختر أساس الحساب:", ["البروتين المهضوم (DP) — الأدق علمياً", "البروتين الخام (CP) — الأسهل ميدانياً"], horizontal=True, key="protein_basis")
    use_dp = "DP" in protein_basis_choice
    if use_dp: st.success("🎯 تستخدم الآن **DP** — الأدق علمياً")
    else: st.info("📊 تستخدم الآن **CP** — الأسهل ميدانياً")

    st.markdown('<div class="section-title">🐾 اختر الحيوان</div>', unsafe_allow_html=True)
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل", "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك"])

    animal_choice = None; production_type = None; requirement = None
    img_key = "عام"; std_key_global = ""

    with animal_tabs[0]:
        st.markdown("### 🐄 الأبقار — NRC 2001")
        cattle_type = st.selectbox("الحالة الفسيولوجية:", ["حليب_عالي", "حليب_متوسط", "حليب_منخفض", "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"], format_func=lambda x: {"حليب_عالي": "🐄 حلابة عالية", "حليب_متوسط": "🐄 حلابة متوسطة", "حليب_منخفض": "🐄 حلابة منخفضة", "تسمين_مكثف": "💪 تسمين مكثف", "تسمين_عادي": "💪 تسمين عادي", "حمل_أخير": "🤰 حمل آخر", "صيانة": "🌿 صيانة"}.get(x, x), key="cattle_type")
        c1_, c2_ = st.columns(2)
        cattle_params = {}
        with c1_:
            if "حليب" in cattle_type: cattle_params["milk_yield"] = st.number_input("🥛 إنتاج الحليب (كجم):", 5.0, 60.0, 20.0, 1.0, key="cattle_milk")
            cattle_params["weight_kg"] = st.number_input("⚖️ الوزن (كجم):", 200.0, 900.0, 500.0, 25.0, key="cattle_wt")
        with c2_:
            req_pre = get_cattle_requirements(cattle_type, **cattle_params)
            st.metric("🧬 DP", f"{req_pre.DP}%"); st.metric("🧬 CP", f"{req_pre.CP}%"); st.metric("🌽 SE", f"{req_pre.SE}")
            st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الأبقار", key="use_cattle"):
            animal_choice = "أبقار"; production_type = cattle_type; requirement = req_pre; img_key = "أبقار"; std_key_global = f"أبقار_{cattle_type}"

    with animal_tabs[1]:
        st.markdown("### 🐏 الأغنام — NRC 2007")
        sg = st.radio("الجنس:", ["ذكر (تسمين)", "أنثى (أمهات)"], horizontal=True, key="sheep_gender")
        is_male_s = "ذكر" in sg
        if is_male_s:
            sheep_type = st.selectbox("الحالة:", ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"], format_func=lambda x: {"تسمين_مكثف": "💪 تسمين مكثف", "تسمين_عادي": "💪 تسمين عادي", "حملان_تيد": "🐑 حملان تيد"}.get(x, x), key="sheep_t_m")
        else:
            sheep_type = st.selectbox("الحالة:", ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"], format_func=lambda x: {"مرضعات": "🍼 مرضعات", "حامل_أخير": "🤰 حامل (4-5)", "حامل_متوسط": "🤰 حامل (1-3)", "صيانة": "🌿 صيانة"}.get(x, x), key="sheep_t_f")
        litter = 1
        if sheep_type == "مرضعات": litter = st.number_input("👶 عدد المواليد:", 1, 3, 1, 1, key="sheep_litter")
        weight_s = st.number_input("⚖️ الوزن (كجم):", 15.0, 120.0, 50.0, 5.0, key="sheep_wt")
        req_pre = get_sheep_requirements(sheep_type, is_male=is_male_s, weight_kg=weight_s, litter_size=litter)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%"); p2.metric("🧬 CP", f"{req_pre.CP}%"); p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الأغنام", key="use_sheep"):
            animal_choice = "أغنام"; production_type = sheep_type; requirement = req_pre; img_key = "أغنام"; std_key_global = f"أغنام_{sheep_type}"

    with animal_tabs[2]:
        st.markdown("### 🐐 الماعز — NRC 2007")
        gg = st.radio("الجنس:", ["ذكر (تسمين)", "أنثى (حلابة)"], horizontal=True, key="goat_gender")
        is_male_g = "ذكر" in gg
        milk_g = 0
        if is_male_g:
            goat_type = st.selectbox("الحالة:", ["تسمين_جديان", "تيوس"], format_func=lambda x: {"تسمين_جديان": "💪 تسمين جديان", "تيوس": "🐐 تيوس"}.get(x, x), key="goat_t_m")
        else:
            goat_type = st.selectbox("الحالة:", ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"], format_func=lambda x: {"حلابة_عالي": "🍼 حلابة عالي", "حلابة_متوسط": "🍼 حلابة متوسط", "حامل_أخير": "🤰 حامل أخير", "صيانة": "🌿 صيانة"}.get(x, x), key="goat_t_f")
            if "حلابة" in goat_type: milk_g = st.number_input("🥛 إنتاج الحليب (كجم):", 0.5, 8.0, 2.0, 0.25, key="goat_milk")
        req_pre = get_goat_requirements(goat_type, is_male=is_male_g, milk_yield=milk_g)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%"); p2.metric("🧬 CP", f"{req_pre.CP}%"); p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الماعز", key="use_goat"):
            animal_choice = "ماعز"; production_type = goat_type; requirement = req_pre; img_key = "ماعز"; std_key_global = f"ماعز_{goat_type}"

    with animal_tabs[3]:
        st.markdown("### 🐪 الإبل — FAO 2010")
        st.info("🐪 الإبل تحتاج بروتيناً أقل وأليافاً أكثر")
        camel_type = st.selectbox("الحالة:", ["نمو", "تسمين", "حليب", "سباق", "صيانة"], format_func=lambda x: {"نمو": "🐪 نمو", "تسمين": "💪 تسمين", "حليب": "🍼 حلابة", "سباق": "🏃 سباق", "صيانة": "🌿 صيانة"}.get(x, x), key="camel_type")
        camel_wt = st.number_input("⚖️ الوزن (كجم):", 100.0, 800.0, 400.0, 25.0, key="camel_wt")
        camel_milk = 5.0
        if camel_type == "حليب": camel_milk = st.number_input("🥛 إنتاج الحليب (لتر):", 2.0, 20.0, 5.0, 0.5, key="camel_milk")
        req_pre = get_camel_requirements(camel_type, weight_kg=camel_wt, milk_yield=camel_milk)
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("🧬 DP", f"{req_pre.DP}%"); p2.metric("🧬 CP", f"{req_pre.CP}%"); p3.metric("🌽 SE", f"{req_pre.SE}"); p4.metric("🌾 NDF", f"{req_pre.NDF}%")
        st.info(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الإبل", key="use_camel"):
            animal_choice = "إبل"; production_type = camel_type; requirement = req_pre; img_key = "إبل"; std_key_global = f"إبل_{camel_type}"

    with animal_tabs[4]:
        st.markdown("### 🐎 الخيول — NRC 2007")
        horse_type = st.selectbox("الحالة:", ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"], format_func=lambda x: {"رياضة_مكثف": "🏇 رياضة مكثف", "رياضة_عادي": "🏇 رياضة عادي", "نمو_أمهار": "🐎 أمهار", "مرضعات": "🍼 مرضعات", "صيانة": "🌿 صيانة"}.get(x, x), key="horse_type")
        horse_wt = st.number_input("⚖️ الوزن (كجم):", 200.0, 800.0, 450.0, 25.0, key="horse_wt")
        req_pre = get_horse_requirements(horse_type, weight_kg=horse_wt)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%"); p2.metric("🧬 CP", f"{req_pre.CP}%"); p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الخيول", key="use_horse"):
            animal_choice = "خيول"; production_type = horse_type; requirement = req_pre; img_key = "خيول"; std_key_global = f"خيول_{horse_type}"

    with animal_tabs[5]:
        st.markdown("### 🐔 الدواجن")
        poultry_strain = st.radio("السلالة:", ["لاحم", "بياض"], horizontal=True, key="poultry_strain")
        poultry_age = st.number_input("العمر (أسبوع):", 1, 20, 1, 1, key="poultry_age")
        req_pre = get_poultry_requirements(poultry_strain, poultry_age)
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("🧬 DP", f"{req_pre.DP}%"); p2.metric("🧬 CP", f"{req_pre.CP}%"); p3.metric("🌽 SE", f"{req_pre.SE}"); p4.metric("Ca", f"{req_pre.Ca}%")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الدواجن", key="use_poultry"):
            animal_choice = "دواجن"; production_type = poultry_strain; requirement = req_pre; img_key = "دواجن"
            if poultry_strain == "لاحم":
                if poultry_age <= 1: std_key_global = "دواجن_لاحم_بادي"
                elif poultry_age <= 3: std_key_global = "دواجن_لاحم_نامي"
                else: std_key_global = "دواجن_لاحم_ناهي"
            else: std_key_global = "دواجن_بياض_إنتاج"

    with animal_tabs[6]:
        st.markdown("### 🦆 السمان")
        quail_strain = st.radio("النوع:", ["تسمين", "بياض"], horizontal=True, key="quail_strain")
        quail_age = st.number_input("العمر (أسبوع):", 1, 8, 1, 1, key="quail_age")
        req_pre = get_quail_requirements(quail_strain, quail_age)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%"); p2.metric("🧬 CP", f"{req_pre.CP}%"); p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد السمان", key="use_quail"):
            animal_choice = "سمان"; production_type = quail_strain; requirement = req_pre; img_key = "سمان"; std_key_global = f"سمان_{quail_strain}"

    with animal_tabs[7]:
        st.markdown("### 🐟 الأسماك")
        fish_species = st.selectbox("النوع:", ["البلطي النيلي", "القرموط الأفريقي", "الكارب"], key="fish_sp")
        fish_stage = st.selectbox("المرحلة:", ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage")
        req_pre = get_fish_requirements(fish_species, fish_stage)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%"); p2.metric("🧬 CP", f"{req_pre.CP}%"); p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الأسماك", key="use_fish"):
            animal_choice = "أسماك"; production_type = fish_stage; requirement = req_pre; img_key = "أسماك"; std_key_global = f"أسماك_{fish_stage.replace(' ', '_')}"

    if not animal_choice or not requirement:
        st.warning("⚠️ اختر حيواناً، وفعّل خيار ✅ الاعتماد للمتابعة")
        st.stop()

    st.markdown(f'<div class="section-title">🎯 المختار: {animal_choice} — {requirement.name_ar}</div>', unsafe_allow_html=True)
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    info_col1.metric("🧬 DP", f"{requirement.DP}%")
    info_col2.metric("🧬 CP", f"{requirement.CP}%")
    info_col3.metric("🌽 SE", f"{requirement.SE}")
    info_col4.metric("🌾 NDF", f"{requirement.NDF}%")
    st.info(f"📝 {requirement.note} | **أساس الحساب: {'DP (مهضوم)' if use_dp else 'CP (خام)'}** | **الدولة: {country}**")

    oil_std_info = get_oil_standard(std_key_global)
    st.markdown('<div class="section-title">🌰 معيار الزيوت</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="oil-info-card">
    <b>📊 الحدود القياسية للزيوت:</b><br>
    ▪️ الحد الأقصى: <b>{oil_std_info['max']}%</b><br>
    ▪️ المثالي: <b>{oil_std_info['optimal']}%</b><br>
    ▪️ المرجع: <b>{oil_std_info['source']}</b><br>
    <small>💡 كل 1% زيت ≈ 90 kcal/kg علف</small>
    </div>
    """, unsafe_allow_html=True)

    requester_name = st.text_input("👤 اسم طالب العلفة:", placeholder="مثال: مزرعة الأمل", value=user_name if not is_owner() else "", key="requester")

    # ═══════════════════════════════════════════════════════════════════
    # زر التركيب الآلي 100%
    # ═══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">⚡ التركيب الآلي الشامل — مطابقة 100%</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="lab-info-card">
    <b>🤖 التركيب الآلي الذكي (مطابقة ≥ 100%):</b><br>
    ▪️ يعتمد فقط على المواد <b>المتوفرة في {country}</b> ({len(country_avail)} مادة)<br>
    ▪️ يستخدم محرك <b>SLSQP</b> عالي الدقة لتقليل الأخطاء<br>
    ▪️ يستهدف مطابقة <b>100%</b> على جميع العناصر (DP, CP, SE, NDF, ADF, Ca, P)<br>
    ▪️ التركيب اليدوي يصل عادة إلى 75%-99% بينما الآلي يصل إلى 100%<br>
    <small>📌 عند اختيار ليبيا مثلاً، لن يستخدم الصويا أو الأمباز لعدم توفرها</small>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 تشغيل التركيب الآلي 100%", type="primary", use_container_width=True, key="auto_full"):
        log_action("تركيب آلي شامل", f"{animal_choice} / {production_type} / {country}")
        with st.spinner(f"⏳ جاري التركيب الآلي باستخدام مواد {country}..."):
            result = auto_run_full_analysis(animal_choice, production_type, requirement.name_ar, std_key_global, live_prices, country=country, custom_ingredients=None)
        if result.get("success"):
            formula = result["formula"]; actual = result["actual_nutrients"]; cost = result["cost"]
            overall_match = result.get("overall_match_pct", 0)
            custom_standard = requirement_to_standard(requirement)
            compare_rows = []; compare_scores = []
            labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP", "SE": "معادل النشاء SE", "NDF": "ألياف NDF", "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH", "Ca": "كالسيوم Ca", "P": "فسفور P"}
            for k, sv in custom_standard.items():
                cv = actual.get(k, 0.0); diff = cv - sv; pct = (diff / sv * 100) if sv else 0
                ev = evaluate_difference(pct)
                compare_scores.append({"score": ev["score"]})
                compare_rows.append({"العنصر": labels.get(k, k), "المعيار": f"{sv:.2f}", "المحسوب": f"{cv:.2f}", "الفرق": f"{diff:+.3f}", "الفرق %": f"{pct:+.2f}%", "التقييم": ev["label"]})
            overall = get_overall_rating(compare_scores)

            # ✅ عرض التقييم بشكل مميز
            if overall_match >= 99.5:
                st.markdown(f"""
                <div class="match-100-card">
                <h3 style="color:#1b5e20; margin:0;">🎯 مطابقة كاملة {overall_match:.1f}%!</h3>
                <p style="margin:5px 0 0 0;">التركيب الآلي حقق مطابقة 100% مع المعيار — أعلى من التركيب اليدوي</p>
                </div>
                """, unsafe_allow_html=True)
            elif overall_match >= 90:
                st.success(f"🌟 مطابقة ممتازة: {overall_match:.1f}% — أفضل من التركيب اليدوي")
            else:
                st.info(f"⭐ مطابقة: {overall_match:.1f}% | التقييم: **{overall['label']}** ({overall['score']:.0f}%)")

            st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

            st.markdown("#### 🌾 المكونات (المتوفرة في " + country + "):")
            for ing, pct in formula.items():
                is_oil = ing in get_oil_ingredients()
                cls = "oil-item" if is_oil else "formula-item"
                icon = "🌰" if is_oil else "▪️"
                st.markdown(f'<div class="{cls}">{icon} <b>{ing}:</b> {pct:.2f}% ({pct*10:.1f} كجم/طن)</div>', unsafe_allow_html=True)

            st.metric("💰 التكلفة الفعلية للطن:", f"${cost:.2f} ({cost*local_rate:,.0f} {local_sym})")

            try:
                db_manager.save_formula(st.session_state["session_id"], user_data.get("username", "زائر"), animal_choice, production_type, requirement.DP, requirement.SE, formula, cost, actual, requester_name)
                log_action("حفظ خلطة آلية", f"{animal_choice}/{country} - ${cost:.2f}")
            except Exception: pass

            try:
                pdf = pdf_gen.generate_report(formula=formula, requirement=requirement, animal_type=animal_choice, breed=requirement.name_ar, cost=cost, city=city, local_cost=cost * local_rate, local_sym=local_sym, requester_name=requester_name, protein_basis="DP" if use_dp else "CP", standard_key=std_key_global, include_charts=True, country=country)
                fname = f"TaworNology_{animal_choice}_{country}_{datetime.now():%Y%m%d_%H%M}.pdf"
                st.download_button("📥 تحميل التقرير PDF", pdf, file_name=fname, mime="application/pdf", use_container_width=True)
            except Exception as e: st.error(f"⚠️ خطأ PDF: {e}")
        else:
            st.error(f"❌ {result.get('message', 'فشل التركيب')}")

    # ═══════════════════════════════════════════════════════════════════
    # اختيار المكونات يدوياً
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown('<div class="section-title">🌾 اختيار المكونات يدوياً</div>', unsafe_allow_html=True)
    st.caption(f"✅ المواد المعروضة أدناه هي المتوفرة في **{country}** فقط")

    selected_ingredients = []; ingredient_prices = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        available_items = {k: v for k, v in items.items() if k in country_avail}
        if not available_items: continue
        with st.expander(f"📁 {cat_name} ({len(available_items)} مادة متوفرة)", expanded=False):
            sub = st.columns(3)
            for i, (ing_name, ing_data) in enumerate(available_items.items()):
                with sub[i % 3]:
                    default_check = ing_name in ["ملح الطعام", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "مضاد سموم فطرية"]
                    if animal_choice in ["أغنام", "ماعز", "أبقار", "إبل"]: default_check = default_check or (ing_name == "بيكربونات الصوديوم")
                    if animal_choice in ["دواجن", "سمان"]: default_check = default_check or ("بريمكس" in ing_name)
                    if cat_name == "🌰 الزيوت النباتية والحيوانية":
                        st.markdown(f"**{ing_name}**")
                        st.caption(f"⚡ SE={ing_data.get('SE', 0):.0f}")
                        checked = st.checkbox("إضافة", value=False, key=f"ck_{animal_choice}_{ing_name}")
                    else:
                        checked = st.checkbox(ing_name, value=default_check, key=f"ck_{animal_choice}_{ing_name}")
                    price = live_prices.get(ing_name, 300.0)
                    if is_owner(): price = st.number_input("$", min_value=5.0, value=float(price), key=f"p_{animal_choice}_{ing_name}", label_visibility="collapsed")
                    else: st.caption(f"💰 ${price:.0f}/طن")
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price

    st.markdown("---")
    if st.button("🚀 تشغيل المحرك اليدوي", type="primary", use_container_width=True, key="run_smart"):
        if len(selected_ingredients) < 3:
            st.error("⚠️ اختر 3 مكونات على الأقل")
        else:
            log_action("تركيب يدوي", f"{animal_choice}/{country}")
            auto_salts = auto_add_salts_and_minerals(animal_choice, requirement, country=country)
            for sname, spct in auto_salts.items():
                if sname not in selected_ingredients:
                    selected_ingredients.append(sname)
                    ingredient_prices[sname] = live_prices.get(sname, 300.0)
            custom_standard = requirement_to_standard(requirement)
            basis_label = "DP" if use_dp else "CP"
            with st.spinner("⏳ جاري التركيب اليدوي..."):
                result = auto_formulate_100(selected_ingredients, ingredient_prices, custom_standard, standard_key=std_key_global, country=country)
            if result["success"]:
                formula = result["formula"]; actual = result["actual_nutrients"]; cost = result["cost"]
                overall_match = result.get("overall_match_pct", 0)
                compare_rows = []; compare_scores = []
                labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP", "SE": "معادل النشاء SE", "NDF": "ألياف NDF", "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH", "Ca": "كالسيوم Ca", "P": "فسفور P"}
                for k, sv in custom_standard.items():
                    cv = actual.get(k, 0.0); diff = cv - sv; pct = (diff / sv * 100) if sv else 0
                    ev = evaluate_difference(pct)
                    compare_scores.append({"score": ev["score"]})
                    compare_rows.append({"العنصر": labels.get(k, k), "المعيار": f"{sv:.2f}", "المحسوب": f"{cv:.2f}", "الفرق": f"{diff:+.3f}", "الفرق %": f"{pct:+.2f}%", "التقييم": ev["label"]})
                overall = get_overall_rating(compare_scores)
                st.success(f"✅ تم التركيب | مطابقة: **{overall_match:.1f}%** | التقييم: **{overall['label']}**")
                st.info(f"💡 الفرق بين الآلي واليدوي: الآلي يستهدف 100% بينما اليدوي قد يصل 75%-99%")
                st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)
                st.markdown("#### 🌾 المكونات:")
                for ing, pct in formula.items():
                    is_oil = ing in get_oil_ingredients()
                    cls = "oil-item" if is_oil else "formula-item"
                    icon = "🌰" if is_oil else "▪️"
                    st.markdown(f'<div class="{cls}">{icon} <b>{ing}:</b> {pct:.2f}% ({pct*10:.1f} كجم/طن)</div>', unsafe_allow_html=True)
                st.metric("💰 التكلفة:", f"${cost:.2f} ({cost*local_rate:,.0f} {local_sym})")
                st.session_state["active_formula"] = formula
                st.session_state["computed_ton_cost"] = cost
                st.session_state["active_animal_img"] = ANIMAL_IMAGES.get(img_key, ANIMAL_IMAGES["عام"])
                st.session_state["active_stage_title"] = f"{animal_choice} — {requirement.name_ar}"
                try:
                    db_manager.save_formula(st.session_state["session_id"], user_data.get("username", "زائر"), animal_choice, production_type, requirement.DP, requirement.SE, formula, cost, actual, requester_name)
                except Exception: pass
                dl1, dl2 = st.columns(2)
                with dl1:
                    try:
                        pdf = pdf_gen.generate_report(formula=formula, requirement=requirement, animal_type=animal_choice, breed=requirement.name_ar, cost=cost, city=city, local_cost=cost * local_rate, local_sym=local_sym, requester_name=requester_name, protein_basis=basis_label, standard_key=std_key_global, include_charts=True, country=country)
                        fname = f"TaworNology_{animal_choice}_{country}_{datetime.now():%Y%m%d_%H%M}.pdf"
                        st.download_button("📥 تحميل PDF", pdf, file_name=fname, mime="application/pdf", use_container_width=True)
                    except Exception as e: st.error(f"⚠️ خطأ PDF: {e}")
                with dl2:
                    try:
                        xl = export_comparison_to_excel(custom_standard, actual, requester_name, animal_choice, requirement.name_ar, formula, std_key_global)
                        if xl:
                            fname = f"TaworNology_{animal_choice}_{country}_{datetime.now():%Y%m%d_%H%M}.xlsx"
                            st.download_button("📊 تحميل Excel", xl, file_name=fname, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                    except Exception as e: st.error(f"⚠️ خطأ Excel: {e}")
            else:
                st.error(f"❌ {result['message']}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب 2: ✅ مكتبة الأعلاف (عرض عادي/طبيعي — جداول)
# ═══════════════════════════════════════════════════════════════════════════

with tabs[1]:
    st.markdown('<div class="section-title">📚 مكتبة الأعلاف الشاملة</div>', unsafe_allow_html=True)
    total_ing = sum(len(v) for v in BIG_FEEDS_LIBRARY.values())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 إجمالي المكونات", total_ing)
    c2.metric("📂 عدد الفئات", len(BIG_FEEDS_LIBRARY))
    c3.metric("🌰 الزيوت", len(get_oil_ingredients()))
    c4.metric("🔬 المراجع", "NRC/FAO/INRA")

    # خيار الفلترة حسب الدولة
    st.markdown("---")
    filter_by_country = st.checkbox(f"🔍 عرض المواد المتوفرة في **{country}** فقط", value=True, key="filter_lib_by_country")
    avail_set = get_country_available_ingredients(country) if filter_by_country else set(_ALL_INGREDIENTS)

    st.markdown(f"### 📖 المكونات ({'متوفرة في ' + country if filter_by_country else 'كل المكونات'})")

    # عرض كل فئة كجدول عادي
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        filtered_items = {k: v for k, v in items.items() if k in avail_set}
        if not filtered_items: continue

        with st.expander(f"📁 {cat_name} ({len(filtered_items)} مادة)", expanded=False):
            # بناء DataFrame للجدول
            rows = []
            is_oil_cat = "الزيوت" in cat_name
            is_mineral_cat = "الأملاح" in cat_name or "البريمكسات" in cat_name or "الإنزيمات" in cat_name
            is_amino_cat = "الأحماض" in cat_name

            for ing_name, d in filtered_items.items():
                row = {"المادة": ing_name}
                if is_oil_cat:
                    row["EE %"] = f"{d.get('EE', 0):.1f}"
                    row["SE"] = f"{d.get('SE', 0):.0f}"
                    row["kcal/kg (تقديري)"] = f"{d.get('SE', 0) * 41:.0f}"
                    row["الوصف"] = d.get('desc', '')[:40]
                elif is_mineral_cat:
                    row["CP %"] = f"{d.get('CP', 0):.1f}"
                    row["Ca %"] = f"{d.get('Ca', 0):.2f}"
                    row["P %"] = f"{d.get('P', 0):.2f}"
                    row["ASH %"] = f"{d.get('ASH', 0):.1f}"
                elif is_amino_cat:
                    row["CP %"] = f"{d.get('CP', 0):.1f}"
                    row["DC"] = f"{d.get('DC', 0):.2f}"
                else:
                    row["CP %"] = f"{d.get('CP', 0):.1f}"
                    row["DC"] = f"{d.get('DC', 0):.2f}"
                    row["SE"] = f"{d.get('SE', 0):.0f}"
                    row["NDF %"] = f"{d.get('NDF', 0):.1f}"
                    row["ADF %"] = f"{d.get('ADF', 0):.1f}"
                    row["EE %"] = f"{d.get('EE', 0):.1f}"
                    row["Ca %"] = f"{d.get('Ca', 0):.2f}"
                    row["P %"] = f"{d.get('P', 0):.2f}"
                rows.append(row)

            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True, height=min(400, 40 + len(rows)*35))

    st.markdown("---")
    st.markdown("### 🕌 دعاء")
    st.markdown(f"<p style='text-align:center; font-size:1.1rem; color:#1b5e20; font-family:Amiri,serif;'>{DUA_FULL}</p>", unsafe_allow_html=True)
    # ═══════════════════════════════════════════════════════════════════════════
# تبويب 3: المختبر
# ═══════════════════════════════════════════════════════════════════════════

with tabs[2]:
    st.markdown('<div class="section-title">🧪 مختبر تحليل الخلطات الجاهزة</div>', unsafe_allow_html=True)
    st.info("📌 أدخل أوزان المكونات (بالكيلوجرام) وسيقوم المختبر بتحليلها")
    st.markdown("### 🐾 اختر الحيوان والحالة")
    animal_options = get_animal_options_for_lab()
    col_a, col_b = st.columns(2)
    with col_a: lab_animal = st.selectbox("🐾 نوع الحيوان:", list(animal_options.keys()), key="lab_animal")
    with col_b:
        lab_states = animal_options[lab_animal]["states"]
        lab_state = st.selectbox("📋 الحالة:", list(lab_states.keys()), format_func=lambda x: lab_states[x], key="lab_state")

    extra_params = {}
    needs = animal_options[lab_animal]["needs_extra"]
    defaults = animal_options[lab_animal]["default_extra"]
    if needs:
        st.markdown("#### ⚙️ معاملات إضافية")
        cols = st.columns(len(needs))
        for i, need in enumerate(needs):
            with cols[i]:
                if need == "milk_yield":
                    label = "🥛 إنتاج الحليب (لتر):" if lab_animal == "إبل" else "🥛 إنتاج الحليب (كجم):"
                    extra_params["milk_yield"] = st.number_input(label, 0.5, 60.0, defaults["milk_yield"], 0.5, key=f"lab_extra_{need}")
                elif need == "weight_kg":
                    max_w = 900.0 if lab_animal == "أبقار" else 800.0
                    extra_params["weight_kg"] = st.number_input("⚖️ الوزن (كجم):", 10.0, max_w, defaults["weight_kg"], 5.0, key=f"lab_extra_{need}")
                elif need == "is_male":
                    gender = st.radio("الجنس:", ["ذكر", "أنثى"], index=0 if defaults["is_male"] else 1, key=f"lab_extra_{need}")
                    extra_params["is_male"] = "ذكر" in gender
                elif need == "litter_size":
                    extra_params["litter_size"] = st.number_input("👶 عدد المواليد:", 1, 3, defaults["litter_size"], 1, key=f"lab_extra_{need}")
                elif need == "age_weeks":
                    extra_params["age_weeks"] = st.number_input("📅 العمر (أسبوع):", 1, 20, defaults["age_weeks"], 1, key=f"lab_extra_{need}")
                elif need == "species":
                    extra_params["species"] = st.selectbox("🐟 النوع:", ["البلطي النيلي", "القرموط الأفريقي", "الكارب"], key=f"lab_extra_{need}")

    try:
        lab_requirement = build_requirement_for_lab(lab_animal, lab_state, extra_params)
        if lab_requirement:
            st.markdown("### 📊 المعيار القياسي")
            metric_cols = st.columns(5)
            metric_cols[0].metric("🧬 DP", f"{lab_requirement.DP}%")
            metric_cols[1].metric("🧬 CP", f"{lab_requirement.CP}%")
            metric_cols[2].metric("🌽 SE", f"{lab_requirement.SE}")
            metric_cols[3].metric("🌾 NDF", f"{lab_requirement.NDF}%")
            metric_cols[4].metric("💊 Ca", f"{lab_requirement.Ca}%")
            st.caption(f"📝 {lab_requirement.note}")
    except Exception as e:
        st.error(f"⚠️ خطأ: {e}"); lab_requirement = None

    st.markdown("---")
    st.markdown("### 📋 بيانات العينة")
    sample_col1, sample_col2 = st.columns(2)
    with sample_col1: sample_id = st.text_input("🔬 رقم العينة:", value=f"LAB-{datetime.now():%Y%m%d-%H%M}", key="lab_sample_id")
    with sample_col2: lab_requester = st.text_input("👤 اسم طالب التحليل:", value=user_name if not is_owner() else "", placeholder="مثال: مصنع الأعلاف", key="lab_requester")

    st.markdown("### 🌾 إدخال أوزان المكونات")
    st.caption("💡 أدخل وزن كل مادة — اترك صفراً إذا لم تستخدمها")
    lab_ingredients_input = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=False):
            cols = st.columns(3)
            for i, (ing_name, ing_data) in enumerate(items.items()):
                with cols[i % 3]:
                    help_text = f"CP={ing_data.get('CP', 0):.1f}% | SE={ing_data.get('SE', 0):.0f} | EE={ing_data.get('EE', 0):.1f}%"
                    weight = st.number_input(f"{ing_name} (كجم):", min_value=0.0, value=0.0, step=0.5, key=f"lab_ing_{ing_name}", help=help_text)
                    if weight > 0: lab_ingredients_input[ing_name] = weight

    lab_notes = st.text_area("📝 ملاحظات المختبر:", placeholder="أي ملاحظات...", key="lab_notes")
    st.markdown("---")

    if st.button("🔬 تشغيل التحليل المختبري", type="primary", use_container_width=True, key="run_lab_analysis"):
        if not lab_ingredients_input: st.error("⚠️ أدخل وزن مادة واحدة على الأقل")
        elif not lab_requirement: st.error("⚠️ تعذر تحديد المعيار")
        else:
            log_action("تحليل مختبري", f"{lab_animal}/{lab_state}/{sample_id}")
            with st.spinner("⏳ جاري التحليل..."):
                analysis = analyze_ready_mixture(lab_ingredients_input, lab_animal, lab_state, extra_params)
            if analysis["success"]:
                st.success(f"✅ تم التحليل! الوزن: {analysis['total_weight']:.2f} كجم")
                n_total = len(analysis['compare_rows'])
                n_ok = sum(1 for r in analysis['compare_rows'] if abs(r['_pct']) <= 5)
                n_near = sum(1 for r in analysis['compare_rows'] if 5 < abs(r['_pct']) <= 15)
                n_bad = sum(1 for r in analysis['compare_rows'] if abs(r['_pct']) > 15)
                sc1, sc2, sc3, sc4 = st.columns(4)
                sc1.metric("إجمالي", n_total); sc2.metric("✅ مطابقة", n_ok)
                sc3.metric("⚠️ قريبة", n_near); sc4.metric("❌ غير مطابقة", n_bad)
                overall = analysis["overall"]
                if overall["score"] >= 85: st.success(f"🎯 **{overall['label']}** — {overall['score']:.0f}%")
                elif overall["score"] >= 65: st.warning(f"⭐ **{overall['label']}** — {overall['score']:.0f}%")
                else: st.error(f"⚠️ **{overall['label']}** — {overall['score']:.0f}%")
                st.markdown("### 📋 جدول المقارنة التفصيلي")
                display_rows = [{"العنصر": r["العنصر"], "المعيار": r["المعيار"], "المحسوب": r["المحسوب"], "الفرق": r["الفرق"], "الفرق %": r["الفرق %"], "التقييم": r["التقييم"]} for r in analysis["compare_rows"]]
                st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)
                if analysis["violations"]:
                    st.markdown("### ⚠️ المخالفات")
                    for v in analysis["violations"]:
                        color = "#ffebee" if v["type"] == "زيادة" else "#fff3e0"
                        icon = "⬆️" if v["type"] == "زيادة" else "⬇️"
                        st.markdown(f'<div style="background:{color}; padding:12px 18px; border-radius:10px; border-right:5px solid #c62828; margin-bottom:8px; direction:rtl; text-align:right;">{icon} <b>{v["element"]}</b>: {v["type"]} بقيمة {v["diff"]} (المعيار: {v["target"]} | الفعلي: {v["actual"]})</div>', unsafe_allow_html=True)
                oil = analysis["oil_check"]
                if oil["total"] > 0:
                    st.markdown("### 🌰 تقييم الزيوت")
                    if oil["status"] == "exceeded": st.error(f"⚠️ تجاوز! {oil['total']:.2f}% > {oil['max']}%")
                    elif oil["status"] == "high": st.warning(f"⚡ مرتفع: {oil['total']:.2f}%")
                    else: st.success(f"✅ مطابق: {oil['total']:.2f}%")
                st.markdown("### 💡 التوصيات الفنية")
                recommendations = generate_recommendations(analysis)
                for i, rec in enumerate(recommendations, 1): st.markdown(f"**{i}.** {rec}")
                st.markdown("### 🌾 مكونات العينة")
                formula_pct = analysis["formula_pct"]
                sorted_ings = sorted(formula_pct.items(), key=lambda x: -x[1])
                for ing, pct in sorted_ings:
                    kg = pct * analysis['total_weight'] / 100.0
                    is_oil = ing in get_oil_ingredients()
                    cls = "oil-item" if is_oil else "formula-item"
                    icon = "🌰" if is_oil else "▪️"
                    st.markdown(f'<div class="{cls}">{icon} <b>{ing}:</b> {kg:.2f} كجم ({pct:.2f}%)</div>', unsafe_allow_html=True)
                try:
                    db_manager.save_lab_analysis(st.session_state["session_id"], user_data.get("username", "زائر"), lab_animal, lab_state, sample_id, formula_pct, analysis["actual"], analysis["standard"], overall["score"], lab_requester)
                    log_action("حفظ تحليل", sample_id)
                except Exception: pass
                if PLOTLY_AVAILABLE and len(formula_pct) > 1:
                    try:
                        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b','#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41','#c62828','#6a1b9a']
                        fig = px.pie(values=list(formula_pct.values()), names=list(formula_pct.keys()), title=f"توزيع مكونات العينة {sample_id}", color_discrete_sequence=colors)
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception: pass
                st.markdown("### 📥 تحميل التقرير")
                dl1, dl2 = st.columns(2)
                with dl1:
                    try:
                        pdf_lab = pdf_gen.generate_lab_report(analysis=analysis, requester_name=lab_requester, sample_id=sample_id, notes=lab_notes)
                        fname = f"TaworNology_LAB_{sample_id}_{datetime.now():%Y%m%d}.pdf"
                        st.download_button("📥 تحميل PDF", pdf_lab, file_name=fname, mime="application/pdf", use_container_width=True)
                    except Exception as e: st.error(f"⚠️ خطأ PDF: {e}")
                with dl2:
                    try:
                        xl = export_comparison_to_excel(analysis["standard"], analysis["actual"], lab_requester, analysis["animal"], analysis["requirement"].name_ar, formula_pct, get_standard_key_for_lab(lab_animal, lab_state))
                        if xl:
                            fname = f"TaworNology_LAB_{sample_id}_{datetime.now():%Y%m%d}.xlsx"
                            st.download_button("📊 تحميل Excel", xl, file_name=fname, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                    except Exception as e: st.error(f"⚠️ خطأ Excel: {e}")
            else:
                st.error(f"❌ {analysis['message']}")

    with st.expander("📖 كيف يعمل المختبر؟"):
        st.markdown("""
        ### خطوات التحليل:
        1. **اختر الحيوان** والحالة الفسيولوجية
        2. **أدخل معاملات إضافية**
        3. **أدخل أوزان المكونات** بالكيلوجرام
        4. **اضغط زر التحليل**

        ### يقوم المختبر بـ:
        - حساب النسب المئوية
        - حساب القيم الغذائية
        - المقارنة مع NRC/FAO/INRA
        - تحديد المخالفات
        - تقييم الزيوت
        - إعطاء توصيات فنية
        """)


# ═══════════════════════════════════════════════════════════════════════════
# تبويب 4: مكتبة الزيوت
# ═══════════════════════════════════════════════════════════════════════════

with tabs[3]:
    st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>', unsafe_allow_html=True)
    st.write("الزيوت المعتمدة وفق NRC و INRA و FAO و Ross 308")
    st.markdown("### 📊 الحدود القياسية للزيوت")
    oil_std_rows = [{"الحيوان/الحالة": key, "الحد الأقصى %": f"{val['max']}%", "المثالي %": f"{val['optimal']}%", "المرجع": val["source"]} for key, val in MAX_OIL_PERCENTAGE.items()]
    st.dataframe(pd.DataFrame(oil_std_rows), use_container_width=True, hide_index=True)
    st.markdown("### 🌰 الزيوت المتوفرة")
    oils = get_oil_ingredients()
    categories = {
        "زيوت نباتية غنية بأوميغا 6": ["زيت ذرة", "زيت عباد الشمس", "زيت بذرة القطن", "زيت فول الصويا"],
        "زيوت نباتية غنية بأوميغا 3": ["زيت الكتان", "زيت الكانولا", "زيت السمك"],
        "زيوت متوازنة": ["زيت النخيل", "زيت جوز الهند", "زيت الزيتون", "زيت السمسم", "زيت الفول السوداني", "زيت الأفوكادو"],
        "دهون حيوانية": ["شحم حيواني (Tallow)", "دهن الدجاج"],
    }
    for category, oil_list in categories.items():
        st.markdown(f"#### {category}")
        for ing_name in oil_list:
            if ing_name not in oils: continue
            ing_data = oils[ing_name]
            with st.expander(f"🌰 {ing_name}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("SE", f"{ing_data.get('SE', 0):.0f}")
                    st.metric("الدهن", "100%")
                with c2:
                    st.metric("طاقة تقديرية", f"{ing_data.get('SE', 0) * 41:.0f} kcal/kg")
                    price = get_market_prices('السودان', 'الخرطوم').get(ing_name, 0)
                    st.metric("سعر تقريبي", f"${price:.0f}/طن")
                with c3:
                    st.metric("أقصى للدواجن", f"{ing_data.get('max_poultry', 'N/A')}%")
                    st.metric("أقصى للمجترات", f"{ing_data.get('max_ruminant', 'N/A')}%")
                st.info(f"📝 {ing_data.get('desc', '')}")
                st.caption(f"📖 المرجع: {ing_data.get('source', 'NRC')}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب 5: بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

with tabs[4]:
    st.markdown('<div class="section-title">🍼 مختبر بدائل الحليب</div>', unsafe_allow_html=True)
    mr1, mr2 = st.columns(2)
    with mr1:
        mr_animal = st.selectbox("نوع الحيوان:", list(MILK_REPLACER_STANDARDS.keys()), key="mr_a")
        mr_volume = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0, 10.0, key="mr_v")
        mr_req = st.text_input("اسم طالب التركيب:", value=user_name if not is_owner() else "", key="mr_r")
    with mr2:
        std_mr = MILK_REPLACER_STANDARDS[mr_animal]
        st.markdown(f"""
        <div class="price-card">
        <b>📊 المعيار — {mr_animal}:</b><br>
        ▪️ بروتين: <b>{std_mr['CP']}%</b><br>
        ▪️ دهن: <b>{std_mr['Fat']}%</b><br>
        ▪️ لاكتوز: <b>{std_mr['Lactose']}%</b><br>
        <small>{std_mr['notes']}</small>
        </div>
        """, unsafe_allow_html=True)
    mr_selected = []
    mr_cols = st.columns(3)
    for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
        with mr_cols[i % 3]:
            default_mr = name in ["حليب مجفف منزوع الدسم", "حليب مجفف كامل الدسم", "شرش حليب مجفف", "زيت جوز الهند", "زيت النخيل", "بريمكس فيتامينات", "كالسيوم كربونات", "فوسفات ثنائي الكالسيوم", "ملح طعام"]
            if st.checkbox(f"{name} — ${data['price']}", value=default_mr, key=f"mr_{name}"):
                mr_selected.append(name)
    if st.button("🧪 تشغيل التركيب", type="primary", use_container_width=True, key="mr_run"):
        if len(mr_selected) < 3: st.warning("⚠️ اختر 3 مكونات على الأقل")
        else:
            r = formulate_milk_replacer(mr_animal, mr_volume, mr_selected)
            if r["success"]:
                st.success(f"✅ تم التركيب لـ ({mr_animal})")
                for ing, pct in r["formula"].items():
                    kg = pct * mr_volume / 100.0
                    st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}% ({kg:.2f} كجم)</div>', unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("💰 التكلفة لـ 100 كجم:", f"${r['cost_per_100kg']:.2f}")
                m2.metric("💰 التكلفة لكل كجم:", f"${r['cost_per_kg']:.3f}")
                try:
                    db_manager.save_milk_replacer(st.session_state["session_id"], user_data.get("username", "زائر"), mr_animal, r["formula"], r["cost_per_kg"], mr_req)
                    log_action("حفظ بديل حليب", mr_animal)
                except Exception: pass
            else: st.error(f"❌ {r['message']}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب 6: OCR
# ═══════════════════════════════════════════════════════════════════════════

with tabs[5]:
    st.markdown('<div class="section-title">📷 المختبر الذكي (OCR)</div>', unsafe_allow_html=True)
    if not OCR_AVAILABLE:
        st.error("⚠️ مكتبة pytesseract غير مثبتة")
        st.code("pip install pytesseract opencv-python-headless", language="bash")
    else:
        uploaded = st.file_uploader("📤 ارفع صورة المكونات:", type=["jpg", "jpeg", "png"])
        if uploaded:
            st.image(uploaded, caption="الصورة", use_container_width=True)
            ocr_req = st.text_input("👤 اسم طالب التحليل:", value=user_name if not is_owner() else "", key="ocr_req")
            if st.button("🔍 تحليل الصورة", type="primary", use_container_width=True):
                log_action("OCR تحليل صورة")
                with st.spinner("جاري التحليل..."):
                    r = extract_ingredients_from_image(uploaded.read())
                if r["success"]:
                    st.success(f"✅ تم استخراج {r['count']} مادة")
                    if r["ingredients"]:
                        st.dataframe(pd.DataFrame([{"المادة": k, "النسبة": f"{v:.2f}%"} for k, v in r["ingredients"].items()]), use_container_width=True, hide_index=True)
                        nutrients = compute_formula_nutrients(r["ingredients"])
                        n1, n2, n3, n4 = st.columns(4)
                        n1.metric("CP", f"{nutrients['CP']:.2f}%")
                        n2.metric("DP", f"{nutrients['DP']:.2f}%")
                        n3.metric("SE", f"{nutrients['SE']:.2f}")
                        n4.metric("NDF", f"{nutrients['NDF']:.2f}%")
                    with st.expander("📝 النص الخام"): st.text(r.get("raw_text", ""))
                else: st.error(f"❌ {r['message']}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويبات المالك
# ═══════════════════════════════════════════════════════════════════════════

if is_owner():
    with tabs[6]:
        st.markdown('<div class="section-title">👥 إدارة المستخدمين والجلسات</div>', unsafe_allow_html=True)
        st.info("📊 لوحة المالك — جميع المستخدمين والجلسات والأنشطة")
        session_stats = db_manager.get_session_stats()
        stats_cols = st.columns(4)
        stats_cols[0].metric("🌟 إجمالي الجلسات", session_stats["total"])
        stats_cols[1].metric("📅 جلسات اليوم", session_stats["today"])
        stats_cols[2].metric("📊 آخر 7 أيام", session_stats["week"])
        stats_cols[3].metric("🟢 نشط (30 دقيقة)", session_stats["active_30min"])
        app_stats = db_manager.get_stats()
        stats_cols2 = st.columns(4)
        stats_cols2[0].metric("🧪 تحاليل المختبر", app_stats["labs"])
        stats_cols2[1].metric("🔬 خلطات مركبة", app_stats["formulas"])
        stats_cols2[2].metric("🍼 بدائل الحليب", app_stats["milk"])
        stats_cols2[3].metric("👥 جلسات", app_stats["users"])
        st.markdown("---")
        user_tabs = st.tabs(["📋 جميع الجلسات", "👤 ملخص المستخدمين", "🔬 الخلطات المركبة", "🧪 تحاليل المختبر"])
        with user_tabs[0]:
            st.markdown("### 📋 جميع الجلسات (آخر 500)")
            sessions = db_manager.get_all_sessions(500)
            if sessions:
                rows = []
                for s in sessions:
                    login_time = s[5] or ""; last_act = s[6] or ""
                    try:
                        login_dt = datetime.fromisoformat(login_time); login_str = login_dt.strftime('%Y-%m-%d %H:%M')
                    except Exception: login_str = login_time[:16]
                    try:
                        last_dt = datetime.fromisoformat(last_act); delta = (datetime.now() - last_dt).total_seconds()
                        status = "🟢" if delta < 1800 else "⚪"
                        last_str = last_dt.strftime('%Y-%m-%d %H:%M')
                    except Exception: last_str = last_act[:16]; status = "⚪"
                    rows.append({"الحالة": status, "المستخدم": s[1] or "زائر", "الدور": s[2] or "guest", "الاسم الكامل": s[3] or "", "الهاتف": s[4] or "", "الدخول": login_str, "آخر نشاط": last_str, "عدد الأنشطة": s[7] or 0})
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=500)
                st.caption(f"📊 إجمالي: {len(rows)} جلسة")
            else: st.info("لا توجد جلسات مسجلة")
        with user_tabs[1]:
            st.markdown("### 👤 ملخص نشاط المستخدمين")
            users_summary = db_manager.get_user_activity_summary()
            if users_summary:
                rows = []
                for u in users_summary:
                    try:
                        first_dt = datetime.fromisoformat(u[4] or ""); first_str = first_dt.strftime('%Y-%m-%d %H:%M')
                    except Exception: first_str = (u[4] or "")[:16]
                    try:
                        last_dt = datetime.fromisoformat(u[3] or ""); last_str = last_dt.strftime('%Y-%m-%d %H:%M')
                    except Exception: last_str = (u[3] or "")[:16]
                    rows.append({"المستخدم": u[0] or "زائر", "عدد الجلسات": u[1] or 0, "إجمالي الأنشطة": u[2] or 0, "أول دخول": first_str, "آخر ظهور": last_str})
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else: st.info("لا توجد بيانات")
        with user_tabs[2]:
            st.markdown("### 🔬 آخر الخلطات المركبة")
            formulas = db_manager.get_all_formulas(100)
            if formulas:
                rows = []
                for f in formulas:
                    try:
                        dt = datetime.fromisoformat(f[5]); date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except Exception: date_str = str(f[5])[:16]
                    rows.append({"المستخدم": f[0], "الحيوان": f[1], "الحالة": f[2], "التكلفة ($)": f"{f[3]:.2f}" if f[3] else "-", "طالب العلفة": f[4] or "-", "التاريخ": date_str})
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else: st.info("لا توجد خلطات مسجلة")
        with user_tabs[3]:
            st.markdown("### 🧪 آخر تحاليل المختبر")
            analyses = db_manager.get_all_lab_analyses(100)
            if analyses:
                rows = []
                for a in analyses:
                    try:
                        dt = datetime.fromisoformat(a[6]); date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except Exception: date_str = str(a[6])[:16]
                    score = a[4] or 0
                    rows.append({"المستخدم": a[0], "الحيوان": a[1], "الحالة": a[2], "رقم العينة": a[3], "التقييم %": f"{score:.0f}%", "طالب التحليل": a[5] or "-", "التاريخ": date_str})
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else: st.info("لا توجد تحاليل مسجلة")

    with tabs[7]:
        st.markdown('<div class="section-title">📊 البورصة</div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🐄 الماشية", "🥩 المنتجات"])
        with t1:
            if "livestock_prices" not in st.session_state:
                st.session_state["livestock_prices"] = {"عجول تسمين هولشتاين ($)": 1350.0, "أبقار كنانة ($)": 900.0, "ضأن محلي ($)": 180.0, "ماعز نوبي ($)": 130.0, "إبل حاشي ($)": 1200.0, "كتكوت لاحم يوم ($)": 0.65, "دجاج بياض ($)": 5.50}
            for animal, price in list(st.session_state["livestock_prices"].items()):
                new_p = st.number_input(f"تحديث: {animal}", min_value=0.0, value=float(price), step=0.1, key=f"lv_{animal}")
                st.session_state["livestock_prices"][animal] = new_p
        with t2:
            if "products_prices" not in st.session_state:
                st.session_state["products_prices"] = {"كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00, "كيلو لحم إبل ($)": 8.50, "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 ($)": 4.20, "لتر حليب بقر ($)": 0.90, "لتر حليب إبل ($)": 3.50}
            for product, price in list(st.session_state["products_prices"].items()):
                new_p = st.number_input(f"تحديث: {product}", min_value=0.0, value=float(price), step=0.05, key=f"pr_{product}")
                st.session_state["products_prices"][product] = new_p

    with tabs[8]:
        st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
        if "inventory" not in st.session_state: st.session_state["inventory"] = {}
        if not st.session_state["inventory"]:
            for cat in BIG_FEEDS_LIBRARY.values():
                for ing in cat: st.session_state["inventory"][ing] = {"quantity": 25.0, "unit": "طن"}
        inv = st.session_state["inventory"]
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("إجمالي", len(inv))
        low = sum(1 for v in inv.values() if (v.get("quantity", 0) if isinstance(v, dict) else v) < 5)
        col_b.metric("منخفضة", low)
        crit = sum(1 for v in inv.values() if (v.get("quantity", 0) if isinstance(v, dict) else v) <= 0)
        col_c.metric("نفذت", crit)
        col_d.metric("آمنة", len(inv) - low - crit)
        cols = st.columns(3)
        for i, (name, data) in enumerate(list(inv.items())[:60]):
            with cols[i % 3]:
                q = data["quantity"] if isinstance(data, dict) else data
                badge = "🔴" if q <= 0 else ("🟡" if q < 5 else "🟢")
                st.markdown(f"{badge} **{name}**: {q:.1f} طن")
                new_q = st.number_input("تحديث:", min_value=0.0, value=float(q), key=f"inv_{name}", label_visibility="collapsed")
                if isinstance(inv[name], dict): inv[name]["quantity"] = new_q

    with tabs[9]:
        st.markdown('<div class="section-title">🧾 الفواتير</div>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1: client = st.text_input("العميل:", "مزرعة الأمل")
        with fc2: tons = st.number_input("الكمية (طن):", 0.1, 1000.0, 2.0, 0.5)
        with fc3: profit = st.number_input("هامش الربح ($/طن):", 0.0, 1000.0, 50.0)
        sell = st.session_state.get("computed_ton_cost", 280.0) + profit
        total = sell * tons
        st.markdown(f"""
        <div class="price-card">
        <h4>🧾 فاتورة</h4>
        <p><b>العميل:</b> {client}</p>
        <p><b>الكمية:</b> {tons} طن</p>
        <p><b>سعر الطن:</b> ${sell:.2f}</p>
        <p style="font-size:1.3rem; color:#1b5e20;"><b>الإجمالي:</b> ${total:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with tabs[10]:
        st.markdown('<div class="section-title">🖨️ الديباجة</div>', unsafe_allow_html=True)
        brand = st.text_input("اسم البراند:", APP_NAME)
        active_img = st.session_state.get("active_animal_img", ANIMAL_IMAGES["عام"])
        active_title = st.session_state.get("active_stage_title", "إنتاج عام")
        st.markdown(f"""
        <div style="border: 3px dashed #1b5e20; padding: 30px; border-radius: 15px; background: linear-gradient(135deg, #f1f8e9, #e8f5e9); direction: rtl; text-align: center;">
        <img src="{active_img}" style="width:100%; max-height:200px; object-fit:cover; border-radius:12px; margin-bottom:15px;">
        <h2 style="color: #1b5e20;">🌟 {brand} 🌟</h2>
        <h3 style="color: #c62828;">{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>
        <p style="background:#e8f5e9; padding:12px; border-radius:8px; color:#1b5e20; font-weight:bold;">🎯 {active_title}</p>
        <small style="color:#666;">📅 {datetime.now():%Y-%m-%d}</small>
        <br><small style="color:#c62828;">🤲 {DUA_SHORT}</small>
        </div>
        """, unsafe_allow_html=True)

    with tabs[11]:
        st.markdown('<div class="section-title">📈 التحليلات</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("الخلطات", app_stats.get("formulas", 0))
        m2.metric("التحاليل", app_stats.get("labs", 0))
        m3.metric("بدائل الحليب", app_stats.get("milk", 0))
        m4.metric("الجلسات", session_stats["total"])
        if PLOTLY_AVAILABLE:
            usage = pd.DataFrame({'المادة': ['ذرة', 'صويا', 'نخالة', 'زيوت', 'أملاح', 'أخرى'], 'النسبة %': [42, 23, 14, 8, 8, 5]})
            fig = px.pie(usage, values='النسبة %', names='المادة', color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)

    with tabs[12]:
        st.markdown('<div class="section-title">🐔 مزارع الدجاج</div>', unsafe_allow_html=True)
        if "broiler_farms" not in st.session_state: st.session_state["broiler_farms"] = {}
        with st.expander("➕ إضافة مزرعة"):
            nf_name = st.text_input("اسم المزرعة:", key="nf_name")
            nf_owner = st.text_input("المالك:", key="nf_owner")
            nf_phone = st.text_input("واتساب:", WHATSAPP_NUMBER, key="nf_phone")
            if st.button("💾 حفظ") and nf_name:
                st.session_state["broiler_farms"][nf_name] = {"owner": nf_owner, "owner_phone": nf_phone, "data": {"age": 1, "birds": 1000, "weight_kg": 0.045, "feed_kg": 0.0, "dead": 0, "temp": 33.0, "hum": 65.0}}
                st.success(f"✅ تمت إضافة {nf_name}"); st.rerun()
        if st.session_state["broiler_farms"]:
            farms = list(st.session_state["broiler_farms"].keys())
            sel = st.selectbox("اختر مزرعة:", [""] + farms)
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input("العمر (يوم):", 1, 60, d["age"], key="bf_age")
                    d["birds"] = st.number_input("الطيور:", 1, value=d["birds"], key="bf_birds")
                    d["weight_kg"] = st.number_input("الوزن (كجم):", 0.0, 10.0, float(d["weight_kg"]), 0.01, key="bf_w")
                    d["feed_kg"] = st.number_input("العلف (كجم):", 0.0, float(d["feed_kg"]), 100.0, key="bf_f")
                with b2:
                    d["dead"] = st.number_input("النافق:", 0, value=d["dead"], key="bf_d")
                    d["temp"] = st.number_input("الحرارة:", 10.0, 45.0, float(d["temp"]), key="bf_t")
                    d["hum"] = st.number_input("الرطوبة:", 20.0, 90.0, float(d["hum"]), key="bf_h")
                alive = d["birds"] - d["dead"]
                gain = alive * (d["weight_kg"] - 0.045)
                adg = ((d["weight_kg"] - 0.045) * 1000 / d["age"] if d["age"] > 0 else 0)
                fcr = (d["feed_kg"] / gain) if gain > 0 else 0
                liv = 100 - (d["dead"] / d["birds"] * 100)
                epef = ((liv * d["weight_kg"]) / (d["age"] * fcr) * 100 if d["age"] > 0 and fcr > 0 else 0)
                k1, k2, k3 = st.columns(3)
                k1.metric("ADG (جم)", f"{adg:.1f}")
                k2.metric("FCR", f"{fcr:.2f}")
                k3.metric("EPEF", f"{epef:.0f}")

    with tabs[13]:
        st.markdown('<div class="section-title">💬 التعليقات</div>', unsafe_allow_html=True)
        if "shared_comments" not in st.session_state:
            st.session_state["shared_comments"] = f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n"
        st.text_area("الحالية:", value=st.session_state["shared_comments"], height=200, disabled=True)
        nc = st.text_area("جديد:")
        if st.button("➕ نشر") and nc:
            st.session_state["shared_comments"] += f"\n• [{user_name} - {datetime.now():%Y-%m-%d %H:%M}]: {nc}"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# المراجع + المساعدة + الدليل
# ═══════════════════════════════════════════════════════════════════════════

with tabs[tabs_titles.index("📚 المراجع")]:
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    st.markdown("""
    ### المراجع المعتمدة:
    - **NRC (2012)** — Nutrient Requirements of Swine
    - **NRC (2007)** — Nutrient Requirements of Small Ruminants
    - **NRC (2001)** — Nutrient Requirements of Dairy Cattle
    - **NRC (2007)** — Nutrient Requirements of Horses
    - **NRC (1994)** — Nutrient Requirements of Poultry
    - **INRA (2018)** — Feeding System for Ruminants
    - **FAO (2010)** — Camel Nutrition and Feeding
    - **Ross 308 (2020)** — Broiler Management Handbook
    - **McDonald et al. (2011)** — Animal Nutrition
    - **Van Soest (1994)** — Nutritional Ecology of the Ruminant
    """)

with tabs[tabs_titles.index("💡 المساعدة")]:
    st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
    st.markdown(f"""
    ### الأسئلة الشائعة:
    - **كيف أبدأ؟** اختر الدولة ثم الحيوان والحالة، فعّل ✅ الاعتماد
    - **التركيب الآلي 100%؟** يعتمد على مواد الدولة المختارة — استهدف مطابقة 100%
    - **مكتبة الأعلاف؟** تبويب 📚 يعرضها كجداول عادية
    - **ليبيا وندرة البروتين؟** النظام يستبعد الصويا تلقائياً ويستخدم بدائل متوفرة
    - **DP أم CP؟** اختر في الأعلى
    - **المختبر؟** تبويب 🧪 لتحليل الخلطات

    ### 🌍 الدول المدعومة (22 دولة):
    السودان، ليبيا، مصر، السعودية، الإمارات، الكويت، قطر، البحرين، عمان، اليمن، الأردن، لبنان، سوريا، العراق، فلسطين، الجزائر، المغرب، تونس، موريتانيا، الصومال، جيبوتي، جزر القمر

    ### 🔧 الدعم الفني
    📧 {OWNER_EMAIL}
    📱 {WHATSAPP_NUMBER}

    ### 🕌 دعاء
    {DUA_FULL}
    """)

with tabs[tabs_titles.index("📖 الدليل")]:
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    st.markdown(f"""
    ### الغرض
    **{APP_NAME}** — منصة ذكية لتركيب الأعلاف بأقل تكلفة وأعلى جودة، مع دعم 22 دولة عربية.

    ### ✨ الميزات الجديدة (v13.0):
    - 🌍 **22 دولة عربية** كل دولة بموادها المتوفرة وأسعار صرفها
    - 📚 **مكتبة أعلاف بجداول عادية** بدل الدوائر
    - 🎯 **التركيب الآلي 100%** عبر محرك SLSQP
    - 🧠 **ذكاء المحرك**: يستبعد الصويا في ليبيا ويستبدلها بمصادر بديلة

    ### 🤖 الفرق بين التركيب الآلي واليدوي:
    - **التركيب الآلي**: يستهدف مطابقة **100%** (SLSQP متعدد الجولات)
    - **التركيب اليدوي**: يصل عادة إلى **75%-99%** حسب المواد المختارة

    ### 🧠 كيف يعمل الذكاء حسب الدولة:
    1. النظام يعرف المواد المتوفرة في كل دولة
    2. عند اختيار ليبيا → يستبعد الصويا والأمباز والليسين
    3. يستبدلها تلقائياً بـ: عباد الشمس، الكانولا، بذور القطن، مسحوق الأسماك
    4. يكمل التركيب بدون أي نقص

    ### الميزات الرئيسية
    - 🐄 **8 قطاعات**: أبقار، أغنام، ماعز، إبل، خيول، دواجن، سمان، أسماك
    - 🧪 **المختبر**: تحليل الخلطات الجاهزة
    - 🌰 **15 زيتاً**: بمعايير NRC/INRA/FAO
    - 👥 **متعدد المستخدمين**: 500+ جلسة

    ### كود المالك
    `{OWNER_CODE}`
    """)


# ═══════════════════════════════════════════════════════════════════════════
# التذييل الثابت
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(f'<div class="mini-signature">🌾 {APP_NAME} v{APP_VERSION} | {SUPERVISOR} © 2026</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# نهاية الملف — End of File — v13.0
# ═══════════════════════════════════════════════════════════════════════════
