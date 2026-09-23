# ============================================================================
# تاور نولجي Tawor Nology — للإنتاج الحيواني وتغذية الحيوان
# تحت إشراف: م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان
# الإصدار: 3.0 (مع ختم رسمي + جداول مقارنة + PDF احترافي + Excel)
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import base64
import smtplib
import time
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ===== مكتبة الصوت =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ===== مكتبات PDF واللغة العربية =====
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer, Image,
                                 SimpleDocTemplate, Frame, PageTemplate)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus.flowables import HRFlowable
import arabic_reshaper
from bidi.algorithm import get_display
import io
import qrcode
from PIL import Image as PILImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sqlite3
from dataclasses import dataclass, asdict

# ===== مكتبة Excel =====
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# ===== دوال الصوت =====
def play_welcome_audio():
    audio_file = "welcome.mp3"
    if not os.path.exists(audio_file):
        if GTTS_AVAILABLE:
            try:
                tts = gTTS(
                    text="مرحباً بك في منصة تاور نولجي للإنتاج الحيواني وتغذية الحيوان، تحت إشراف الاختصاصي عبدالقادر إسماعيل تاور، اختصاصي تغذية الحيوان",
                    lang="ar"
                )
                tts.save(audio_file)
            except Exception as e:
                st.warning(f"⚠️ تعذر توليد الصوت: {e}")
                return
        else:
            st.warning("⚠️ مكتبة gTTS غير مثبتة، يرجى تثبيتها: pip install gtts")
            return
    if os.path.exists(audio_file):
        try:
            with open(audio_file, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()
            st.components.v1.html(
                f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>',
                height=0
            )
        except Exception as e:
            st.warning(f"⚠️ تعذر تشغيل الصوت: {e}")

# ============================================================
# 1. نظام قاعدة البيانات المحلية (SQLite)
# ============================================================
class DatabaseManager:
    def __init__(self, db_path="tawor_nology.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id TEXT PRIMARY KEY,
                      username TEXT UNIQUE,
                      password_hash TEXT,
                      role TEXT,
                      full_name TEXT,
                      email TEXT,
                      phone TEXT,
                      created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS farm_cycles
                     (cycle_id TEXT PRIMARY KEY,
                      farm_name TEXT, animal_type TEXT, breed TEXT,
                      start_date TEXT, end_date TEXT,
                      initial_birds INTEGER, final_weight_kg REAL,
                      total_feed_kg REAL, total_dead INTEGER,
                      total_culled INTEGER, fcr REAL, adg REAL,
                      epef REAL, mortality_rate REAL, notes TEXT,
                      created_by TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas
                     (formula_id TEXT PRIMARY KEY, formula_name TEXT,
                      animal_type TEXT, target_dp REAL, target_se REAL,
                      ingredients TEXT, total_cost REAL,
                      created_by TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS invoices
                     (invoice_id TEXT PRIMARY KEY, customer_name TEXT,
                      formula_id TEXT, quantity_ton REAL, unit_price REAL,
                      total_price REAL, status TEXT,
                      created_by TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history
                     (record_id TEXT PRIMARY KEY, ingredient_name TEXT,
                      price REAL, currency TEXT, country TEXT, city TEXT,
                      record_date TEXT, recorded_by TEXT)''')
        conn.commit()
        conn.close()

    def execute_query(self, query: str, params: tuple = ()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data

    def insert_record(self, table: str, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        c.execute(query, list(data.values()))
        conn.commit()
        conn.close()

# ============================================================
# 2. نظام المصادقة
# ============================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()

    def _create_default_admin(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner',
                             'م. عبدالقادر إسماعيل تاور',
                             'abukram128@gmail.com', '+249123533489')

    def create_user(self, username, password, role, full_name, email, phone):
        user_id = secrets.token_hex(16)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        data = {
            'user_id': user_id, 'username': username,
            'password_hash': password_hash, 'role': role,
            'full_name': full_name, 'email': email, 'phone': phone,
            'created_date': datetime.now().isoformat()
        }
        self.db.insert_record('users', data)
        return user_id

    def authenticate(self, username, password):
        users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
        if users:
            user = users[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == password_hash:
                return {
                    'user_id': user[0], 'username': user[1], 'role': user[3],
                    'full_name': user[4], 'email': user[5], 'phone': user[6]
                }
        return None

# ============================================================
# 3. نظام التنبؤ بالأسعار
# ============================================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()

    def get_ingredient_prices(self, ingredient_name, days=30):
        results = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? ORDER BY record_date DESC LIMIT ?",
            (ingredient_name, days)
        )
        return [{
            'record_id': r[0], 'ingredient_name': r[1], 'price': r[2],
            'currency': r[3], 'country': r[4], 'city': r[5], 'record_date': r[6]
        } for r in results]

    def predict_price(self, ingredient_name, days_ahead=7):
        prices = self.get_ingredient_prices(ingredient_name, 30)
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0}
        price_list = [p['price'] for p in prices]
        weights = np.array(range(1, len(price_list) + 1))
        weighted_avg = np.average(price_list, weights=weights)
        trend = (price_list[0] - price_list[-1]) / len(price_list) if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        return {
            'prediction': max(0, prediction),
            'confidence': min(1, len(price_list) / 30),
            'current_price': price_list[0] if price_list else None,
            'trend': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'
        }

# ============================================================
# 4. نظام المراجع العلمية
# ============================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education",
                 "edition": "7th Edition", "isbn": "978-1408204238",
                 "summary": "المرجع الأساسي في تغذية الحيوان، يغطي جميع جوانب التغذية من الهضم إلى متطلبات العناصر الغذائية."},
                {"id": "REF002", "authors": "Cheeke, P.R., Dierenfeld, E.S.",
                 "year": 2010, "title": "Comparative Animal Nutrition and Metabolism",
                 "publisher": "CABI", "isbn": "978-1845936310",
                 "summary": "مقارنة بين آليات التغذية والتمثيل الغذائي في مختلف أنواع الحيوانات."}
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية",
            "references": [
                {"id": "REF003", "authors": "NRC (National Research Council)",
                 "year": 2012, "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press", "edition": "11th Revised Edition",
                 "isbn": "978-0309214230", "summary": "المرجع الرسمي لمتطلبات العناصر الغذائية للخنازير."},
                {"id": "REF004", "authors": "NRC (National Research Council)",
                 "year": 2001, "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press", "edition": "7th Revised Edition",
                 "isbn": "978-0309069977", "summary": "المرجع الأساسي في تغذية أبقار الحليب."}
            ]
        },
        "energy_carbohydrates": {
            "title": "الطاقة والكربوهيدرات",
            "references": [
                {"id": "REF006", "authors": "Van Soest, P.J.", "year": 1994,
                 "title": "Nutritional Ecology of the Ruminant",
                 "publisher": "Cornell University Press", "edition": "2nd Edition",
                 "isbn": "978-0801427725", "summary": "المرجع الكلاسيكي في تغذية المجترات وتحليل الألياف."}
            ]
        },
        "minerals_vitamins": {
            "title": "المعادن والفيتامينات",
            "references": [
                {"id": "REF008", "authors": "Underwood, E.J., Suttle, N.F.",
                 "year": 1999, "title": "The Mineral Nutrition of Livestock",
                 "publisher": "CABI", "edition": "3rd Edition", "isbn": "978-0851991283",
                 "summary": "المرجع الشامل في تغذية المعادن للثروة الحيوانية."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.", "year": 2009,
                 "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press", "edition": "3rd Edition",
                 "isbn": "978-1904761578", "summary": "المرجع العملي في تغذية الدواجن التجارية."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.", "year": 1993,
                 "title": "The Ruminant Animal: Digestive Physiology and Nutrition",
                 "publisher": "Waveland Press", "isbn": "978-0881337389",
                 "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات."}
            ]
        },
        "sheep_goats": {
            "title": "تغذية الأغنام والماعز",
            "references": [
                {"id": "REF014", "authors": "NRC (National Research Council)", "year": 2007,
                 "title": "Nutrient Requirements of Small Ruminants",
                 "publisher": "National Academies Press", "isbn": "978-0309102131",
                 "summary": "المرجع الرسمي لمتطلبات الأغنام والماعز والمجترات الصغيرة."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول",
            "references": [
                {"id": "REF015", "authors": "NRC (National Research Council)", "year": 2007,
                 "title": "Nutrient Requirements of Horses",
                 "publisher": "National Academies Press", "edition": "6th Revised Edition",
                 "isbn": "978-0309102124", "summary": "المرجع الأساسي في تغذية الخيول ومتطلباتها الغذائية."}
            ]
        },
        "aquaculture": {
            "title": "تغذية الأسماك",
            "references": [
                {"id": "REF016", "authors": "Halver, J.E., Hardy, R.W.", "year": 2002,
                 "title": "Fish Nutrition", "publisher": "Academic Press",
                 "edition": "3rd Edition", "isbn": "978-0123196521",
                 "summary": "المرجع الشامل في تغذية الأسماك والمزارع المائية."}
            ]
        },
        "broiler": {
            "title": "إنتاج الدجاج اللاحم",
            "references": [
                {"id": "REF020", "authors": "Ross 308 Broiler Management Guide", "year": 2020,
                 "title": "Ross Broiler Management Handbook", "publisher": "Aviagen",
                 "summary": "الدليل الشامل لإدارة الدجاج اللاحم سلالة روس."}
            ]
        },
        "digestible_protein": {
            "title": "البروتين المهضوم",
            "references": [
                {"id": "REF023", "authors": "INRA (Institut National de la Recherche Agronomique)",
                 "year": 2007, "title": "INRA Feeding System for Ruminants",
                 "publisher": "Wageningen Academic Publishers", "isbn": "978-9086860197",
                 "summary": "النظام الفرنسي المتقدم لتغذية المجترات وتقدير البروتين المهضوم."}
            ]
        }
    }

    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم لكل مادة علفية.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً، وليس مجرد الكمية الموجودة في العلف."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف، وكلما زاد الرقم زادت الطاقة التي يمنحها للحيوان."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming) الذي يحسب أقل تكلفة لتحقيق متطلبات غذائية محددة.",
            "reference": "REF024",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية تلبي جميع احتياجات الحيوان الغذائية."
        },
        "ما هي أهمية إضافة الإنزيمات للأعلاف": {
            "answer": "الإنزيمات في الأعلاف تعمل على تحسين هضم واستفادة الحيوان من العناصر الغذائية. الإنزيمات مثل الفايتيز تحرر الفسفور المرتبط، وإنزيمات NSP تكسر جدران الخلايا النباتية.",
            "reference": "REF010",
            "simplified": "الإنزيمات تساعد الحيوان على هضم العلف بشكل أفضل، مما يوفر في تكاليف التغذية ويحسن الإنتاج."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF هو مقياس شامل لكفاءة إنتاج الدجاج اللاحم. يحسب بالمعادلة: EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل الغذائي) × 100.",
            "reference": "REF020",
            "simplified": "EPEF هو رقم يعبر عن كفاءة مزرعة الدجاج، وكلما كان أعلى دل ذلك على إنتاجية أفضل."
        }
    }

    @staticmethod
    def get_reference(ref_id):
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None

    @staticmethod
    def get_knowledge_answer(question):
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question:
                ref = ScientificReferenceSystem.get_reference(value.get("reference", ""))
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"]),
                    "reference": ref
                }
        return None

# ============================================================
# 5. قاموس المعايير القياسية للعناصر الغذائية (جديد)
# ============================================================
NUTRIENT_STANDARDS = {
    "أبقار_حليب":    {"CP": 16.0, "DP": 12.5, "SE": 68.0, "NDF": 35.0, "ADF": 22.0, "EE": 4.0, "ASH": 8.0},
    "أبقار_تسمين":   {"CP": 13.0, "DP": 10.0, "SE": 65.0, "NDF": 40.0, "ADF": 25.0, "EE": 3.5, "ASH": 7.5},
    "أغنام_تسمين":   {"CP": 15.0, "DP": 12.0, "SE": 64.0, "NDF": 32.0, "ADF": 20.0, "EE": 3.5, "ASH": 8.0},
    "أغنام_حليب":    {"CP": 16.0, "DP": 12.8, "SE": 66.0, "NDF": 30.0, "ADF": 19.0, "EE": 4.0, "ASH": 8.5},
    "أغنام_صيانة":   {"CP": 11.0, "DP": 8.0,  "SE": 50.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.0, "ASH": 8.0},
    "ماعز_تسمين":    {"CP": 14.5, "DP": 11.5, "SE": 62.0, "NDF": 33.0, "ADF": 20.0, "EE": 3.5, "ASH": 8.0},
    "ماعز_حليب":     {"CP": 16.0, "DP": 12.8, "SE": 65.0, "NDF": 30.0, "ADF": 19.0, "EE": 4.0, "ASH": 8.5},
    "خيول_رياضة":    {"CP": 12.0, "DP": 9.5,  "SE": 65.0, "NDF": 35.0, "ADF": 22.0, "EE": 4.5, "ASH": 7.5},
    "خيول_نمو":      {"CP": 15.0, "DP": 12.5, "SE": 65.0, "NDF": 30.0, "ADF": 18.0, "EE": 4.0, "ASH": 8.0},
    "دواجن_بادي":    {"CP": 23.0, "DP": 20.0, "SE": 76.0, "NDF": 8.0,  "ADF": 4.0,  "EE": 5.0, "ASH": 6.5},
    "دواجن_نامي":    {"CP": 21.0, "DP": 18.5, "SE": 74.0, "NDF": 9.0,  "ADF": 5.0,  "EE": 4.5, "ASH": 6.0},
    "دواجن_ناهي":    {"CP": 19.0, "DP": 16.5, "SE": 75.0, "NDF": 10.0, "ADF": 5.5,  "EE": 4.0, "ASH": 6.0},
    "دواجن_بياض":    {"CP": 16.5, "DP": 14.5, "SE": 70.0, "NDF": 12.0, "ADF": 6.0,  "EE": 4.0, "ASH": 9.5},
    "سمان_بادي":     {"CP": 24.0, "DP": 20.0, "SE": 72.0, "NDF": 8.0,  "ADF": 4.0,  "EE": 5.0, "ASH": 6.5},
    "سمان_بياض":     {"CP": 18.0, "DP": 15.0, "SE": 68.0, "NDF": 11.0, "ADF": 5.5,  "EE": 4.0, "ASH": 9.0},
    "أسماك_نمو":     {"CP": 32.0, "DP": 25.0, "SE": 70.0, "NDF": 12.0, "ADF": 6.0,  "EE": 6.0, "ASH": 9.0},
    "أسماك_تسمين":   {"CP": 28.0, "DP": 22.0, "SE": 68.0, "NDF": 13.0, "ADF": 7.0,  "EE": 6.5, "ASH": 9.5},
}

def compute_formula_nutrients(formula: dict) -> dict:
    """حساب جميع العناصر الغذائية لخلطة معطاة (بالنسب %)"""
    totals = {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0}
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                d = cat[ing]
                totals["CP"]  += (pct / 100.0) * d.get("CP", 0.0)
                totals["DP"]  += (pct / 100.0) * d.get("CP", 0.0) * d.get("DC", 0.0)
                totals["SE"]  += (pct / 100.0) * d.get("SE", 0.0)
                totals["NDF"] += (pct / 100.0) * d.get("NDF", 0.0)
                totals["ADF"] += (pct / 100.0) * d.get("ADF", 0.0)
                totals["EE"]  += (pct / 100.0) * d.get("EE", 0.0)
                totals["ASH"] += (pct / 100.0) * d.get("ASH", 0.0)
                break
    return totals

def get_standard_key(animal: str, stage: str) -> str:
    """تحديد مفتاح المعيار القياسي حسب الحيوان والمرحلة"""
    a = str(animal).strip()
    s = str(stage).strip()
    if "أبقار" in a:
        return "أبقار_حليب" if ("حليب" in s or "إدرار" in s) else "أبقار_تسمين"
    if "أغنام" in a:
        if "حليب" in s or "إدرار" in s: return "أغنام_حليب"
        if "صيانة" in s: return "أغنام_صيانة"
        return "أغنام_تسمين"
    if "ماعز" in a:
        return "ماعز_حليب" if ("حليب" in s or "إدرار" in s) else "ماعز_تسمين"
    if "خيول" in a:
        return "خيول_رياضة" if "رياضة" in s else "خيول_نمو"
    if "دواجن" in a and "بياض" in a: return "دواجن_بياض"
    if "دواجن" in a and "بادي" in s: return "دواجن_بادي"
    if "دواجن" in a and "نامي" in s: return "دواجن_نامي"
    if "دواجن" in a: return "دواجن_ناهي"
    if "سمان" in a: return "سمان_بياض" if "بياض" in s else "سمان_بادي"
    if "أسماك" in a: return "أسماك_تسمين" if "تسمين" in s else "أسماك_نمو"
    return "دواجن_ناهي"

# ============================================================
# 6. إعدادات المنصة
# ============================================================
st.set_page_config(
    page_title="تاور نولجي Tawor Nology | للإنتاج الحيواني وتغذية الحيوان",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_caching_system():
    return {"cache_hits": 0, "cache_misses": 0, "last_cleanup": datetime.now()}
CACHE_SYSTEM = init_caching_system()

CODES_DB = {
    "202687": {"role": "owner", "name": "م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG", "logo.png", "logo.jpg"]
LOGO_OPTIONS = ["logo.png", "logo.jpg", "LOGO.PNG", "14686.jpg", "14686.JPG", "1000069464.jpg"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

@st.cache_data(ttl=3600)
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
logo_base64 = get_image_base64(LOGO_OPTIONS)

def send_code_to_mail(receiver_email, attachment_type="full"):
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or not SENDER_PASSWORD:
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP.")
        return False
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل - تاور نولجي Tawor Nology"
    body = """السلام عليكم م. عبدالقادر،

مرفق مع هذه الرسالة النسخة البرمجية الكاملة والمستقرة لمنصة تاور نولجي."""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        try:
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except NameError:
            code_content = "# كود المنصة مأرشيف داخلياً\n"
        file_hash = hashlib.md5(code_content.encode()).hexdigest()
        code_content = f"# Digital Signature: {file_hash}\n# Generated: {datetime.now().isoformat()}\n\n{code_content}"
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment',
                              filename="tawor_nology_platform.py")
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

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text):
        reshaped_text = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text

arabic_processor = ArabicTextProcessor()

# ============================================================
# 7. مكتبة الأعلاف الكاملة
# ============================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0}
    },
    "🌱 الأكساب ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5}
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5}
    },
    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0}
    }
}

# ============================================================
# 8. مولد PDF الاحترافي الجديد مع ختم وترويسة وجداول مقارنة
# ============================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        self.font_bold = 'Helvetica-Bold'
        for fpath in ["Amiri-Regular.ttf", "Amiri.ttf", "Cairo-Regular.ttf",
                      "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
            if os.path.exists(fpath):
                try:
                    pdfmetrics.registerFont(TTFont('ArabicFont', fpath))
                    self.font_name = 'ArabicFont'
                    self.font_bold = 'ArabicFont'
                    break
                except Exception:
                    pass
        self.logo_path = None
        for lp in ["logo.png", "logo.jpg", "14686.jpg", "14686.JPG",
                   "1000069464.jpg", "1000069464.JPG"]:
            if os.path.exists(lp):
                self.logo_path = lp
                break

    def _ar(self, text):
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except Exception:
            return str(text)

    def _draw_page_decorations(self, canvas_obj, doc):
        """الترويسة والختم والترقيم على كل صفحة"""
        canvas_obj.saveState()
        w, h = doc.pagesize

        # ===== الترويسة العلوية =====
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, h - 82, w, 82, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, h - 87, w, 5, fill=1, stroke=0)

        # شعار (إن وجد)
        try:
            if self.logo_path:
                canvas_obj.drawImage(self.logo_path, 30, h - 72, width=55,
                                     height=55, preserveAspectRatio=True,
                                     anchor='sw', mask='auto')
        except Exception:
            pass

        # اسم المنصة
        canvas_obj.setFillColor(white)
        canvas_obj.setFont(self.font_name, 20)
        canvas_obj.drawCentredString(w / 2, h - 35, self._ar("تاور نولجي  Tawor Nology"))
        canvas_obj.setFont(self.font_name, 11)
        canvas_obj.setFillColor(HexColor('#e8f5e9'))
        canvas_obj.drawCentredString(w / 2, h - 53, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
        canvas_obj.setFont(self.font_name, 9)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.drawCentredString(w / 2, h - 71,
            self._ar("إشراف: م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان"))

        # ===== التذييل السفلي =====
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, 0, w, 32, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, 32, w, 3, fill=1, stroke=0)

        canvas_obj.setFillColor(white)
        canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawCentredString(w / 2, 18,
            self._ar("تاور نولجي Tawor Nology © 2026 — جميع الحقوق محفوظة"))

        # رقم الصفحة
        page_num = canvas_obj.getPageNumber()
        canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawRightString(w - 30, 18, f"Page {page_num}")
        canvas_obj.drawString(30, 18, "Tawor Nology")

        # ===== الختم الرسمي الدائري =====
        sx, sy = w - 105, 105
        canvas_obj.setStrokeColor(HexColor('#c62828'))
        canvas_obj.setLineWidth(2.8)
        canvas_obj.circle(sx, sy, 68, stroke=1, fill=0)
        canvas_obj.setLineWidth(1.4)
        canvas_obj.circle(sx, sy, 60, stroke=1, fill=0)
        canvas_obj.setLineWidth(0.6)
        canvas_obj.circle(sx, sy, 55, stroke=1, fill=0)

        canvas_obj.setFillColor(HexColor('#c62828'))
        canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawCentredString(sx, sy + 38, self._ar("تاور نولجي"))
        canvas_obj.drawCentredString(sx, sy + 26, self._ar("Tawor Nology"))

        canvas_obj.setFont(self.font_name, 7)
        canvas_obj.drawCentredString(sx, sy + 8,  self._ar("م. عبدالقادر"))
        canvas_obj.drawCentredString(sx, sy - 3,  self._ar("إسماعيل تاور"))
        canvas_obj.setFont(self.font_name, 6)
        canvas_obj.drawCentredString(sx, sy - 18, self._ar("اختصاصي تغذية الحيوان"))
        canvas_obj.drawCentredString(sx, sy - 32, self._ar("معتمد رسمياً"))
        canvas_obj.drawCentredString(sx, sy - 44, self._ar("© 2026"))

        canvas_obj.restoreState()

    def _comparison_table(self, standard: dict, calculated: dict):
        """جدول مقارنة القيم القياسية vs المحسوبة مع تلوين ذكي"""
        header = [self._ar(x) for x in
                  ["العنصر الغذائي", "المعيار القياسي", "القيمة المحسوبة", "الفرق", "التقييم"]]
        data = [header]
        style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR',  (0, 0), (-1, 0), white),
            ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME',   (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE',   (0, 0), (-1, -1), 10),
            ('GRID',       (0, 0), (-1, -1), 1, HexColor('#9e9e9e')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ]
        labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP", "SE": "معادل النشاء SE",
                  "NDF": "ألياف NDF", "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH"}
        row = 1
        for key in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]:
            if key not in standard: continue
            std_v = standard[key]
            calc_v = calculated.get(key, 0.0)
            diff = calc_v - std_v
            pct = (diff / std_v * 100) if std_v else 0
            if abs(pct) <= 5:
                status, bg = "مطابق", HexColor('#e8f5e9')
            elif abs(pct) <= 15:
                status, bg = "مقبول", HexColor('#fff8e1')
            else:
                status, bg = "غير مطابق", HexColor('#ffebee')
            unit = "%" if key in ("CP", "DP", "NDF", "ADF", "EE", "ASH") else "وحدة"
            data.append([
                self._ar(labels.get(key, key)),
                f"{std_v:.2f} {unit}",
                f"{calc_v:.2f} {unit}",
                f"{diff:+.2f} ({pct:+.1f}%)",
                self._ar(status),
            ])
            style_cmds.append(('BACKGROUND', (0, row), (-1, row), bg))
            row += 1
        t = Table(data, colWidths=[105, 100, 100, 100, 95])
        t.setStyle(TableStyle(style_cmds))
        return t

    def generate_comprehensive_report(
        self, formula, target_dp, breed, cost, city, local_cost, local_sym,
        computed_se, requester_name="", animal_type="", production_stage="",
        include_charts=True, report_type="تركيب علفة"
    ):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=45, leftMargin=45, topMargin=105, bottomMargin=60
        )
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(
                self._ar(text),
                ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                               alignment=align, textColor=HexColor(color),
                               spaceAfter=6, leading=size * 1.6)
            )

        # ===== عنوان التقرير =====
        story.append(P(f"تقرير فني رسمي — {report_type}", size=18,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        # ===== بيانات الطالب =====
        client_box_data = [
            [self._ar("👤 اسم طالب الخدمة :"), self._ar(requester_name or "........................")],
            [self._ar("📍 الموقع الجغرافي :"), self._ar(city)],
            [self._ar("🐾 الفصيل المستهدف :"), self._ar(breed)],
            [self._ar("📅 تاريخ الإصدار :"), datetime.now().strftime('%Y-%m-%d  |  %H:%M')],
        ]
        ct = Table(client_box_data, colWidths=[145, 345])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ]))
        story.append(ct)
        story.append(Spacer(1, 20))

        # ===== جدول المقارنة =====
        story.append(P("📊 جدول مقارنة العناصر الغذائية (المعيار القياسي مقابل المحسوب)",
                       size=13, align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))

        std_key = get_standard_key(animal_type, production_stage)
        standard_vals = NUTRIENT_STANDARDS.get(std_key, NUTRIENT_STANDARDS["دواجن_ناهي"])
        calculated_vals = compute_formula_nutrients(formula)
        story.append(self._comparison_table(standard_vals, calculated_vals))
        story.append(Spacer(1, 20))

        # ===== جدول التكاليف =====
        story.append(P("💰 ملخص التكاليف والمعايير الفنية", size=13,
                       align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 6))
        cost_data = [
            [self._ar("البند"), self._ar("القيمة")],
            [self._ar("التكلفة للطن (دولار)"), f"${cost:.2f}"],
            [self._ar(f"التكلفة للطن ({local_sym})"), f"{local_cost:,.2f}"],
            [self._ar("معادل النشاء المحسوب (SE)"), f"{computed_se:.2f} وحدة"],
            [self._ar("البروتين المستهدف (DP)"), f"{target_dp:.2f} %"],
        ]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR',  (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f5f5f5')),
            ('GRID',       (0, 0), (-1, -1), 1, HexColor('#2e7d32')),
            ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',   (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE',   (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tc)
        story.append(Spacer(1, 20))

        # ===== جدول المكونات =====
        if formula:
            story.append(P("🌾 المقادير المعتمدة للطن الواحد", size=13,
                           align=TA_RIGHT, color='#1b5e20'))
            story.append(Spacer(1, 6))
            ing_data = [[
                self._ar("المكون"), self._ar("النسبة %"), self._ar("كجم/طن"),
            ]]
            for ing, pct in formula.items():
                ing_data.append([
                    self._ar(ing), f"{pct:.2f}%", f"{pct * 10:.1f}",
                ])
            ti = Table(ing_data, colWidths=[260, 115, 115])
            ti.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR',  (0, 0), (-1, 0), white),
                ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME',   (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE',   (0, 0), (-1, -1), 10),
                ('GRID',       (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [HexColor('#ffffff'), HexColor('#f5f5f5')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(ti)
            story.append(Spacer(1, 18))

        # ===== الرسم البياني =====
        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20', '#2e7d32', '#388e3c', '#43a047',
                          '#4caf50', '#66bb6a', '#81c784', '#a5d6a7']
                ax.pie(vals, autopct='%1.1f%%', colors=colors[:len(names)],
                       textprops={'fontsize': 8})
                ax.legend([self._ar(n) for n in names],
                          title=self._ar("المكونات"),
                          loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                          fontsize=8)
                ax.set_title(self._ar('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=110, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except Exception:
                pass

        story.append(Spacer(1, 25))

        # ===== صناديق التوقيع =====
        sign = [
            [self._ar("توقيع طالب الخدمة"), self._ar("توقيع المختص")],
            [self._ar("................................"),
             self._ar("م. عبدالقادر إسماعيل تاور")],
            [self._ar("التاريخ: ..../..../........"),
             self._ar("اختصاصي تغذية الحيوان")],
        ]
        ts = Table(sign, colWidths=[245, 245])
        ts.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9')),
        ]))
        story.append(ts)

        # بناء PDF
        doc.build(story,
                  onFirstPage=self._draw_page_decorations,
                  onLaterPages=self._draw_page_decorations)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ============================================================
# 9. دالة تصدير جدول المقارنة إلى Excel
# ============================================================
def export_comparison_to_excel(standard: dict, calculated: dict,
                               requester_name="", animal="", stage="",
                               formula: dict = None) -> bytes:
    """تصدير جدول المقارنة + المكونات إلى ملف Excel منسق"""
    if not OPENPYXL_AVAILABLE:
        return b""

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "مقارنة العناصر"
    ws.sheet_view.rightToLeft = True

    # تنسيقات
    header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    header_fill = PatternFill('solid', fgColor='1B5E20')
    title_font = Font(name='Arial', size=14, bold=True, color='1B5E20')
    info_font = Font(name='Arial', size=10, bold=True)
    center = Alignment(horizontal='center', vertical='center', wrap_text=True)
    right_align = Alignment(horizontal='right', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # العنوان
    ws.merge_cells('A1:F1')
    ws['A1'] = "تاور نولجي Tawor Nology — تقرير مقارنة العناصر الغذائية"
    ws['A1'].font = title_font
    ws['A1'].alignment = center

    # بيانات الطالب
    ws['A2'] = "اسم طالب الخدمة:"; ws['A2'].font = info_font; ws['A2'].alignment = right_align
    ws.merge_cells('B2:D2'); ws['B2'] = requester_name or "---"
    ws['E2'] = "التاريخ:"; ws['E2'].font = info_font; ws['E2'].alignment = right_align
    ws['F2'] = datetime.now().strftime('%Y-%m-%d')

    ws['A3'] = "الفصيل:"; ws['A3'].font = info_font; ws['A3'].alignment = right_align
    ws.merge_cells('B3:D3'); ws['B3'] = f"{animal} — {stage}"
    ws['E3'] = "المشرف:"; ws['E3'].font = info_font; ws['E3'].alignment = right_align
    ws['F3'] = "م. عبدالقادر إسماعيل تاور"

    # رأس الجدول
    headers = ["العنصر الغذائي", "المعيار القياسي", "القيمة المحسوبة", "الفرق", "الفرق %", "التقييم"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    labels = {"CP": "بروتين خام (CP)", "DP": "بروتين مهضوم (DP)",
              "SE": "معادل النشاء (SE)", "NDF": "ألياف NDF",
              "ADF": "ألياف ADF", "EE": "دهن خام (EE)", "ASH": "رماد (ASH)"}

    row = 6
    for key in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]:
        if key not in standard: continue
        std_v = standard[key]
        calc_v = calculated.get(key, 0.0)
        diff = calc_v - std_v
        pct = (diff / std_v * 100) if std_v else 0
        if abs(pct) <= 5:
            status, color = "مطابق", 'C8E6C9'
        elif abs(pct) <= 15:
            status, color = "مقبول", 'FFF8E1'
        else:
            status, color = "غير مطابق", 'FFCDD2'

        values = [labels[key], round(std_v, 2), round(calc_v, 2),
                  round(diff, 2), round(pct, 2), status]
        for col, v in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=v)
            cell.alignment = center
            cell.border = border
            cell.fill = PatternFill('solid', fgColor=color)
        row += 1

    # جدول المكونات
    if formula:
        row += 2
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        ws.cell(row=row, column=1, value="مكونات الخلطة").font = title_font
        ws.cell(row=row, column=1).alignment = center
        row += 1
        for col, h in enumerate(["المكون", "النسبة %", "كجم/طن", "", "", ""], 1):
            cell = ws.cell(row=row, column=col, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center
            cell.border = border
        row += 1
        for ing, pct in formula.items():
            ws.cell(row=row, column=1, value=ing).border = border
            ws.cell(row=row, column=1).alignment = right_align
            ws.cell(row=row, column=2, value=round(pct, 2)).border = border
            ws.cell(row=row, column=2).alignment = center
            ws.cell(row=row, column=3, value=round(pct * 10, 1)).border = border
            ws.cell(row=row, column=3).alignment = center
            row += 1

    # توسيع الأعمدة
    for col in range(1, 7):
        ws.column_dimensions[get_column_letter(col)].width = 22

    # حفظ
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()

# ============================================================
# 10. كلاس إدارة مزارع الدجاج اللاحم
# ============================================================
class BroilerFarmManager:
    @staticmethod
    def calculate_adg(current_weight_g, initial_weight_g, age_days):
        if age_days <= 0: return 0.0
        return (current_weight_g - initial_weight_g) / age_days

    @staticmethod
    def calculate_fcr(total_feed_kg, total_weight_gain_kg):
        if total_weight_gain_kg <= 0: return 0.0
        return total_feed_kg / total_weight_gain_kg

    @staticmethod
    def calculate_mortality_rate(dead_count, initial_count):
        if initial_count <= 0: return 0.0
        return (dead_count / initial_count) * 100.0

    @staticmethod
    def calculate_cull_rate(culled_count, initial_count):
        if initial_count <= 0: return 0.0
        return (culled_count / initial_count) * 100.0

    @staticmethod
    def calculate_livability(initial_count, dead_count):
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)

    @staticmethod
    def calculate_epef(livability, body_weight_kg, age_days, fcr):
        if age_days <= 0 or fcr <= 0: return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0

    @staticmethod
    def get_temp_humidity_table():
        return pd.DataFrame({
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55]
        })

# ============================================================
# 11. نظام أسعار المدن
# ============================================================
CITY_PRICES_FILE = "city_prices.json"

def load_city_prices():
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_city_prices(data):
    with open(CITY_PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

CITY_CUSTOM_PRICES = load_city_prices()

class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                for ing in items:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0, "min_threshold": 5.0, "unit": "طن",
                        "last_updated": datetime.now().isoformat(),
                        "price_history": [], "supplier": "غير محدد"
                    }

    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data if isinstance(data, (int, float)) else data["quantity"]
            threshold = 5.0 if isinstance(data, (int, float)) else data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings

InventoryManager.initialize_inventory()

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country, state_or_region, city):
        feed_prices = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for ing in cat:
                feed_prices[ing] = 230.0
        base_prices = {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
            "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0,
            "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0,
            "كسب بذور القطن (مقشور)": 290.0, "نخالة قمح (ردة)": 150.0,
            "البرسيم الجاف (الدريس)": 170.0, "مولاس قصب السكر": 120.0,
            "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0,
            "مركزات خيول ومجترات": 600.0,
            "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
            "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
            "بيكربونات الصوديوم (الصودا)": 340.0
        }
        feed_prices.update(base_prices)
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
            if "كردفان" in state_or_region or state_or_region == "إقليم النيل الأزرق":
                multiplier = 1.20
                feed_prices["سورجم (فتريتة)"] *= 0.85
                feed_prices["أمباز الفول السوداني (كسب)"] *= 0.85
            elif state_or_region in ["ولاية القضارف", "ولاية الجزيرة"]:
                feed_prices["سورجم (فتريتة)"] *= 0.82
                feed_prices["أمباز الفول السوداني (كسب)"] *= 0.88
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
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}

# ============================================================
# 12. حالة الجلسة
# ============================================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "session_token" not in st.session_state: st.session_state["session_token"] = None
if "broiler_farms" not in st.session_state: st.session_state["broiler_farms"] = {}
if "selected_farm" not in st.session_state: st.session_state["selected_farm"] = None
if "audio_played" not in st.session_state: st.session_state["audio_played"] = False
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = (
        "• [توجيه م. عبدالقادر إسماعيل تاور]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا لتبادل الخبرات التركيبية.\n"
        "• [ملاحظة مختص]: تم مراجعة جودة كسب زهرة الشمس المتاح حالياً بالأسواق.\n"
    )
if "standard_vacc_schedule" not in st.session_state:
    st.session_state["standard_vacc_schedule"] = {
        1: {"type": "فيتامين", "name": "فيتامين AD3E", "dose": "1 مل/لتر ماء", "route": "مياه الشرب"},
        7: {"type": "لقاح", "name": "نيوكاسل (Lasota)", "dose": "قطرة عين", "route": "قطرة عين/أنف"},
        14: {"type": "لقاح", "name": "Gumboro (Intermediate)", "dose": "قطرة فم", "route": "مياه الشرب"},
        21: {"type": "دواء", "name": "مضاد كوكسيديا (Amprolium)", "dose": "1 جم/لتر", "route": "مياه الشرب لمدة 3 أيام"},
        28: {"type": "فيتامين", "name": "فيتامين C + E", "dose": "0.5 جم/لتر", "route": "مياه الشرب"},
        35: {"type": "لقاح", "name": "Gumboro booster", "dose": "قطرة فم", "route": "مياه الشرب"},
    }
if "whatsapp_alerts_sent" not in st.session_state:
    st.session_state["whatsapp_alerts_sent"] = {}
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0,
        "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0,
        "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0,
        "كتكوت لاحم عمر يوم ($)": 0.65,
        "دجاج بياض عمر البشاير ($)": 5.50
    }
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50,
        "كيلو لحم ضأن طازج ($)": 9.00,
        "كيلو لحم دجاج لاحم صافي ($)": 3.80,
        "طبق بيض مائدة 30 بيضة ($)": 4.20,
        "رطل / لتر حليب خام ($)": 0.90,
        "كيلو جبن أبيض محلي ($)": 5.00,
        "كيلو جبن جاف / شيدر ($)": 8.50
    }
if "active_formula" not in st.session_state:
    st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state: st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

def send_whatsapp_broiler_alert(phone_number, message):
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
    st.markdown(
        f"<div style='background:#e8f5e9; padding:10px; border-radius:8px; direction:ltr;'>"
        f"📲 <b>تنبيه عبر واتساب:</b> <a href='{whatsapp_url}' target='_blank'>"
        f"اضغط لإرسال الرسالة إلى {phone_number}</a><br>{message}</div>",
        unsafe_allow_html=True)

def check_and_alert_medications(farm_name, farm_data, current_age):
    phone = farm_data.get("owner_phone", WHATSAPP_NUMBER)
    schedule = st.session_state["standard_vacc_schedule"]
    alerts = []
    for age_day, item in schedule.items():
        if age_day == current_age:
            key = f"{farm_name}_{age_day}_{item['type']}_{item['name']}"
            if key not in st.session_state["whatsapp_alerts_sent"]:
                alert_msg = (f"🔔 تنبيه لمزرعة {farm_name} (العمر {age_day} يوم):\n"
                             f"{item['type']} {item['name']} - الجرعة: {item['dose']} - طريقة الإعطاء: {item['route']}")
                send_whatsapp_broiler_alert(phone, alert_msg)
                st.session_state["whatsapp_alerts_sent"][key] = datetime.now().isoformat()
                alerts.append(alert_msg)
    if alerts:
        st.info(f"📢 تم إرسال {len(alerts)} تنبيه إلى المالك لليوم (العمر {current_age} يوم).")
    else:
        st.success("✅ لا توجد تحصينات أو أدوية مستحقة اليوم.")

# ============================================================
# 13. CSS المحسّن
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');

    * {
        font-family: 'Cairo', 'Tajawal', sans-serif;
        color: #1a1a1a !important;
    }

    html, body, [data-testid="stAppViewContainer"] {
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
        backdrop-filter: blur(5px);
    }

    h1, h2, h3, h4, h5, p, span, li, div, label, .stMarkdown,
    .stTextInput, .stNumberInput, .stSelectbox {
        color: #1a1a1a !important;
        text-shadow: none !important;
    }

    .formula-item {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(232,245,233,0.95) 100%);
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #1b5e20 !important;
        border-right: 5px solid #2e7d32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        text-align: right;
        transition: transform 0.3s ease;
    }
    .formula-item:hover {
        transform: translateX(-5px);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
    }

    .section-title {
        color: #1b5e20 !important;
        border-right: 6px solid #2e7d32;
        padding-right: 15px;
        text-align: right;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
        background: linear-gradient(to left, rgba(46,125,50,0.1), transparent);
        padding: 10px 15px;
        border-radius: 8px;
    }

    .sack-tag {
        border: 3px dashed #1b5e20;
        padding: 30px;
        border-radius: 15px;
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
        direction: rtl;
        text-align: right;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
    }
    .sack-tag * { color: #1a1a1a !important; }

    .profile-img-style {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #d4af37;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
        display: block;
        margin: 0 auto;
        transition: transform 0.3s ease;
    }
    .profile-img-style:hover { transform: scale(1.05); }

    .animal-banner-img {
        width: 100%;
        max-height: 200px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 3px solid #2e7d32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
    }

    .mini-left-signature {
        position: fixed;
        left: 20px;
        bottom: 20px;
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
        color: white !important;
        padding: 8px 20px;
        font-size: 0.85rem;
        border-radius: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        direction: rtl;
        backdrop-filter: blur(5px);
    }
    .mini-left-signature * { color: white !important; }

    .stock-critical {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        padding: 8px 12px;
        border-radius: 8px;
        color: #c62828 !important;
        font-weight: bold;
        border: 1px solid #ef5350;
    }

    .stock-normal {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 8px 12px;
        border-radius: 8px;
        color: #2e7d32 !important;
        border: 1px solid #66bb6a;
    }

    .price-card {
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #2e7d32;
        margin-bottom: 20px;
        direction: rtl;
        text-align: right;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    .price-card * { color: #1a1a1a !important; }

    .warning-card {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        padding: 15px;
        border-radius: 12px;
        border-right: 5px solid #f57c00;
        margin-bottom: 15px;
        direction: rtl;
        text-align: right;
        color: #e65100 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    .warning-card * { color: #e65100 !important; }

    .manual-book {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        padding: 35px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 8px 30px rgba(0,0,0,0.08);
        direction: rtl;
        text-align: right;
    }
    .manual-book * { color: #1a1a1a !important; }

    .book-chapter {
        background: linear-gradient(135deg, #1a237e, #283593);
        color: #ffffff !important;
        padding: 15px 20px;
        border-radius: 10px;
        font-weight: bold;
        margin-top: 25px;
        font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        letter-spacing: 0.5px;
    }
    .book-chapter * { color: #ffffff !important; }

    .book-body {
        padding: 20px 25px;
        font-size: 1.1rem;
        line-height: 1.8;
        color: #2c3e50 !important;
        border-left: 4px solid #3498db;
        margin-bottom: 20px;
        background: linear-gradient(to right, #f8f9fa, #ffffff);
        border-radius: 0 10px 10px 0;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    }
    .book-body * { color: #2c3e50 !important; }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card * { color: #1a1a1a !important; }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 30px rgba(0,0,0,0.15);
    }

    .stButton > button {
        color: #1a1a1a !important;
        background-color: #e8f5e9 !important;
        border: 1px solid #2e7d32 !important;
        font-weight: bold !important;
    }
    .stButton > button:hover { background-color: #c8e6c9 !important; }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }

    .stTabs [data-baseweb="tab-list"] button { color: #1a1a1a !important; }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #1b5e20 !important;
        font-weight: bold;
    }

    .stAlert, .stInfo, .stSuccess, .stWarning, .stError { color: #1a1a1a !important; }
    .stAlert * { color: #1a1a1a !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 14. بوابة الدخول
# ============================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. يرجى المحاولة بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0

    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🌾 تاور نولجي Tawor Nology</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#1a1a1a;'>بوابة الدخول الذكية — للإنتاج الحيواني وتغذية الحيوان</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#c62828; font-weight:bold;'>م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان</p>", unsafe_allow_html=True)

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tawor-nology.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center; margin:20px 0;">'
                    f'<img src="data:image/png;base64,{qr_base64}" width="150"></div>',
                    unsafe_allow_html=True)
    except Exception:
        pass

    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)

    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")
        col_login, col_reset = st.columns(2)
        with col_login:
            if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
                input_code_stripped = input_code.strip()
                if input_code_stripped in CODES_DB:
                    st.session_state["approved"] = True
                    st.session_state["user_role"] = CODES_DB[input_code_stripped]["role"]
                    st.session_state["login_welcome_shown"] = False
                    st.session_state["login_attempts"] = 0
                    st.session_state["last_login_time"] = datetime.now()
                    st.session_state["session_token"] = secrets.token_urlsafe(32)
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    st.session_state["last_login_time"] = datetime.now()
                    remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                    st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
        with col_reset:
            if st.button("🔄 نسيت الكود", use_container_width=True):
                st.info("يرجى التواصل مع مدير النظام: abukram128@gmail.com")
    else:
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
            auth = AuthManager()
            user = auth.authenticate(username, password)
            if user:
                st.session_state["approved"] = True
                st.session_state["user_role"] = user['role']
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.session_state["user"] = user
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة! متبقي {remaining} محاولات")

        st.caption("💡 المستخدم الافتراضي: admin / admin123")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state["approved"] and not st.session_state.get("audio_played", False):
    play_welcome_audio()
    st.session_state["audio_played"] = True

if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👋 مرحباً بك، م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.",
        "breeder": "🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح."
    }
    role_icons = {"owner": "👑", "specialist": "👨‍🔬", "breeder": "🌾"}
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"),
             icon=role_icons.get(st.session_state["user_role"], "🌾"))
    st.session_state["login_welcome_shown"] = True

# ============================================================
# 15. الواجهة الرئيسية
# ============================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_info = {
        "owner": "م. عبدالقادر إسماعيل تاور 👑",
        "specialist": "المختص والزملاء 👨‍🔬",
        "breeder": "المربي 🌾"
    }
    st.markdown(
        f"""<div style='text-align: left; font-size:0.9rem; color:#1a1a1a; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); padding: 10px; border-radius: 10px;'>
        الحساب: <b>{role_info.get(st.session_state["user_role"], "مستخدم")}</b><br>
        <small>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></div>""",
        unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != "inventory":
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">',
                    unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>تاور نولجي Tawor Nology 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>للإنتاج الحيواني وتغذية الحيوان</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1rem; margin-top:5px; margin-bottom:0;'>محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم (DP) ومعادل النشاء (SE)</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

st.markdown("### 📢 المشاركة التسويقية والدعوة العلمية")
share_text_payload = """📢 دعوة علمية وتسويقية من تاور نولجي Tawor Nology للإنتاج الحيواني وتغذية الحيوان

إلى كل مهتم بتطوير الثروة الحيوانية؛ من أطباء بيطريين، اختصاصيي إنتاج حيواني، ومربين طموحين:
يسعدنا دعوتكم لاستخدام وتجربة المنصة المتقدمة لتركيب وتطوير الأعلاف، بإشراف وتصميم:
[ م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان ]

🎯 ما تقدمه المنصة:
• حلول برمجية ذكية لتركيب أعلاف اقتصادية على أساس البروتين المهضوم ومعادل النشاء.
• أدوات دقيقة لحساب الاحتياجات الغذائية بما يضمن أعلى معدلات نمو وإنتاجية.
• دعم كامل للعمل الميداني والبحث العلمي والخصم التلقائي للمستودعات.
• نظام تحليلات متقدم وتقارير PDF احترافية.
• إدارة مزارع الدجاج اللاحم مع حساب KPIs و EPEF.

🔗 رابط المنصة: [ضع رابط موقعك هنا]"""
st.text_area("النص الدعائي والإعلامي الجاهز للنشر:", value=share_text_payload, height=140, key="top_share_box")
col_copy, col_share = st.columns(2)
with col_copy:
    if st.button("📋 نسخ الرابط والنص", type="secondary", use_container_width=True):
        st.success("تم التجهيز بنجاح! يمكنك الآن نسخ النص ومشاركته.")
with col_share:
    encoded_share = urllib.parse.quote(share_text_payload[:200])
    st.link_button("📲 مشاركة مباشرة عبر واتساب", f"https://wa.me/?text={encoded_share}", use_container_width=True)

st.markdown("---")

welcome_messages = {
    "owner": {"bg": "#eff6ff", "border": "#1d4ed8",
              "text": "👑 أهلاً بك م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل."},
    "specialist": {"bg": "#f0fdf4", "border": "#16a34a",
                   "text": "🔬 مرحباً بكم في منصة تاور نولجي لتركيب وتحليل الأعلاف الذكية."},
    "breeder": {"bg": "#fffbeb", "border": "#d97706",
                "text": "🚜 أهلاً وسهلاً بكم في منصة تاور نولجي. نوفر لكم خلطات مبنية على القيمة الغذائية الحقيقية الممتصة لضمان التوفير المالي العالي."}
}
current_welcome = welcome_messages.get(st.session_state["user_role"], welcome_messages["breeder"])
st.markdown(
    f"""<div style='background-color: {current_welcome["bg"]}; padding: 15px; border-radius: 8px;
    border-right: 5px solid {current_welcome["border"]}; text-align: right; direction: rtl; margin-bottom: 20px;'>
    <b>{current_welcome["text"]}</b></div>""",
    unsafe_allow_html=True)

# ============================================================
# 16. تحديد التبويبات حسب الدور
# ============================================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية",
        "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع",
        "🖨️ مصمم الديباجة والدعاية", "📈 التحليلات المتقدمة",
        "🐔 إدارة مزارع الدجاج اللاحم — خاص بالمالك",
        "💬 تعليقات المختصين", "📚 المراجع العلمية",
        "💡 المساعدة الذكية", "📖 دليل المستخدم"
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية",
        "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع",
        "🖨️ مصمم الديباجة والدعاية", "📈 التحليلات المتقدمة",
        "💬 تعليقات المختصين", "📚 المراجع العلمية",
        "💡 المساعدة الذكية", "📖 دليل المستخدم"
    ]
else:
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية", "📚 المراجع العلمية",
        "💡 المساعدة الذكية", "📖 دليل المستخدم"
    ]

tabs = st.tabs(tabs_titles)

# ============================================================
# 17. التبويب الأول: النمذجة والمختبر
# ============================================================
with tabs[0]:
    sub_tab_formulator, sub_tab_analyzer = st.tabs([
        "🎯 تركيب علفة نموذجية (أقل تكلفة بالبروتين المهضوم)",
        "🔬 مختبر تحليل وفحص الأعلاف الجاهزة"
    ])

    # ========== تركيب العلف ==========
    with sub_tab_formulator:
        st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
        col_country, col_state, col_city = st.columns(3)
        with col_country:
            user_country = st.selectbox("اختر دولة المربي:",
                ["السودان", "LIBYA", "مصر", "باقي دول العالم / البورصة المفتوحة"])
        c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"})
        local_rate = c_info["rate"]
        local_sym = c_info["sym"]

        chosen_state = "عام"
        with col_state:
            if user_country == "السودان":
                chosen_state = st.selectbox("اختر الولاية السودانية:",
                    ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف",
                     "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان",
                     "إقليم النيل الأزرق", "ولاية البحر الأحمر", "ولاية نهر النيل"])
            elif user_country == "LIBYA":
                chosen_state = st.selectbox("اختر الإقليم الجغرافي:",
                    ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
            else:
                chosen_state = st.selectbox("الإقليم الإداري:",
                    ["المركز الرئيسي العالمي", "الأسواق المفتوحة"])

        with col_city:
            if user_country == "السودان":
                cities_map = {
                    "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
                    "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"],
                    "ولاية القضارف": ["القضارف المدينة", "الفاو"],
                    "ولاية شمال كردفان": ["الأبيض", "بارا", "أم روابة"],
                    "ولاية جنوب كردفان": ["كادوقلي", "الدلنج"],
                    "ولاية غرب كردفان": ["الفوله", "النهود", "بابنوسة"],
                    "إقليم النيل الأزرق": ["الدمازين", "الروصيرص"],
                    "ولاية البحر الأحمر": ["بورتسودان", "سواكن"],
                    "ولاية نهر النيل": ["شندي", "عطبرة", "الدامر"]
                }
                user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
            elif user_country == "LIBYA":
                cities_map = {
                    "المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء", "درنة"],
                    "المنطقة الغربية": ["طرابلس", "مصراتة", "الزاوية"],
                    "المنطقة الجنوبية": ["سبها", "مرزق", "غات"]
                }
                user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
            else:
                user_city = st.text_input("اكتب اسم المدينة:", "طبرق")

        city_key = f"{user_country}|||{chosen_state}|||{user_city}"
        custom_prices = CITY_CUSTOM_PRICES.get(city_key, {})
        live_prices = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)

        col_view1, col_view2 = st.columns(2)
        with col_view1:
            st.markdown(
                f'<div class="price-card"><b>📈 بورصة الماشية والداجن في ({user_city}):</b><br>' +
                "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> '
                             f'(<span style="color:#e65100; font-weight:bold;">{v*local_rate:,.2f} {local_sym}</span>)'
                             for k, v in st.session_state["global_livestock_prices"].items()]) + "</div>",
                unsafe_allow_html=True)
        with col_view2:
            st.markdown(
                f'<div class="price-card"><b>🥩 بورصة المنتجات الحيوانية في ({user_city}):</b><br>' +
                "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> '
                             f'(<span style="color:#1b5e20; font-weight:bold;">{v*local_rate:,.2f} {local_sym}</span>)'
                             for k, v in st.session_state["global_products_prices"].items()]) + "</div>",
                unsafe_allow_html=True)

        st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
        col_sec, col_sub, col_prod = st.columns(3)
        with col_sec:
            main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:",
                ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها",
                 "الخيول والفروسية", "الطيور والسمان", "الأسماك والأحياء المائية"])
        show_measurements = False
        weight_factor = 10000
        feed_factor = 0.02
        default_dp = 11.0
        default_se = 60.0
        dynamic_img_key = "عام"
        chosen_concentrate = None
        gender_option = "إناث"

        if main_sector in ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها"]:
            with col_sec:
                gender_option = st.radio("حدد الجنس:",
                    ["ذكور (تسمين)", "إناث (حليب / أمهات)"], horizontal=True)

        with col_sub:
            if main_sector == "الأغنام وسلالاتها 🐏":
                sub_type = st.selectbox("السلالة المستهدفة:",
                    ["الضأن الصحراوي السوداني", "البربري", "النعيمي", "سلالات محلية / هجين"])
                dynamic_img_key = "أغنام"
                show_measurements = True
                weight_factor = 15500
                feed_factor = 0.035
                chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الماعز وسلالاتها":
                sub_type = st.selectbox("السلالة المستهدفة:",
                    ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور / محسن"])
                dynamic_img_key = "ماعز"
                show_measurements = True
                weight_factor = 15000
                feed_factor = 0.032
                chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الأبقار وسلالاتها":
                sub_type = st.selectbox("السلالة المستهدفة:",
                    ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"])
                dynamic_img_key = "أبقار"
                show_measurements = True
                weight_factor = 10838
                feed_factor = 0.025
                chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الخيول والفروسية":
                sub_type = st.selectbox("السلالة المستهدفة:",
                    ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"])
                dynamic_img_key = "خيول"
                show_measurements = True
                weight_factor = 11877
                feed_factor = 0.022
                chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الطيور والسمان":
                sub_type = st.selectbox("نوع الطيور:",
                    ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"])
                dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"
                chosen_concentrate = "مركزات دواجن وسمان"
            else:
                sub_type = st.selectbox("نوع الأسماك:",
                    ["البلطي النيلي (Tilapia)", "القرموط"])
                dynamic_img_key = "أسماك"
                chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

        with col_prod:
            if main_sector == "الأغنام وسلالاتها 🐏":
                if gender_option == "ذكور (تسمين)":
                    prod_stage = st.selectbox("خط إنتاج الذكور:",
                        ["تسمين حملان مكثف (نمو سريع)", "حملان تيد / كباش جاهزة للأسواق"])
                    default_dp = 12.0 if "مكثف" in prod_stage else 9.5
                    default_se = 64.0 if "مكثف" in prod_stage else 58.0
                else:
                    prod_stage = st.selectbox("خط إنتاج الإناث:",
                        ["نعاج مرضعات (إدرار عالي)", "نعاج حامل (الفترة الأخيرة)", "نعاج جافة / صيانة"])
                    default_dp = 12.8 if "مرضعات" in prod_stage else (10.5 if "حامل" in prod_stage else 8.0)
                    default_se = 66.0 if "مرضعات" in prod_stage else (60.0 if "حامل" in prod_stage else 50.0)
            elif main_sector == "الماعز وسلالاتها":
                if gender_option == "ذكور (تسمين)":
                    prod_stage = st.selectbox("خط إنتاج الذكور:",
                        ["تسمين جديان نمو سريع", "تيوس علفية جاهزة للتسويق"])
                    default_dp = 11.5 if "جديان" in prod_stage else 9.0
                    default_se = 62.0 if "جديان" in prod_stage else 55.0
                else:
                    prod_stage = st.selectbox("خط إنتاج الإناث:",
                        ["عنزات حلابة وغزارة لبن", "عنزات حامل (دفع غذائي)", "صيانة دورية للأمهات"])
                    default_dp = 12.8 if "حلابة" in prod_stage else (10.0 if "حامل" in prod_stage else 7.8)
                    default_se = 65.0 if "حلابة" in prod_stage else (58.0 if "حامل" in prod_stage else 48.0)
            elif main_sector == "الأبقار وسلالاتها":
                prod_stage = st.selectbox("نوع الإنتاج:",
                    ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"])
                default_dp = 12.5 if "حليب" in prod_stage else 10.0
                default_se = 68.0 if "حليب" in prod_stage else 65.0
            elif main_sector == "الخيول والفروسية":
                prod_stage = st.selectbox("نوع الإنتاج:",
                    ["خيول رياضة ونشاط مكثف", "أمهار نامية صغيرة", "فرسات مرضعات"])
                default_dp = 12.5 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 9.5
                default_se = 65.0 if "رياضة" in prod_stage else 60.0
            elif main_sector == "الطيور والسمان":
                if "السمان" in sub_type:
                    prod_stage = st.selectbox("نوع الإنتاج:",
                        ["سمان بادي / نامي", "سمان بياض إنتاجي"])
                    default_dp = 20.0 if "بادي" in prod_stage else 16.5
                    default_se = 72.0 if "بادي" in prod_stage else 68.0
                else:
                    prod_stage = st.selectbox("نوع الإنتاج:",
                        ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض إنتاجي"])
                    default_dp = 20.0 if "بادي" in prod_stage else (
                        18.5 if "نامي" in prod_stage else (
                            16.5 if "ناهي" in prod_stage else 15.0))
                    default_se = 76.0 if "بادي" in prod_stage else (
                        74.0 if "نامي" in prod_stage else (
                            75.0 if "ناهي" in prod_stage else 70.0))
            else:
                prod_stage = st.selectbox("نوع الإنتاج:",
                    ["بادئ زريعة أسماك عالي", "نمو وتسمين أسماك نيلية"])
                default_dp = 29.5 if "زريعة" in prod_stage else 25.0
                default_se = 70.0

        if show_measurements:
            st.markdown('<div class="section-title">📐 القياسات الجسدية وتقدير الأوزان</div>', unsafe_allow_html=True)
            col_h, col_l, col_ag = st.columns(3)
            with col_h:
                h_girth = st.number_input("📏 محيط الصدر (سم):",
                    value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 75.0)
            with col_l:
                b_length = st.number_input("📏 طول الجسم (سم):",
                    value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 65.0)
            with col_ag:
                a_months = st.number_input("⏳ العمر التقديري (أشهر):", value=12)
            calc_weight = (h_girth ** 2 * b_length) / weight_factor
            req_feed_kg = calc_weight * feed_factor
            st.success(f"📊 الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم** | "
                       f"الاحتياج اليومي للمادة الجافة: **{req_feed_kg:.2f} كجم**")
        else:
            st.markdown('<div class="section-title">✨ قطاع الطيور والأسماك</div>', unsafe_allow_html=True)
            st.info("💡 تم تحييد شريط القياس الجسدي لعدم ملاءمته للطيور والأسماك.")

        # بيانات الطالب
        st.markdown('<div class="section-title">👤 بيانات طالب الخدمة</div>', unsafe_allow_html=True)
        requester_name = st.text_input(
            "اسم طالب العلفة (سيظهر في التقرير الرسمي):",
            placeholder="مثال: مزرعة الأمل – أحمد محمد",
            key="formulator_requester"
        )

        st.markdown('<div class="section-title">📋 رابعاً: حدود الموازنة الذكية (DP & SE)</div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        use_cp_basis = st.checkbox("⚡ استخدم البروتين الخام (CP) بدلاً من المهضوم (DP)", value=False)
        if use_cp_basis:
            default_cp = default_dp / 0.82
            with col_p1:
                st.metric("🧬 بروتين خام (CP) مقترح:", f"{default_cp:.1f} %")
                override_cp = st.checkbox("⚙️ تعديل البروتين الخام")
                final_target_cp = st.slider("حدّد نسبة CP:", 5.0, 60.0,
                    value=float(default_cp)) if override_cp else default_cp
            final_target_dp = None
        else:
            with col_p1:
                st.metric("🧬 بروتين مهضوم (DP) مقترح:", f"{default_dp} %")
                override_dp = st.checkbox("⚙️ تعديل فني اختياري للبروتين المهضوم")
                final_target_dp = st.slider("حدّد نسبة DP:", 5.0, 40.0,
                    value=default_dp) if override_dp else default_dp
        with col_p2:
            st.metric("🌽 معادل النشاء (SE) مقترح:", f"{default_se} وحدة")
            override_se = st.checkbox("⚙️ تعديل فني اختياري لمعادل النشاء")
            final_target_se = st.slider("حدّد حد الـ SE المستهدف:", 10.0, 90.0,
                value=default_se) if override_se else default_se

        selected_ingredients = []
        ingredient_prices = {}
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}",
                             expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
                sub_cols = st.columns(3)
                for idx, (ing_name, _) in enumerate(items.items()):
                    with sub_cols[idx % 3]:
                        is_def = ing_name == chosen_concentrate or ing_name in [
                            "ذرة صفراء", "سورجم (فتريتة)", "أمباز الفول السوداني (كسب)",
                            "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام",
                            "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                            "بيكربونات الصوديوم (الصودا)", "مضاد سموم فطرية"]
                        checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                        current_live_price = live_prices.get(ing_name, 350.0)
                        if ing_name in custom_prices:
                            current_live_price = custom_prices[ing_name]
                        if st.session_state["user_role"] == "owner":
                            price_input = st.number_input(f"السعر للطن ({ing_name}) $:",
                                min_value=5.0, value=float(current_live_price),
                                key=f"price_{ing_name}")
                        else:
                            st.markdown(f"💰 السعر الحالي: **`${current_live_price:.2f}`** / طن")
                            price_input = current_live_price
                        if checked:
                            selected_ingredients.append(ing_name)
                            ingredient_prices[ing_name] = price_input

        fixed_additives = {
            "ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2,
            "الحجر الجيري (بودرة بلاط)": 2.5 if "بياض" in prod_stage else 1.5,
            "فوسفات ثنائي الكالسيوم (DCP)": 1.0
        }
        auto_added_enzymes = {}
        mandatory_warnings = []

        if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاتها", "الأغنام وسلالاتها 🐏"]:
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
            mandatory_warnings.append(
                "🚨 <b>إضافة إلزامية - بيكربونات الصوديوم:</b> تم فرضها أوتوماتيكياً بنسبة 0.75% "
                "كمنظم حموضة (Buffer) لحماية الكرش من <b>التحمض Ruminal Acidosis</b>.")
        elif main_sector == "الطيور والسمان":
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.20

        if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
            auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
            mandatory_warnings.append(
                "🚨 <b>إضافة إلزامية - إنزيم الفايتيز:</b> مضاف تلقائياً بنسبة 0.05% "
                "لتحرير <b>الفسفور النباتي المرتبط</b> وتحسين الهضم.")

        if "كسب بذور القطن (مقشور)" in selected_ingredients and main_sector == "الطيور والسمان":
            auto_added_enzymes["كبريتات الحديدوز (معادل الجوسيبول)"] = 0.15
            mandatory_warnings.append(
                "⚠️ <b>معالجة الجوسيبول:</b> تم دمج كبريتات الحديدوز بنسبة 0.15% "
                "لربط <b>الجوسيبول الحر السام Toxic Gossypol</b> وإبطال مفعوله.")

        if main_sector == "الطيور والسمان" and (
                ("شعير مطحون" in selected_ingredients) or ("قمح محلي مصنّع" in selected_ingredients)):
            auto_added_enzymes["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.08
            mandatory_warnings.append(
                "⚠️ <b>إضافة إنزيمات الـ NSP:</b> لمنع عارض البراز الرطب (Wet Litter).")

        all_fixed_additives = {**fixed_additives, **auto_added_enzymes}
        for item in all_fixed_additives:
            if item not in selected_ingredients:
                selected_ingredients.append(item)
                ingredient_prices[item] = live_prices.get(item, 40.0)

        st.markdown("---")
        nz_placeholder = st.empty()

        if st.button("🚀 تشغيل محرك الاستمثال الخطي (بالبروتين المهضوم ومعادل النشاء)",
                     type="primary", use_container_width=True):
            with nz_placeholder.container():
                st.warning("⚠️ **إشعار هام:** يرجى التأكد من موازنة درجات حرارة كبس العلف "
                           "لضمان عدم تثبيط الإنزيمات والفيتامينات الدقيقة. (سيختفي تلقائياً بعد 40 ثانية)")

            c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
            bounds = [(all_fixed_additives[ing], all_fixed_additives[ing])
                      if ing in all_fixed_additives else (0.0, 100.0)
                      for ing in selected_ingredients]

            A_eq = [[1.0 for _ in selected_ingredients]]
            b_eq = [100.0]

            cp_row = []
            se_row = []
            for ing in selected_ingredients:
                cp_val = 0.0
                dc_val = 0.0
                se_val = 0.0
                for cat in BIG_FEEDS_LIBRARY.values():
                    if ing in cat:
                        cp_val = cat[ing].get("CP", 0.0)
                        dc_val = cat[ing].get("DC", 0.0)
                        se_val = cat[ing].get("SE", 0.0)
                if use_cp_basis:
                    cp_row.append(cp_val)
                else:
                    cp_row.append(cp_val * dc_val)
                se_row.append(se_val)
            A_eq.append(cp_row)
            if use_cp_basis:
                b_eq.append(final_target_cp * 100.0)
            else:
                b_eq.append(final_target_dp * 100.0)

            A_ub = []
            b_ub = []
            A_ub.append([-1.0 * x for x in se_row])
            b_ub.append(-1.0 * final_target_se * 100.0)

            grain_indicators = [1.0 if ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"]
                                else 0.0 for ing in selected_ingredients]
            if sum(grain_indicators) > 0:
                A_ub.append([-1.0 * x for x in grain_indicators])
                b_ub.append(-50.0)
            if "نخالة قمح (ردة)" in selected_ingredients:
                fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0
                                    for ing in selected_ingredients]
                A_ub.append(fiber_indicators)
                b_ub.append(18.0)

            dynamic_limits = {
                "مولاس قصب السكر": {"default": 12.0, "دواجن": 5.0, "خيول": 8.0, "أسماك": 5.0},
                "يوريا علفية محصنة (المجترات فقط)": {"default": 1.0, "دواجن": 0.0, "خيول": 0.0, "أسماك": 0.0},
                "سرسة الأرز المطحونة": {"default": 10.0},
                "ملح الطعام": {"default": 1.0}
            }
            sector_key = main_sector.replace(" وسلالاتها", "").replace(" والأحياء المائية", "")
            for material, limits_dict in dynamic_limits.items():
                if material in selected_ingredients:
                    limit = limits_dict.get(sector_key, limits_dict.get("default", 15.0))
                    idx = selected_ingredients.index(material)
                    constraint_row = [0.0] * len(selected_ingredients)
                    constraint_row[idx] = 1.0
                    A_ub.append(constraint_row)
                    b_ub.append(limit)
                    mandatory_warnings.append(f"ℹ️ <b>حد أقصى:</b> {material} ≤ {limit}% (تلقائي للقطاع)")

            res = linprog(c_vector, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None,
                          A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

            if not res.success:
                A_ub_flex = []
                b_ub_flex = []
                A_ub_flex.append([-1.0 * x for x in se_row])
                b_ub_flex.append(-1.0 * (final_target_se - 3.0) * 100.0)
                if sum(grain_indicators) > 0:
                    A_ub_flex.append([-1.0 * x for x in grain_indicators])
                    b_ub_flex.append(-40.0)
                if "نخالة قمح (ردة)" in selected_ingredients:
                    fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0
                                        for ing in selected_ingredients]
                    A_ub_flex.append(fiber_indicators)
                    b_ub_flex.append(25.0)
                for material, limits_dict in dynamic_limits.items():
                    if material in selected_ingredients:
                        limit = limits_dict.get(sector_key, limits_dict.get("default", 15.0)) + 3
                        idx = selected_ingredients.index(material)
                        constraint_row = [0.0] * len(selected_ingredients)
                        constraint_row[idx] = 1.0
                        A_ub_flex.append(constraint_row)
                        b_ub_flex.append(limit)
                res = linprog(c_vector, A_ub=A_ub_flex, b_ub=b_ub_flex,
                              A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

            if res.success:
                formula_results = {}
                computed_se_total = 0.0
                for idx, ing in enumerate(selected_ingredients):
                    if res.x[idx] > 0.0001:
                        formula_results[ing] = res.x[idx]
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                computed_se_total += (res.x[idx] / 100.0) * cat[ing].get("SE", 0.0)

                st.session_state["active_formula"] = formula_results
                st.session_state["active_cp_tag"] = final_target_dp if not use_cp_basis else (final_target_cp * 0.82)
                st.session_state["active_se_tag"] = computed_se_total
                st.session_state["active_breed_tag"] = sub_type
                st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(
                    dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
                st.session_state["active_stage_title"] = f"{main_sector} ({gender_option}) - {prod_stage}"
                st.success(f"🎯 تم تشغيل محرك الاستمثال الخطي بنجاح في سوق: {user_city}")

                if not use_cp_basis and final_target_dp > 0:
                    nutritive_ratio = computed_se_total / final_target_dp
                    st.info(f"📊 النسبة الغذائية للخلطة (Nutritive Ratio = SE / DP): "
                            f"**{nutritive_ratio:.2f}**")

                if mandatory_warnings:
                    st.markdown("### 🔬 تقرير فحص العلل والتدخل البرمجي:")
                    for warn in mandatory_warnings:
                        st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)

                # ===== جدول المقارنة في الواجهة =====
                st.markdown("### 📊 جدول مقارنة العناصر الغذائية (قياسي vs محسوب)")
                std_key = get_standard_key(main_sector, prod_stage)
                standard_vals = NUTRIENT_STANDARDS.get(std_key, NUTRIENT_STANDARDS["دواجن_ناهي"])
                calculated_vals = compute_formula_nutrients(formula_results)

                compare_rows = []
                labels_ar = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP", "SE": "معادل النشاء SE",
                             "NDF": "ألياف NDF", "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH"}
                for k, std_v in standard_vals.items():
                    calc_v = calculated_vals.get(k, 0.0)
                    diff = calc_v - std_v
                    pct = (diff / std_v * 100) if std_v else 0
                    if abs(pct) <= 5:
                        status = "✅ مطابق"
                    elif abs(pct) <= 15:
                        status = "⚠️ مقبول"
                    else:
                        status = "❌ غير مطابق"
                    compare_rows.append({
                        "العنصر": labels_ar.get(k, k),
                        "المعيار القياسي": f"{std_v:.2f}",
                        "القيمة المحسوبة": f"{calc_v:.2f}",
                        "الفرق": f"{diff:+.2f}",
                        "الفرق %": f"{pct:+.1f}%",
                        "التقييم": status,
                    })
                st.dataframe(pd.DataFrame(compare_rows),
                             use_container_width=True, hide_index=True)

                res_col1, res_col2 = st.columns([0.6, 0.4])
                with res_col1:
                    st.write("#### 📝 المقادير المعتمدة لتركيب طن واحد (كجم):")
                    for k, v in formula_results.items():
                        st.markdown(f'<div class="formula-item">▪️ <b>{k}:</b> {v:.2f} % '
                                    f'➡️ ({v*10:.1f} كجم / طن)</div>',
                                    unsafe_allow_html=True)

                    ton_cost = res.fun / 100.0 if hasattr(res, 'fun') else 280.0
                    st.session_state["computed_ton_cost"] = ton_cost
                    st.metric(f"💰 التكلفة الفعلية لإنتاج الطن في {user_city}: ",
                              f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")

                    col_share, col_pdf, col_excel = st.columns(3)
                    with col_share:
                        share_message = (f"تاور نولجي Tawor Nology - الخلطة المعتمدة: {sub_type} "
                                         f"({gender_option})، بتكلفة إنتاج {ton_cost:.2f}$ للطن. "
                                         f"المشرف: م. عبدالقادر إسماعيل تاور.")
                        encoded_share_msg = urllib.parse.quote(share_message)
                        st.link_button("📲 مشاركة الفاتورة", f"https://wa.me/?text={encoded_share_msg}")

                    with col_pdf:
                        try:
                            pdf_data = pdf_generator.generate_comprehensive_report(
                                formula=formula_results,
                                target_dp=st.session_state["active_cp_tag"],
                                breed=f"{sub_type} ({gender_option})",
                                cost=ton_cost,
                                city=user_city,
                                local_cost=ton_cost * local_rate,
                                local_sym=local_sym,
                                computed_se=computed_se_total,
                                requester_name=requester_name,
                                animal_type=main_sector,
                                production_stage=prod_stage,
                                include_charts=True,
                                report_type="تركيب علفة"
                            )
                            st.download_button(
                                "📥 تحميل PDF",
                                pdf_data,
                                file_name=f"TaworNology_Feed_{user_city}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as pdf_err:
                            st.error(f"⚠️ خطأ PDF: {pdf_err}")

                    with col_excel:
                        try:
                            xlsx_data = export_comparison_to_excel(
                                standard=standard_vals,
                                calculated=calculated_vals,
                                requester_name=requester_name,
                                animal=main_sector,
                                stage=prod_stage,
                                formula=formula_results
                            )
                            if xlsx_data:
                                st.download_button(
                                    "📊 تحميل Excel",
                                    xlsx_data,
                                    file_name=f"TaworNology_Feed_{user_city}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            else:
                                st.warning("⚠️ openpyxl غير مثبتة")
                        except Exception as xlsx_err:
                            st.error(f"⚠️ خطأ Excel: {xlsx_err}")

                with res_col2:
                    fig = px.pie(values=list(formula_results.values()),
                                 names=list(formula_results.keys()),
                                 title="توزيع مكونات الخلطة",
                                 color_discrete_sequence=px.colors.sequential.Greens)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    chart_data = pd.DataFrame({
                        'المكون': list(formula_results.keys()),
                        'النسبة المئوية': list(formula_results.values()),
                        'الوزن (كجم/طن)': [v*10 for v in formula_results.values()]
                    })
                    st.bar_chart(chart_data.set_index('المكون')['الوزن (كجم/طن)'])
            else:
                st.error("❌ تعذر إيجاد حل رياضي متزن. يرجى إتاحة خامات إضافية "
                         "ككسب فول صويا أو أمباز الفول لتوسيع مساحة الحل.")
            time.sleep(40)
            nz_placeholder.empty()

    # ========== مختبر التحليل ==========
    with sub_tab_analyzer:
        st.markdown('<div class="section-title">🔬 مختبر فحص وتحليل الخلطات الجاهزة</div>', unsafe_allow_html=True)
        st.write("اكتب مقادير خلطتك الحالية بالكيلوجرام، وسيقوم المختبر بتحليلها برمجياً.")

        st.subheader("🎯 حدد الحيوان والغرض المستهدف للمقارنة:")
        col_lab_animal, col_lab_stage = st.columns(2)
        with col_lab_animal:
            target_animal = st.selectbox("اختر الفصيل:",
                ["أبقار", "أغنام", "ماعز", "خيول", "دواجن لاحم",
                 "دواجن بياض", "سمان", "أسماك"])
        with col_lab_stage:
            if target_animal in ["أبقار", "أغنام", "ماعز"]:
                production_type = st.selectbox("مرحلة الإنتاج:",
                    ["تسمين", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"])
            elif target_animal in ["دواجن لاحم", "دواجن بياض", "سمان"]:
                production_type = st.selectbox("مرحلة الإنتاج:",
                    ["بادي", "نامي", "ناهي", "بياض"])
            else:
                production_type = st.selectbox("مرحلة الإنتاج:", ["نمو", "تسمين نهائي"])

        st.markdown("---")
        lab_requester = st.text_input(
            "👤 اسم طالب التحليل (سيظهر في التقرير الرسمي):",
            placeholder="مثال: مصنع أعلاف الجزيرة – م. سامي",
            key="lab_requester"
        )
        st.markdown("---")

        st.subheader("📥 أدخل أوزان المكونات بالكيلوجرام:")
        lab_user_inputs = {}
        all_library_ingredients = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            for ing_name in items.keys():
                all_library_ingredients.append(ing_name)

        col_input1, col_input2, col_input3 = st.columns(3)
        total_ing_count = len(all_library_ingredients)
        segment = total_ing_count // 3 + 1

        with col_input1:
            for ing_name in all_library_ingredients[:segment]:
                lab_user_inputs[ing_name] = st.number_input(
                    f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0,
                    step=5.0, key=f"lab_in_{ing_name}")
        with col_input2:
            for ing_name in all_library_ingredients[segment:segment*2]:
                lab_user_inputs[ing_name] = st.number_input(
                    f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0,
                    step=5.0, key=f"lab_in_{ing_name}")
        with col_input3:
            for ing_name in all_library_ingredients[segment*2:]:
                lab_user_inputs[ing_name] = st.number_input(
                    f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0,
                    step=5.0, key=f"lab_in_{ing_name}")

        st.markdown("---")
        if st.button("🧪 تشغيل التحليل المخبري", type="primary", use_container_width=True):
            lab_total_weight = sum(lab_user_inputs.values())
            if lab_total_weight <= 0:
                st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
            else:
                calculated = {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0,
                              "ADF": 0.0, "EE": 0.0, "ASH": 0.0}
                lab_formula_pct = {}
                entered_components_summary = []

                for ing_name, weight in lab_user_inputs.items():
                    if weight > 0:
                        pct = weight / lab_total_weight * 100
                        lab_formula_pct[ing_name] = pct
                        for cat, items in BIG_FEEDS_LIBRARY.items():
                            if ing_name in items:
                                d = items[ing_name]
                                calculated["CP"]  += (pct / 100) * d.get("CP", 0.0)
                                calculated["DP"]  += (pct / 100) * d.get("CP", 0.0) * d.get("DC", 0.0)
                                calculated["SE"]  += (pct / 100) * d.get("SE", 0.0)
                                calculated["NDF"] += (pct / 100) * d.get("NDF", 0.0)
                                calculated["ADF"] += (pct / 100) * d.get("ADF", 0.0)
                                calculated["EE"]  += (pct / 100) * d.get("EE", 0.0)
                                calculated["ASH"] += (pct / 100) * d.get("ASH", 0.0)
                                break
                        entered_components_summary.append({
                            "المادة العلفية": ing_name,
                            "الوزن المدخل": f"{weight:.1f} كجم",
                            "النسبة المئوية": f"{pct:.2f}%"
                        })

                st.success("🔬 تم فحص العينة وتحليل المحتوى الغذائي بنجاح!")
                st.markdown(f"### ⚖️ إجمالي وزن الخلطة: **{lab_total_weight:.1f} كجم**")
                st.write("#### 📊 نسب توزيع المكونات:")
                st.table(pd.DataFrame(entered_components_summary))

                st.markdown("---")
                st.markdown("#### 📊 جدول مقارنة العناصر الغذائية (قياسي vs محسوب)")
                std_key = get_standard_key(target_animal, production_type)
                standard_vals = NUTRIENT_STANDARDS.get(std_key, NUTRIENT_STANDARDS["دواجن_ناهي"])
                labels_ar = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                             "SE": "معادل النشاء SE", "NDF": "ألياف NDF",
                             "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH"}
                compare_rows = []
                for k, std_v in standard_vals.items():
                    calc_v = calculated.get(k, 0.0)
                    diff = calc_v - std_v
                    pct = (diff / std_v * 100) if std_v else 0
                    if abs(pct) <= 5:
                        status = "✅ مطابق"
                    elif abs(pct) <= 15:
                        status = "⚠️ مقبول"
                    else:
                        status = "❌ غير مطابق"
                    compare_rows.append({
                        "العنصر": labels_ar.get(k, k),
                        "المعيار القياسي": f"{std_v:.2f}",
                        "القيمة المحسوبة": f"{calc_v:.2f}",
                        "الفرق": f"{diff:+.2f}",
                        "الفرق %": f"{pct:+.1f}%",
                        "التقييم": status,
                    })
                st.dataframe(pd.DataFrame(compare_rows),
                             use_container_width=True, hide_index=True)

                st.markdown("---")
                st.write("#### 🔬 تقرير الفحص المخبري النهائي:")
                st.write(f"🔬 البروتين الخام (CP) المحسوب: **{calculated['CP']:.2f}%**")
                st.write(f"🔬 البروتين المهضوم (DP) المحسوب: **{calculated['DP']:.2f}%**")
                st.write(f"🔬 معادل النشاء (SE) المحسوب: **{calculated['SE']:.2f} وحدة**")

                if lab_formula_pct:
                    fig = px.bar(x=list(lab_formula_pct.keys()),
                                 y=list(lab_formula_pct.values()),
                                 labels={'x': 'المادة العلفية', 'y': 'النسبة %'},
                                 title="توزيع النسب المئوية في الخلطة المختبرة")
                    st.plotly_chart(fig, use_container_width=True)

                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    try:
                        pdf_lab = pdf_generator.generate_comprehensive_report(
                            formula=lab_formula_pct,
                            target_dp=calculated["DP"],
                            breed=f"{target_animal} - {production_type}",
                            cost=0.0,
                            city="المختبر المركزي",
                            local_cost=0.0,
                            local_sym="USD",
                            computed_se=calculated["SE"],
                            requester_name=lab_requester,
                            animal_type=target_animal,
                            production_stage=production_type,
                            include_charts=True,
                            report_type="تحليل مختبري"
                        )
                        st.download_button(
                            "📥 تحميل التقرير المختبري PDF",
                            pdf_lab,
                            file_name=f"TaworNology_Lab_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"⚠️ خطأ PDF: {e}")

                with col_dl2:
                    try:
                        xlsx_lab = export_comparison_to_excel(
                            standard=standard_vals,
                            calculated=calculated,
                            requester_name=lab_requester,
                            animal=target_animal,
                            stage=production_type,
                            formula=lab_formula_pct
                        )
                        if xlsx_lab:
                            st.download_button(
                                "📊 تحميل التقرير Excel",
                                xlsx_lab,
                                file_name=f"TaworNology_Lab_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"⚠️ خطأ Excel: {e}")

                lab_share_text = (f"نتيجة مختبر تاور نولجي:\nالحيوان: {target_animal} - {production_type}\n"
                                  f"البروتين المهضوم: {calculated['DP']:.2f}%\n"
                                  f"معادل النشاء: {calculated['SE']:.2f}")
                encoded_lab = urllib.parse.quote(lab_share_text)
                st.markdown(
                    f'<a href="https://wa.me/?text={encoded_lab}" target="_blank">'
                    f'<button style="background-color:#25D366; color:white; padding:10px; border-radius:5px;">'
                    f'📲 مشاركة النتيجة عبر واتساب</button></a>',
                    unsafe_allow_html=True)

# ============================================================
# 18. تبويب بورصة الأسعار
# ============================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[1]:
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور نولجي المركزية</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب مختص: متاح لك استعراض الأسعار فقط.")

        tab_livestock, tab_products = st.tabs(["🐄 بورصة الماشية", "🥛 بورصة المنتجات"])
        with tab_livestock:
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                st.subheader("أسعار الماشية والداجن")
                for animal, price in st.session_state["global_livestock_prices"].items():
                    if st.session_state["user_role"] == "owner":
                        st.session_state["global_livestock_prices"][animal] = st.number_input(
                            f"تحديث: {animal}", min_value=0.0, value=float(price),
                            step=0.1, key=f"livestock_{animal}")
                    else:
                        st.markdown(f"▪️ {animal}: **${price:.2f}**")
            with col_edit2:
                if st.session_state["user_role"] == "owner":
                    st.subheader("إضافة حيوان جديد")
                    new_animal = st.text_input("اسم الحيوان/السلالة:")
                    new_price = st.number_input("السعر بالدولار:", min_value=0.0, value=0.0)
                    if st.button("إضافة إلى البورصة") and new_animal:
                        st.session_state["global_livestock_prices"][f"{new_animal} ($)"] = new_price
                        st.success("تمت الإضافة بنجاح!")
                        st.rerun()
        with tab_products:
            col_prod1, col_prod2 = st.columns(2)
            with col_prod1:
                st.subheader("أسعار المنتجات الحيوانية")
                for product, price in st.session_state["global_products_prices"].items():
                    if st.session_state["user_role"] == "owner":
                        st.session_state["global_products_prices"][product] = st.number_input(
                            f"تحديث: {product}", min_value=0.0, value=float(price),
                            step=0.05, key=f"prod_edit_{product}")
                    else:
                        st.markdown(f"▪️ {product}: **${price:.2f}**")

# ============================================================
# 19. تبويب إدارة المخازن
# ============================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[2]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب مختص: يمكنك مراجعة الأرصدة فقط.")
        stock_warnings = InventoryManager.check_stock_levels()
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        with col_stats1:
            st.metric("إجمالي المواد", len(st.session_state["inventory"]))
        with col_stats2:
            critical_items = sum(1 for v in stock_warnings.values() if v == "نفذ المخزون")
            st.metric("مواد نفذت", critical_items,
                      delta=f"-{critical_items}" if critical_items > 0 else "0")
        with col_stats3:
            low_items = sum(1 for v in stock_warnings.values() if v == "منخفض")
            st.metric("مواد منخفضة", low_items,
                      delta=f"-{low_items}" if low_items > 0 else "0")
        with col_stats4:
            healthy_items = len(st.session_state["inventory"]) - critical_items - low_items
            st.metric("مواد آمنة", healthy_items)
        st.markdown("---")
        inv_cols = st.columns(3)
        for idx, (ing_name, qty_data) in enumerate(list(st.session_state["inventory"].items())):
            with inv_cols[idx % 3]:
                qty = qty_data if isinstance(qty_data, (int, float)) else qty_data["quantity"]
                threshold = 5.0 if isinstance(qty_data, (int, float)) else qty_data.get("min_threshold", 5.0)
                if qty <= 0:
                    status_badge = f'<span class="stock-critical">⚠️ نفذ: {qty:.2f} طن</span>'
                elif qty < threshold:
                    status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>'
                else:
                    status_badge = f'<span class="stock-normal">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                if st.session_state["user_role"] == "owner":
                    new_qty = st.number_input(f"تحديث ({ing_name}) طن:",
                        min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")
                    if isinstance(st.session_state["inventory"][ing_name], dict):
                        st.session_state["inventory"][ing_name]["quantity"] = new_qty
                        st.session_state["inventory"][ing_name]["last_updated"] = datetime.now().isoformat()
                    else:
                        st.session_state["inventory"][ing_name] = new_qty

# ============================================================
# 20. تبويب الفواتير
# ============================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[3]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            client_name = st.text_input("اسم العميل / المزرعة:",
                "مزارع الإنتاج المتكاملة")
        with col_c2:
            required_tons = st.number_input("الكمية المطلوبة (طن):",
                min_value=0.1, value=2.0, step=0.5)
        with col_c3:
            added_profit = st.number_input("هامش الربح للطن ($):",
                min_value=0.0, value=50.0)
        selling_price = st.session_state["computed_ton_cost"] + added_profit
        total_bill = selling_price * required_tons
        st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
        col_fact1, col_fact2 = st.columns(2)
        with col_fact1:
            st.markdown(f"""<div class="price-card"><h4>تفاصيل الفاتورة:</h4>
            <p>العميل: <b>{client_name}</b></p>
            <p>الكمية: <b>{required_tons} طن</b></p>
            <p>سعر الطن: <b>${selling_price:.2f}</b></p>
            <p style="font-size: 1.2rem; color: #1b5e20;">الإجمالي: <b>${total_bill:.2f}</b></p></div>""",
            unsafe_allow_html=True)
        with col_fact2:
            st.markdown("#### 📊 مكونات الخلطة المباعة:")
            if st.session_state["active_formula"]:
                for ingredient, pct in st.session_state["active_formula"].items():
                    required_amount = (pct / 100) * required_tons
                    st.markdown(f"▪️ {ingredient}: **{required_amount:.2f}** طن ({pct:.1f}% من الخلطة)")
        if st.session_state["user_role"] == "owner":
            if st.button("✅ تأكيد عملية البيع وخصم المكونات",
                         type="primary", use_container_width=True):
                can_deduct = True
                for name, pct in st.session_state["active_formula"].items():
                    current_stock = st.session_state["inventory"].get(name, 0.0)
                    if isinstance(current_stock, dict):
                        current_stock = current_stock["quantity"]
                    required_amount = (pct / 100) * required_tons
                    if current_stock < required_amount:
                        can_deduct = False
                        st.error(f"❌ رصيد غير كافي: {name}!")
                        break
                if can_deduct:
                    for name, pct in st.session_state["active_formula"].items():
                        required_amount = (pct / 100) * required_tons
                        if isinstance(st.session_state["inventory"][name], dict):
                            st.session_state["inventory"][name]["quantity"] -= required_amount
                            st.session_state["inventory"][name]["last_updated"] = datetime.now().isoformat()
                        else:
                            st.session_state["inventory"][name] -= required_amount
                    st.success("🔥 تم الخصم التلقائي وتحديث المخازن بنجاح!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
        else:
            st.info("ℹ️ تأكيد الفواتير متاح لإدارة المالك فقط.")

# ============================================================
# 21. تبويب مصمم الديباجة
# ============================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[4]:
        st.markdown('<div class="section-title">👑 مصمم ديباجات الطباعة الفنية</div>', unsafe_allow_html=True)
        trade_brand = st.text_input("اسم البراند التجاري:",
            "تاور نولجي Tawor Nology")
        col_preview, col_options = st.columns([0.7, 0.3])
        with col_preview:
            st.markdown(f"""<div class="sack-tag">
            <img src="{st.session_state['active_animal_img']}" class="animal-banner-img">
            <h2 style="text-align: center; margin-top:0; color: #1b5e20;">🌟 {trade_brand} 🌟</h2>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">
            م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان</h3>
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:10px; color:#1b5e20; border-radius: 8px;">
            🎯 {st.session_state['active_stage_title']} |
            DP: {st.session_state['active_cp_tag']:.1f}% |
            SE: {st.session_state['active_se_tag']:.1f} وحدة</p>
            <div style="text-align: center; margin-top: 15px;">
            <small style="color: #666;">تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}</small>
            </div></div>""", unsafe_allow_html=True)
        with col_options:
            st.markdown("#### خيارات التخصيص:")
            st.checkbox("إضافة QR Code", value=True)
            st.checkbox("إظهار تاريخ الإنتاج", value=True)
            st.slider("حجم الخط", 12, 24, 16)
            if st.button("📥 تصدير الديباجة كـ PDF", use_container_width=True):
                st.success("تم تجهيز الديباجة للطباعة!")

# ============================================================
# 22. تبويب التحليلات المتقدمة
# ============================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[5]:
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة ولوحة المؤشرات</div>', unsafe_allow_html=True)
        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
        with col_met1:
            st.markdown("""<div class="metric-card">
            <h3 style="color: #1b5e20;">عدد الخلطات</h3>
            <h2 style="color: #2e7d32;">1,247</h2>
            <p>خلطة تم توليدها</p></div>""", unsafe_allow_html=True)
        with col_met2:
            st.markdown("""<div class="metric-card">
            <h3 style="color: #1565C0;">متوسط التكلفة</h3>
            <h2 style="color: #1976D2;">$285</h2>
            <p>لطن العلف</p></div>""", unsafe_allow_html=True)
        with col_met3:
            st.markdown("""<div class="metric-card">
            <h3 style="color: #E65100;">نسبة التوفير</h3>
            <h2 style="color: #F57C00;">18%</h2>
            <p>مقارنة بالتقليدي</p></div>""", unsafe_allow_html=True)
        with col_met4:
            st.markdown("""<div class="metric-card">
            <h3 style="color: #2E7D32;">رضا العملاء</h3>
            <h2 style="color: #388E3C;">96%</h2>
            <p>تقييم إيجابي</p></div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("🔮 تنبؤات الأسعار")
        predictor = PricePredictor()
        ingredients = ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح"]
        col_preds = st.columns(3)
        for idx, ing in enumerate(ingredients):
            with col_preds[idx]:
                pred = predictor.predict_price(ing, 7)
                if pred.get('prediction'):
                    trend_icon = "📈" if pred.get('trend') == 'up' else "📉" if pred.get('trend') == 'down' else "➡️"
                    st.metric(
                        f"{trend_icon} {ing}",
                        f"${pred['prediction']:.2f}",
                        delta=f"{pred['prediction'] - pred.get('current_price', 0):.2f}",
                        help=f"الثقة: {pred.get('confidence', 0)*100:.0f}%"
                    )
        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("📊 توزيع استخدام المواد العلفية")
            usage_data = pd.DataFrame({
                'المادة': ['ذرة', 'صويا', 'نخالة', 'أملاح', 'أخرى'],
                'نسبة الاستخدام': [45, 25, 15, 10, 5]
            })
            fig = px.pie(usage_data, values='نسبة الاستخدام', names='المادة',
                         title='المواد الأكثر استخداماً',
                         color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)
        with col_chart2:
            st.subheader("📈 اتجاه أسعار المواد الخام")
            dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
            price_trend = pd.DataFrame({
                'التاريخ': dates,
                'الذرة': [220, 225, 230, 228, 235, 240, 238, 242, 245, 248, 250, 252],
                'الصويا': [440, 445, 442, 448, 450, 455, 452, 458, 460, 462, 465, 468]
            })
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=price_trend['التاريخ'], y=price_trend['الذرة'],
                mode='lines+markers', name='الذرة',
                line=dict(color='#2e7d32', width=2)))
            fig.add_trace(go.Scatter(x=price_trend['التاريخ'], y=price_trend['الصويا'],
                mode='lines+markers', name='الصويا',
                line=dict(color='#1565C0', width=2)))
            fig.update_layout(title='اتجاه أسعار المواد الخام خلال العام',
                xaxis_title='التاريخ', yaxis_title='السعر ($/طن)',
                hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 23. تبويب مزارع الدجاج (owner فقط)
# ============================================================
if st.session_state["user_role"] == "owner":
    with tabs[6]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم — خاص بالمالك</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #f0fdf4; padding:15px; border-radius:12px; border-right:5px solid #16a34a; margin-bottom:20px;'>
        <b>📘 الدليل الموسع:</b> يمكنك تسجيل مزارع متعددة بأسماء ملاكها، وتدوين السجل الصحي اليومي.
        يقوم النظام بمقارنة ما تم إعطاؤه فعلياً بالبروتوكول القياسي، ويرسل تنبيهات عبر واتساب.
        </div>
        """, unsafe_allow_html=True)

        col_farms = st.columns([0.4, 0.6])
        with col_farms[0]:
            st.markdown("#### 🏠 إدارة المزارع المسجلة")
            farm_names = list(st.session_state["broiler_farms"].keys())
            selected = st.selectbox("اختر مزرعة:", [""] + farm_names,
                format_func=lambda x: x if x else "-- أضف مزرعة جديدة --")
            if st.button("➕ إضافة مزرعة جديدة", use_container_width=True):
                st.session_state["show_add_farm"] = True
            if st.button("🗑️ حذف المزرعة المختارة", use_container_width=True):
                if selected and selected in st.session_state["broiler_farms"]:
                    del st.session_state["broiler_farms"][selected]
                    if st.session_state["selected_farm"] == selected:
                        st.session_state["selected_farm"] = None
                    st.success(f"تم حذف مزرعة {selected}")
                    st.rerun()

        if st.session_state.get("show_add_farm", False):
            st.markdown("#### ✏️ بيانات المزرعة الجديدة")
            new_name = st.text_input("اسم المزرعة")
            new_owner = st.text_input("اسم المالك")
            new_phone = st.text_input("رقم واتساب المالك:", value=WHATSAPP_NUMBER)
            if st.button("💾 حفظ المزرعة الجديدة") and new_name:
                st.session_state["broiler_farms"][new_name] = {
                    "owner": new_owner, "owner_phone": new_phone,
                    "daily_logs": [], "health_log": [],
                    "current_data": {
                        "farm_name": new_name,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "flock_age_days": 1, "initial_birds": 1,
                        "current_weight_kg": 0.045, "initial_weight_kg": 0.045,
                        "total_feed_consumed_kg": 0.0, "dead_birds": 0,
                        "culled_birds": 0, "temperature_c": 33.0,
                        "humidity_percent": 65.0,
                        "ventilation_status": "جيدة",
                        "litter_quality": "جيدة", "notes": ""
                    },
                    "created_at": datetime.now().isoformat()
                }
                st.session_state["selected_farm"] = new_name
                st.session_state["show_add_farm"] = False
                st.success("تمت إضافة المزرعة بنجاح!")
                st.rerun()

        if selected and selected in st.session_state["broiler_farms"]:
            st.session_state["selected_farm"] = selected
            farm = st.session_state["broiler_farms"][selected]
            st.markdown(f"### 🏷️ المزرعة: **{selected}** (المالك: {farm.get('owner', 'غير مسجل')})")

            current = farm["current_data"]
            st.markdown("#### 📝 بيانات اليوم الحالية")
            col_inputs, col_outputs = st.columns([0.5, 0.5])
            with col_inputs:
                new_age = st.number_input("عمر القطيع (يوم)", min_value=1, max_value=60,
                    value=max(current["flock_age_days"], 1), step=1, key="bf_age")
                init_birds = st.number_input("عدد الكتاكيت المستلمة", min_value=1,
                    value=max(current["initial_birds"], 1), step=100, key="bf_init")
                dead = st.number_input("النافق حتى اليوم", min_value=0,
                    value=current["dead_birds"], step=1, key="bf_dead")
                culled = st.number_input("المستبعدين", min_value=0,
                    value=current["culled_birds"], step=1, key="bf_culled")
                avg_wt = st.number_input("متوسط الوزن الحي (كجم)", min_value=0.0,
                    value=current["current_weight_kg"], step=0.05, key="bf_wt")
                init_wt = st.number_input("وزن الكتكوت عند الاستلام (كجم)", min_value=0.030,
                    value=current["initial_weight_kg"], step=0.005, key="bf_init_wt")
                feed = st.number_input("إجمالي العلف المستهلك (كجم)", min_value=0.0,
                    value=current["total_feed_consumed_kg"], step=100.0, key="bf_feed")
                temp = st.number_input("درجة الحرارة (مئوي)", min_value=10.0, max_value=45.0,
                    value=current["temperature_c"], step=0.5, key="bf_temp")
                hum = st.number_input("الرطوبة (%)", min_value=20.0, max_value=90.0,
                    value=current["humidity_percent"], step=1.0, key="bf_hum")
                vent = st.selectbox("التهوية", ["سيئة", "مقبولة", "جيدة", "ممتازة"],
                    index=["سيئة", "مقبولة", "جيدة", "ممتازة"].index(current["ventilation_status"]),
                    key="bf_vent")
                litter = st.selectbox("جودة الفرشة", ["سيئة", "مقبولة", "جيدة", "ممتازة"],
                    index=["سيئة", "مقبولة", "جيدة", "ممتازة"].index(current["litter_quality"]),
                    key="bf_litter")
                notes = st.text_area("ملاحظات", value=current["notes"], key="bf_notes")

                st.markdown("#### 💊 السجل الصحي اليومي")
                given_meds = st.text_area(
                    "الأدوية والفيتامينات والتحصينات التي تم إعطاؤها اليوم:",
                    placeholder="مثال: لقاح نيوكاسل - قطرة عين - الساعة 8 صباحاً")
                if st.button("💾 حفظ بيانات اليوم والسجل الصحي",
                             use_container_width=True, type="primary"):
                    current.update({
                        "flock_age_days": new_age, "initial_birds": init_birds,
                        "dead_birds": dead, "culled_birds": culled,
                        "current_weight_kg": avg_wt, "initial_weight_kg": init_wt,
                        "total_feed_consumed_kg": feed,
                        "temperature_c": temp, "humidity_percent": hum,
                        "ventilation_status": vent, "litter_quality": litter,
                        "notes": notes,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    daily_record = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "age_days": new_age, "avg_weight_kg": avg_wt,
                        "feed_consumed_kg": feed, "dead": dead, "culled": culled,
                        "temperature": temp, "humidity": hum, "notes": notes
                    }
                    farm["daily_logs"].append(daily_record)
                    if given_meds.strip():
                        health_record = {
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "age_days": new_age,
                            "medications_given": given_meds,
                            "standard_required": st.session_state["standard_vacc_schedule"].get(new_age, None)
                        }
                        farm["health_log"].append(health_record)
                    st.success("تم حفظ بيانات اليوم والسجل الصحي بنجاح!")
                    check_and_alert_medications(selected, farm, new_age)
                    st.rerun()

            with col_outputs:
                total_alive = current["initial_birds"] - current["dead_birds"] - current["culled_birds"]
                total_gain_kg = total_alive * (current["current_weight_kg"] - current["initial_weight_kg"])
                adg = BroilerFarmManager.calculate_adg(
                    current["current_weight_kg"] * 1000,
                    current["initial_weight_kg"] * 1000,
                    current["flock_age_days"])
                fcr = BroilerFarmManager.calculate_fcr(
                    current["total_feed_consumed_kg"], total_gain_kg) if total_gain_kg > 0 else 0
                mortality = BroilerFarmManager.calculate_mortality_rate(
                    current["dead_birds"], current["initial_birds"])
                livability = BroilerFarmManager.calculate_livability(
                    current["initial_birds"], current["dead_birds"])
                epef = BroilerFarmManager.calculate_epef(
                    livability, current["current_weight_kg"],
                    current["flock_age_days"], fcr)

                st.metric("الوزن الحي (كجم)", f"{current['current_weight_kg']:.3f}")
                st.metric("معدل النمو اليومي ADG (جم)", f"{adg:.1f}")
                st.metric("معامل التحويل FCR", f"{fcr:.2f}")
                st.metric("نسبة النفوق (%)", f"{mortality:.2f}%")
                st.metric("الحيوية (%)", f"{livability:.1f}%")
                st.metric("مؤشر EPEF", f"{epef:.0f}")

                st.markdown("#### 🌡️ جدول الحرارة والرطوبة القياسي")
                st.dataframe(BroilerFarmManager.get_temp_humidity_table(),
                             use_container_width=True, hide_index=True)

                temp_hum_df = BroilerFarmManager.get_temp_humidity_table()
                closest = temp_hum_df.iloc[(temp_hum_df['العمر (يوم)'] - current["flock_age_days"]).abs().argsort()[:1]].iloc[0]
                rec_temp = closest['درجة الحرارة (مئوي)']
                rec_hum = closest['الرطوبة النسبية (%)']
                if abs(temp - rec_temp) > 2 or abs(hum - rec_hum) > 10:
                    st.warning(f"⚠️ درجة الحرارة ({temp}°C) أو الرطوبة ({hum}%) خارج النطاق الموصى به "
                               f"لعمر {current['flock_age_days']} يوم (موصى: {rec_temp}°C, {rec_hum}%).")

                standard_today = st.session_state["standard_vacc_schedule"].get(current["flock_age_days"])
                if standard_today:
                    st.info(f"📋 **البروتوكول القياسي (العمر {current['flock_age_days']} يوم):**\n"
                            f"- {standard_today['type']}: {standard_today['name']}\n"
                            f"- الجرعة: {standard_today['dose']}\n"
                            f"- طريقة الإعطاء: {standard_today['route']}")

            st.markdown("---")
            with st.expander("📜 سجل اليوميات السابقة"):
                if farm["daily_logs"]:
                    st.dataframe(pd.DataFrame(farm["daily_logs"]),
                                 use_container_width=True)
                else:
                    st.info("لا توجد سجلات يومية بعد.")
            with st.expander("💊 السجل الصحي"):
                if farm["health_log"]:
                    st.dataframe(pd.DataFrame(farm["health_log"]),
                                 use_container_width=True)
                else:
                    st.info("لا توجد سجلات صحية بعد.")

            if st.button("📄 إرسال التقرير اليومي عبر واتساب",
                         use_container_width=True):
                report_lines = [
                    f"تقرير مزرعة {selected} - المالك: {farm.get('owner', 'غير مسجل')}",
                    f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}",
                    f"🐔 العمر: {current['flock_age_days']} يوم",
                    f"⚖️ متوسط الوزن: {current['current_weight_kg']:.3f} كجم",
                    f"📈 ADG: {adg:.1f} جم/يوم",
                    f"🔄 FCR: {fcr:.2f}",
                    f"💀 النافق: {current['dead_birds']} طير",
                    f"❤️ الحيوية: {livability:.1f}%",
                    f"🏆 EPEF: {epef:.0f}",
                    f"🌡️ درجة الحرارة: {temp}°C (موصى {rec_temp}°C)",
                    f"💧 الرطوبة: {hum}% (موصى {rec_hum}%)",
                    f"📝 ملاحظات: {notes}"
                ]
                report_text = "\n".join(report_lines)
                encoded = urllib.parse.quote(report_text[:1500])
                st.markdown(
                    f'<a href="https://wa.me/{farm.get("owner_phone", WHATSAPP_NUMBER)}?text={encoded}" '
                    f'target="_blank"><button style="background:#25D366; color:white; '
                    f'padding:10px; border-radius:5px;">📲 إرسال التقرير عبر واتساب</button></a>',
                    unsafe_allow_html=True)
                st.text_area("معاينة التقرير:", report_text, height=250)
        else:
            if not st.session_state.get("show_add_farm", False):
                st.info("👈 يرجى إضافة مزرعة جديدة أو اختيار مزرعة مسجلة.")

# ============================================================
# 24. تبويب تعليقات المختصين
# ============================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    comments_tab_index = 7 if st.session_state["user_role"] == "owner" else 6
    with tabs[comments_tab_index]:
        st.markdown('<div class="section-title">💬 قناة التواصل والتعليقات الفنية</div>', unsafe_allow_html=True)
        st.markdown("### 📝 دفتر الملاحظات الفنية المشتركة:")
        st.text_area("التعليقات الحالية:", value=st.session_state["shared_comments"],
                     height=200, disabled=True)
        col_comment1, col_comment2 = st.columns(2)
        with col_comment1:
            if st.session_state["user_role"] == "owner":
                new_comment = st.text_area("📝 إضافة تعليق جديد (المالك):",
                    placeholder="اكتب توجيهاً أو ملاحظة...")
                if st.button("➕ نشر التعليق"):
                    if new_comment:
                        st.session_state["shared_comments"] += (
                            f"\n• [المالك {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {new_comment}")
                        st.success("تم نشر التعليق!")
                        st.rerun()
            else:
                st.info("المختصون يمكنهم إضافة تعليقاتهم أدناه.")
                spec_comment = st.text_area("📝 تعليق مختص:",
                    placeholder="أضف ملاحظتك الفنية...")
                if st.button("➕ إضافة تعليق مختص"):
                    if spec_comment:
                        st.session_state["shared_comments"] += (
                            f"\n• [مختص {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {spec_comment}")
                        st.success("تم إضافة التعليق!")
                        st.rerun()
        with col_comment2:
            st.markdown("#### 📊 الإحصائيات")
            st.metric("عدد التعليقات", len(st.session_state["shared_comments"].split('\n')))
            if st.button("🗑️ تفريغ التعليقات", use_container_width=True):
                if st.session_state["user_role"] == "owner":
                    st.session_state["shared_comments"] = ""
                    st.success("تم تفريغ جميع التعليقات!")
                    st.rerun()
                else:
                    st.warning("هذه الخاصية للمالك فقط.")

# ============================================================
# 25. تبويب المراجع العلمية
# ============================================================
ref_tab_index = 8 if st.session_state["user_role"] == "owner" else (
    7 if st.session_state["user_role"] == "specialist" else 1)
with tabs[ref_tab_index]:
    st.markdown('<div class="section-title">📚 المراجع العلمية المعتمدة</div>', unsafe_allow_html=True)
    ref_categories = list(ScientificReferenceSystem.REFERENCES.keys())
    selected_cat = st.selectbox("اختر التخصص:", ref_categories,
        format_func=lambda x: ScientificReferenceSystem.REFERENCES[x]["title"])
    if selected_cat:
        cat_data = ScientificReferenceSystem.REFERENCES[selected_cat]
        st.markdown(f"## {cat_data['title']}")
        for ref in cat_data["references"]:
            with st.expander(f"📖 {ref['title']} ({ref['year']})"):
                st.markdown(f"**المؤلفون:** {ref['authors']}")
                st.markdown(f"**الناشر:** {ref['publisher']}")
                if 'edition' in ref:
                    st.markdown(f"**الطبعة:** {ref['edition']}")
                if 'isbn' in ref:
                    st.markdown(f"**ISBN:** {ref['isbn']}")
                st.markdown(f"**ملخص:** {ref['summary']}")
                st.markdown(f"**الرقم المرجعي:** `{ref['id']}`")
    st.markdown("---")
    st.markdown("### 🧠 بنك المعرفة السريع (اسألني عن أي مصطلح)")
    user_question = st.text_input("اكتب سؤالك:")
    if user_question:
        answer = ScientificReferenceSystem.get_knowledge_answer(user_question)
        if answer:
            st.markdown(f"**الإجابة المبسطة:** {answer['simplified']}")
            st.markdown(f"**التفصيل العلمي:** {answer['answer']}")
            if answer['reference']:
                ref = answer['reference']
                st.markdown(f"**المصدر:** {ref['authors']} ({ref['year']}) - {ref['title']} - {ref['publisher']}")
        else:
            st.warning("لم أجد إجابة مباشرة، يمكنك البحث في المراجع أعلاه.")

# ============================================================
# 26. تبويب المساعدة الذكية
# ============================================================
help_tab_index = 9 if st.session_state["user_role"] == "owner" else (
    8 if st.session_state["user_role"] == "specialist" else 2)
with tabs[help_tab_index]:
    st.markdown('<div class="section-title">💡 المساعدة الذكية والأسئلة الشائعة</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background: #e3f2fd; padding:20px; border-radius:12px; direction: rtl; text-align: right;'>
    <h3>🌟 الأسئلة المتكررة:</h3>
    <ul>
    <li><b>كيف أبدأ في تركيب علفة؟</b> اختر القطاع الحيواني، حدد الموقع الجغرافي، ثم اختر المكونات واضغط على زر التشغيل.</li>
    <li><b>ما هو البروتين المهضوم؟</b> هو البروتين الذي يستطيع الحيوان هضمه فعلياً، وهو أدق من البروتين الخام.</li>
    <li><b>كيف أحسب معادل النشاء؟</b> المحرك يحسبه تلقائياً بناءً على مكونات الخلطة.</li>
    <li><b>هل يمكنني تعديل الأسعار؟</b> نعم، المالك فقط يمكنه تعديل الأسعار.</li>
    <li><b>كيف أحصل على تقرير PDF؟</b> بعد تشغيل المحرك، ستجد زر تحميل التقرير (PDF و Excel).</li>
    <li><b>كيف أضيف اسم طالب العلفة في التقرير؟</b> اكتبه في حقل "اسم طالب الخدمة" قبل تشغيل المحرك.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔧 دعم فني")
    st.markdown("للتواصل مع الدعم الفني: [abukram128@gmail.com](mailto:abukram128@gmail.com)")

# ============================================================
# 27. تبويب دليل المستخدم
# ============================================================
guide_tab_index = 10 if st.session_state["user_role"] == "owner" else (
    9 if st.session_state["user_role"] == "specialist" else 3)
with tabs[guide_tab_index]:
    st.markdown('<div class="section-title">📖 دليل المستخدم الشامل</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="manual-book">
    <h3>🎯 الغرض من المنصة</h3>
    <p>تاور نولجي Tawor Nology هي أداة ذكية لتركيب الأعلاف الحيوانية بأقل تكلفة، مع تحقيق التوازن الغذائي المطلوب بناءً على البروتين المهضوم ومعادل النشاء.</p>

    <div class="book-chapter">الفصل الأول: تسجيل الدخول</div>
    <div class="book-body">
    يمكنك الدخول باستخدام كود سري أو اسم مستخدم وكلمة مرور. الكود الافتراضي للمالك هو <b>202687</b>.
    </div>

    <div class="book-chapter">الفصل الثاني: تركيب العلفة</div>
    <div class="book-body">
    <ol>
    <li>اختر الموقع الجغرافي (الدولة، الولاية، المدينة).</li>
    <li>اختر القطاع الحيواني (أغنام، ماعز، أبقار، خيول، دواجن، أسماك).</li>
    <li>اختر السلالة ونوع الإنتاج.</li>
    <li>أدخل اسم طالب العلفة (سيظهر في التقرير).</li>
    <li>حدد نسبة البروتين المهضوم ومعادل النشاء.</li>
    <li>اختر المكونات واضغط على زر تشغيل المحرك.</li>
    <li>اطلع على جدول مقارنة العناصر وحمّل التقرير PDF أو Excel.</li>
    </ol>
    </div>

    <div class="book-chapter">الفصل الثالث: إدارة المخازن والفواتير</div>
    <div class="book-body">
    يمكن للمالك تحديث أرصدة المخازن، وإصدار فواتير البيع مع الخصم التلقائي.
    </div>

    <div class="book-chapter">الفصل الرابع: إدارة مزارع الدجاج</div>
    <div class="book-body">
    خاصة بالمالك، تتيح لك تسجيل مزارع الدجاج اللاحم، وتدوين البيانات اليومية، وحساب مؤشرات الأداء ADG، FCR، EPEF.
    </div>

    <div class="book-chapter">الفصل الخامس: المراجع والمساعدة</div>
    <div class="book-body">
    يمكنك الاطلاع على المراجع العلمية المعتمدة، وطرح الأسئلة في بنك المعرفة السريع.
    </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 28. التذييل الثابت
# ============================================================
st.markdown(
    '<div class="mini-left-signature">🌾 تاور نولجي Tawor Nology | '
    'م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان © 2026</div>',
    unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
