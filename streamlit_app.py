# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 4.0 (الدمج الكامل - مختبر ذكي + معادلات متقدمة + محرك خطي)
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, smtplib, time, urllib.parse, re, io, hashlib, secrets, sqlite3, warnings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
warnings.filterwarnings('ignore')

# ===== الصوت =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ===== OCR =====
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

# ===== PDF =====
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
import matplotlib.pyplot as plt

# ============================================================================
# دوال الصوت
# ============================================================================
def play_audio_from_text(text, lang="ar"):
    if not GTTS_AVAILABLE:
        st.warning("⚠️ مكتبة gTTS غير مثبتة.")
        return
    try:
        tts = gTTS(text=text, lang=lang)
        audio_file = io.BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        audio_b64 = base64.b64encode(audio_file.read()).decode()
        st.components.v1.html(
            f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>',
            height=0
        )
    except Exception as e:
        st.warning(f"⚠️ تعذر تشغيل الصوت: {e}")

def play_surah_fatiha():
    st.markdown('''
    <div style="direction: rtl; text-align: center; padding: 15px; background: linear-gradient(135deg, #f5f0e8, #e8e0d5); border-radius: 15px; border: 2px solid #8B7355; margin-bottom: 20px;">
        <h3 style="color: #2E7D32;">﷽ سورة الفاتحة</h3>
        <audio controls autoplay style="width: 100%; max-width: 400px; margin-top: 10px;">
            <source src="https://server8.mp3quran.net/sds/001.mp3" type="audio/mpeg">
        </audio>
        <p style="font-size: 0.8rem; color: #666;">🎙️ بصوت الشيخ عبد الرحمن السديس</p>
    </div>
    ''', unsafe_allow_html=True)

def guide_section(tab_name, guide_text):
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{guide_text}</div>", unsafe_allow_html=True)
        if st.button(f"🔊 تشغيل الدليل صوتياً ({tab_name})"):
            play_audio_from_text(guide_text)

def play_welcome_audio():
    if GTTS_AVAILABLE:
        play_audio_from_text("مرحباً بك في منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف، تحت إشراف الاختصاصي عبد القادر إسماعيل تاور.")

# ============================================================================
# قاعدة البيانات الموسعة
# ============================================================================
class DatabaseManager:
    def __init__(self, db_path="tower_platform.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT, full_name TEXT, email TEXT, phone TEXT, created_date TEXT)''',
            '''CREATE TABLE IF NOT EXISTS farms (farm_id TEXT PRIMARY KEY, farm_name TEXT UNIQUE, farm_type TEXT, owner_name TEXT, owner_phone TEXT, location TEXT, created_date TEXT, last_updated TEXT)''',
            '''CREATE TABLE IF NOT EXISTS production_cycles (cycle_id TEXT PRIMARY KEY, farm_id TEXT, cycle_type TEXT, start_date TEXT, end_date TEXT, initial_count INTEGER, breed TEXT, target_weight REAL, target_age INTEGER, status TEXT, notes TEXT)''',
            '''CREATE TABLE IF NOT EXISTS daily_records (record_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT, age_days INTEGER, live_birds INTEGER, avg_weight REAL, min_weight REAL, max_weight REAL, feed_consumed REAL, water_consumed REAL, dead_count INTEGER, culled_count INTEGER, temperature REAL, humidity REAL, ventilation_status TEXT, litter_quality TEXT, feed_conversion REAL, mortality_rate REAL, notes TEXT)''',
            '''CREATE TABLE IF NOT EXISTS health_records (health_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT, age_days INTEGER, treatment_type TEXT, treatment_name TEXT, dose REAL, dose_unit TEXT, administration_route TEXT, administered_by TEXT, notes TEXT)''',
            '''CREATE TABLE IF NOT EXISTS performance_comparisons (comparison_id TEXT PRIMARY KEY, cycle_id TEXT, comparison_date TEXT, metric_type TEXT, farm_value REAL, standard_value REAL, deviation REAL, status TEXT)''',
            '''CREATE TABLE IF NOT EXISTS vaccine_alerts (alert_id TEXT PRIMARY KEY, cycle_id TEXT, alert_date TEXT, scheduled_date TEXT, vaccine_name TEXT, vaccine_type TEXT, dose TEXT, route TEXT, status TEXT, sent BOOLEAN DEFAULT 0)''',
            '''CREATE TABLE IF NOT EXISTS feed_formulas (formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT, target_dp REAL, target_se REAL, ingredients TEXT, total_cost REAL, created_by TEXT, created_date TEXT)''',
            '''CREATE TABLE IF NOT EXISTS invoices (invoice_id TEXT PRIMARY KEY, customer_name TEXT, formula_id TEXT, quantity_ton REAL, unit_price REAL, total_price REAL, status TEXT, created_by TEXT, created_date TEXT)''',
            '''CREATE TABLE IF NOT EXISTS price_history (record_id TEXT PRIMARY KEY, ingredient_name TEXT, price REAL, currency TEXT, country TEXT, city TEXT, record_date TEXT, recorded_by TEXT)''',
            '''CREATE TABLE IF NOT EXISTS lab_results (result_id TEXT PRIMARY KEY, sample_name TEXT, sample_type TEXT, cp REAL, dc REAL, se REAL, ndf REAL, adf REAL, ee REAL, ash REAL, moisture REAL, analysis_date TEXT, analyzed_by TEXT, notes TEXT, image_path TEXT)'''
        ]
        for t in tables:
            c.execute(t)
        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data

    def insert_record(self, table, data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        c.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", list(data.values()))
        conn.commit()
        conn.close()
        return True

    def get_records(self, table, conditions=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if conditions:
            where = ' AND '.join([f"{k}=?" for k in conditions.keys()])
            result = c.execute(f"SELECT * FROM {table} WHERE {where}", list(conditions.values()))
        else:
            result = c.execute(f"SELECT * FROM {table}")
        data = result.fetchall()
        conn.close()
        return data

    def update_record(self, table, data, condition):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        where = ' AND '.join([f"{k}=?" for k in condition.keys()])
        c.execute(f"UPDATE {table} SET {set_clause} WHERE {where}", list(data.values()) + list(condition.values()))
        conn.commit()
        conn.close()
        return True

# ============================================================================
# نظام إدارة المزارع
# ============================================================================
class FarmManagementSystem:
    def __init__(self):
        self.db = DatabaseManager()

    def create_farm(self, farm_name, farm_type, owner_name, owner_phone, location=""):
        farm_id = secrets.token_hex(16)
        data = {'farm_id': farm_id, 'farm_name': farm_name, 'farm_type': farm_type,
                'owner_name': owner_name, 'owner_phone': owner_phone, 'location': location,
                'created_date': datetime.now().isoformat(), 'last_updated': datetime.now().isoformat()}
        self.db.insert_record('farms', data)
        return farm_id

    def create_production_cycle(self, farm_id, cycle_type, initial_count, breed, target_weight=0.0, target_age=0):
        cycle_id = secrets.token_hex(16)
        data = {'cycle_id': cycle_id, 'farm_id': farm_id, 'cycle_type': cycle_type,
                'start_date': datetime.now().isoformat(), 'end_date': '', 'initial_count': initial_count,
                'breed': breed, 'target_weight': target_weight, 'target_age': target_age,
                'status': 'active', 'notes': ''}
        self.db.insert_record('production_cycles', data)
        return cycle_id

    def add_daily_record(self, cycle_id, record_data):
        record_id = secrets.token_hex(16)
        live_birds = record_data.get('live_birds', 0)
        avg_weight = record_data.get('avg_weight', 0)
        feed_consumed = record_data.get('feed_consumed', 0)
        dead_count = record_data.get('dead_count', 0)
        initial_count = record_data.get('initial_count', live_birds + dead_count)
        total_gain = live_birds * avg_weight
        feed_conversion = feed_consumed / total_gain if total_gain > 0 else 0
        mortality_rate = (dead_count / initial_count) * 100 if initial_count > 0 else 0
        data = {'record_id': record_id, 'cycle_id': cycle_id, 'record_date': datetime.now().isoformat(),
                'age_days': record_data.get('age_days', 0), 'live_birds': live_birds, 'avg_weight': avg_weight,
                'min_weight': record_data.get('min_weight', avg_weight * 0.9),
                'max_weight': record_data.get('max_weight', avg_weight * 1.1),
                'feed_consumed': feed_consumed, 'water_consumed': record_data.get('water_consumed', 0),
                'dead_count': dead_count, 'culled_count': record_data.get('culled_count', 0),
                'temperature': record_data.get('temperature', 0), 'humidity': record_data.get('humidity', 0),
                'ventilation_status': record_data.get('ventilation_status', 'جيدة'),
                'litter_quality': record_data.get('litter_quality', 'جيدة'),
                'feed_conversion': feed_conversion, 'mortality_rate': mortality_rate,
                'notes': record_data.get('notes', '')}
        self.db.insert_record('daily_records', data)
        return record_id

    def add_health_record(self, cycle_id, health_data):
        health_id = secrets.token_hex(16)
        data = {'health_id': health_id, 'cycle_id': cycle_id, 'record_date': datetime.now().isoformat(),
                'age_days': health_data.get('age_days', 0), 'treatment_type': health_data.get('treatment_type', ''),
                'treatment_name': health_data.get('treatment_name', ''), 'dose': health_data.get('dose', 0),
                'dose_unit': health_data.get('dose_unit', ''),
                'administration_route': health_data.get('administration_route', ''),
                'administered_by': health_data.get('administered_by', ''), 'notes': health_data.get('notes', '')}
        self.db.insert_record('health_records', data)
        return health_id

    def get_active_cycles(self, farm_id=None):
        if farm_id:
            return self.db.get_records('production_cycles', {'farm_id': farm_id, 'status': 'active'})
        return self.db.get_records('production_cycles', {'status': 'active'})

    def close_cycle(self, cycle_id):
        self.db.update_record('production_cycles',
                              {'status': 'completed', 'end_date': datetime.now().isoformat()},
                              {'cycle_id': cycle_id})

    def check_vaccine_alerts(self, cycle_id):
        standard_vaccines = {
            1: {'type': 'فيتامين', 'name': 'فيتامين AD3E', 'dose': '1 مل/لتر', 'route': 'مياه الشرب'},
            7: {'type': 'لقاح', 'name': 'نيوكاسل (Lasota)', 'dose': 'قطرة عين', 'route': 'قطرة عين/أنف'},
            14: {'type': 'لقاح', 'name': 'Gumboro (Intermediate)', 'dose': 'قطرة فم', 'route': 'مياه الشرب'},
            21: {'type': 'دواء', 'name': 'مضاد كوكسيديا (Amprolium)', 'dose': '1 جم/لتر', 'route': 'مياه الشرب'},
            28: {'type': 'فيتامين', 'name': 'فيتامين C + E', 'dose': '0.5 جم/لتر', 'route': 'مياه الشرب'},
            35: {'type': 'لقاح', 'name': 'Gumboro booster', 'dose': 'قطرة فم', 'route': 'مياه الشرب'},
            42: {'type': 'لقاح', 'name': 'نيوكاسل (بخاخ)', 'dose': 'بخاخ', 'route': 'رش'},
        }
        records = self.db.get_records('daily_records', {'cycle_id': cycle_id})
        if not records:
            return []
        latest_age = records[-1][3] if records else 0
        alerts = []
        for age, vaccine in standard_vaccines.items():
            if age >= latest_age and age <= latest_age + 2:
                health_records = self.db.get_records('health_records', {'cycle_id': cycle_id})
                if not [h for h in health_records if h[3] == age and h[4] == vaccine['type']]:
                    alert_id = secrets.token_hex(16)
                    alert_data = {'alert_id': alert_id, 'cycle_id': cycle_id,
                                  'alert_date': datetime.now().isoformat(),
                                  'scheduled_date': (datetime.now() + timedelta(days=1)).isoformat(),
                                  'vaccine_name': vaccine['name'], 'vaccine_type': vaccine['type'],
                                  'dose': vaccine['dose'], 'route': vaccine['route'],
                                  'status': 'pending', 'sent': 0}
                    self.db.insert_record('vaccine_alerts', alert_data)
                    alerts.append(alert_data)
        return alerts

# ============================================================================
# نظام المصادقة
# ============================================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()

    def _create_default_admin(self):
        if not self.db.execute_query("SELECT * FROM users WHERE username='admin'"):
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')

    def create_user(self, username, password, role, full_name, email, phone):
        user_id = secrets.token_hex(16)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.db.insert_record('users', {
            'user_id': user_id, 'username': username, 'password_hash': password_hash,
            'role': role, 'full_name': full_name, 'email': email, 'phone': phone,
            'created_date': datetime.now().isoformat()
        })
        return user_id

    def authenticate(self, username, password):
        users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
        if users:
            user = users[0]
            if user[2] == hashlib.sha256(password.encode()).hexdigest():
                return {'user_id': user[0], 'username': user[1], 'role': user[3],
                        'full_name': user[4], 'email': user[5], 'phone': user[6]}
        return None

# ============================================================================
# التنبؤ بالأسعار
# ============================================================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()

    def get_ingredient_prices(self, ingredient_name, days=30):
        results = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? ORDER BY record_date DESC LIMIT ?",
            (ingredient_name, days))
        return [{'price': r[2], 'record_date': r[6]} for r in results]

    def predict_price(self, ingredient_name, days_ahead=7):
        prices = self.get_ingredient_prices(ingredient_name, 30)
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0}
        price_list = [p['price'] for p in prices]
        weights = np.array(range(1, len(price_list) + 1))
        weighted_avg = np.average(price_list, weights=weights)
        trend = (price_list[0] - price_list[-1]) / len(price_list) if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        return {'prediction': max(0, prediction), 'confidence': min(1, len(price_list) / 30),
                'current_price': price_list[0] if price_list else None,
                'trend': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'}

# ============================================================================
# المراجع العلمية
# ============================================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education",
                 "edition": "7th Edition", "isbn": "978-1408204238",
                 "summary": "المرجع الأساسي في تغذية الحيوان، يغطي جميع الجوانب."},
                {"id": "REF002", "authors": "Cheeke, P.R., Dierenfeld, E.S.", "year": 2010,
                 "title": "Comparative Animal Nutrition and Metabolism", "publisher": "CABI",
                 "isbn": "978-1845936310", "summary": "مقارنة بين آليات التغذية والتمثيل الغذائي."}
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية",
            "references": [
                {"id": "REF003", "authors": "NRC", "year": 2012, "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press", "isbn": "978-0309214230",
                 "summary": "المرجع الرسمي للخنازير."},
                {"id": "REF004", "authors": "NRC", "year": 2001, "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press", "isbn": "978-0309069977",
                 "summary": "المرجع الأساسي في تغذية أبقار الحليب."}
            ]
        },
        "energy_carbohydrates": {
            "title": "الطاقة والكربوهيدرات",
            "references": [
                {"id": "REF006", "authors": "Van Soest, P.J.", "year": 1994,
                 "title": "Nutritional Ecology of the Ruminant", "publisher": "Cornell University Press",
                 "isbn": "978-0801427725", "summary": "المرجع الكلاسيكي في تغذية المجترات."}
            ]
        },
        "minerals_vitamins": {
            "title": "المعادن والفيتامينات",
            "references": [
                {"id": "REF008", "authors": "Underwood, E.J., Suttle, N.F.", "year": 1999,
                 "title": "The Mineral Nutrition of Livestock", "publisher": "CABI",
                 "isbn": "978-0851991283", "summary": "المرجع الشامل في تغذية المعادن."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.", "year": 2009,
                 "title": "Commercial Poultry Nutrition", "publisher": "Nottingham University Press",
                 "isbn": "978-1904761578", "summary": "المرجع العملي في تغذية الدواجن."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.", "year": 1993,
                 "title": "The Ruminant Animal", "publisher": "Waveland Press",
                 "isbn": "978-0881337389", "summary": "المرجع الشامل في فسيولوجيا المجترات."}
            ]
        },
        "sheep_goats": {
            "title": "تغذية الأغنام والماعز",
            "references": [
                {"id": "REF014", "authors": "NRC", "year": 2007,
                 "title": "Nutrient Requirements of Small Ruminants",
                 "publisher": "National Academies Press", "isbn": "978-0309102131",
                 "summary": "المرجع الرسمي للأغنام والماعز."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول",
            "references": [
                {"id": "REF015", "authors": "NRC", "year": 2007,
                 "title": "Nutrient Requirements of Horses", "publisher": "National Academies Press",
                 "isbn": "978-0309102124", "summary": "المرجع الأساسي في تغذية الخيول."}
            ]
        },
        "aquaculture": {
            "title": "تغذية الأسماك",
            "references": [
                {"id": "REF016", "authors": "Halver, J.E., Hardy, R.W.", "year": 2002,
                 "title": "Fish Nutrition", "publisher": "Academic Press",
                 "isbn": "978-0123196521", "summary": "المرجع الشامل في تغذية الأسماك."}
            ]
        },
        "broiler": {
            "title": "إنتاج الدجاج اللاحم",
            "references": [
                {"id": "REF020", "authors": "Ross 308", "year": 2020,
                 "title": "Ross Broiler Management Handbook", "publisher": "Aviagen",
                 "summary": "الدليل الشامل لإدارة الدجاج اللاحم."}
            ]
        },
        "digestible_protein": {
            "title": "البروتين المهضوم",
            "references": [
                {"id": "REF023", "authors": "INRA", "year": 2007,
                 "title": "INRA Feeding System for Ruminants",
                 "publisher": "Wageningen Academic Publishers", "isbn": "978-9086860197",
                 "summary": "النظام الفرنسي لتغذية المجترات."},
                {"id": "REF024", "authors": "Pesti, G.M., Miller, B.R.", "year": 2009,
                 "title": "Least-Cost Feed Formulation", "publisher": "University of Georgia",
                 "summary": "النظرية والتطبيق لتركيب الأعلاف بأقل تكلفة."}
            ]
        }
    }

    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (DP) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم. أدق من البروتين الخام.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (SE) هو مقياس لكمية الطاقة التي يوفرها العلف، مقارنة بالطاقة التي يوفرها النشاء النقي.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس الطاقة في العلف."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "باستخدام محرك الاستمثال الخطي (Linear Programming) لحساب أقل تكلفة مع تحقيق المتطلبات الغذائية.",
            "reference": "REF024",
            "simplified": "برنامج ذكي يحسب أرخص خلطة تلبي احتياجات الحيوان."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل) × 100.",
            "reference": "REF020",
            "simplified": "رقم يعبر عن كفاءة مزرعة الدجاج."
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
                return {"answer": value["answer"], "simplified": value.get("simplified", value["answer"]), "reference": ref}
        return None

# ============================================================================
# المعادلات الإنتاجية المتقدمة (NRC)
# ============================================================================
class AdvancedProductionEquations:
    @staticmethod
    def calculate_milk_protein_requirement(milk_yield_kg, milk_protein_pct=3.3):
        return (milk_yield_kg * (milk_protein_pct / 100)) / 0.65

    @staticmethod
    def calculate_maintenance_protein(weight_kg):
        return 2.5 * (weight_kg ** 0.75)

    @staticmethod
    def calculate_metabolic_protein(weight_kg):
        return 1.2 * (weight_kg ** 0.75)

    @staticmethod
    def calculate_total_protein_for_dairy(weight_kg, milk_yield_kg, milk_fat_pct=3.5, milk_protein_pct=3.3):
        maintenance = AdvancedProductionEquations.calculate_maintenance_protein(weight_kg)
        metabolic = AdvancedProductionEquations.calculate_metabolic_protein(weight_kg)
        production = AdvancedProductionEquations.calculate_milk_protein_requirement(milk_yield_kg, milk_protein_pct)
        total = maintenance + metabolic + production
        return {'maintenance': maintenance, 'metabolic': metabolic, 'production': production, 'total': total,
                'dp_requirement': (total / (weight_kg * 10)) * 100}

    @staticmethod
    def calculate_energy_for_dairy(weight_kg, milk_yield_kg, milk_fat_pct=3.5):
        maintenance = 0.08 * (weight_kg ** 0.75)
        fat_correction = 1 + 0.15 * (milk_fat_pct - 3.5)
        production = 5.3 * milk_yield_kg * fat_correction
        total = maintenance + production
        return {'maintenance_energy': maintenance, 'production_energy': production,
                'total_energy': total, 'se_requirement': total * 10}

    @staticmethod
    def calculate_protein_for_gain(daily_gain_kg, protein_in_gain_pct=18.0):
        return (daily_gain_kg * (protein_in_gain_pct / 100)) / 0.65

    @staticmethod
    def calculate_energy_for_gain(daily_gain_kg, gain_energy_pct=5.0):
        return (daily_gain_kg * gain_energy_pct) / 0.70

    @staticmethod
    def calculate_total_protein_for_fattening(weight_kg, daily_gain_kg):
        maintenance = 2.0 * (weight_kg ** 0.75)
        metabolic = 1.0 * (weight_kg ** 0.75)
        production = AdvancedProductionEquations.calculate_protein_for_gain(daily_gain_kg)
        total = maintenance + metabolic + production
        return {'maintenance': maintenance, 'metabolic': metabolic, 'production': production, 'total': total,
                'dp_requirement': (total / (weight_kg * 8)) * 100}

    @staticmethod
    def calculate_total_energy_for_fattening(weight_kg, daily_gain_kg):
        maintenance = 0.07 * (weight_kg ** 0.75)
        production = AdvancedProductionEquations.calculate_energy_for_gain(daily_gain_kg)
        total = maintenance + production
        return {'maintenance_energy': maintenance, 'production_energy': production,
                'total_energy': total, 'se_requirement': total * 10}

# ============================================================================
# المختبر الذكي
# ============================================================================
class SmartLabSystem:
    def __init__(self):
        self.db = DatabaseManager()
        self.ocr_available = OCR_AVAILABLE or EASYOCR_AVAILABLE
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['ar', 'en'], gpu=False)
            except:
                self.reader = None

    def analyze_image(self, image):
        if not self.ocr_available:
            return None, "مكتبات OCR غير مثبتة."
        results = []
        try:
            if EASYOCR_AVAILABLE and self.reader:
                result = self.reader.readtext(np.array(image))
                for (bbox, text, prob) in result:
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                img = PILImage.open(image) if not isinstance(image, PILImage.Image) else image
                text = pytesseract.image_to_string(img, lang='ara+eng')
                results = text.split('\n')
            return self._parse_ocr_results(results), None
        except Exception as e:
            return None, f"خطأ في تحليل الصورة: {str(e)}"

    def _parse_ocr_results(self, texts):
        data = {'sample_name': '', 'cp': None, 'dc': None, 'se': None, 'ndf': None,
                'adf': None, 'ee': None, 'ash': None, 'moisture': None, 'detected_ingredients': []}
        patterns = {
            'cp': [r'بروتين\s*خام\s*[:=]?\s*([\d.]+)', r'CP\s*[:=]?\s*([\d.]+)'],
            'dc': [r'معامل\s*الهضم\s*[:=]?\s*([\d.]+)', r'DC\s*[:=]?\s*([\d.]+)'],
            'se': [r'معادل\s*النشاء\s*[:=]?\s*([\d.]+)', r'SE\s*[:=]?\s*([\d.]+)'],
            'ndf': [r'NDF\s*[:=]?\s*([\d.]+)'],
            'adf': [r'ADF\s*[:=]?\s*([\d.]+)'],
            'ee': [r'دهن\s*خام\s*[:=]?\s*([\d.]+)', r'EE\s*[:=]?\s*([\d.]+)'],
            'ash': [r'رماد\s*[:=]?\s*([\d.]+)', r'ASH\s*[:=]?\s*([\d.]+)'],
            'moisture': [r'رطوبة\s*[:=]?\s*([\d.]+)']
        }
        for text in texts:
            text_clean = text.strip()
            if 'اسم' in text_clean and not data['sample_name']:
                parts = text_clean.split(':')
                if len(parts) > 1:
                    data['sample_name'] = parts[1].strip()
            for key, pattern_list in patterns.items():
                if data[key] is None:
                    for pattern in pattern_list:
                        match = re.search(pattern, text_clean, re.IGNORECASE)
                        if match:
                            try:
                                data[key] = float(match.group(1))
                                break
                            except:
                                pass
        return data

    def save_lab_result(self, result_data):
        result_id = secrets.token_hex(16)
        data = {'result_id': result_id, 'sample_name': result_data.get('sample_name', ''),
                'sample_type': result_data.get('sample_type', ''), 'cp': result_data.get('cp', 0.0),
                'dc': result_data.get('dc', 0.0), 'se': result_data.get('se', 0.0),
                'ndf': result_data.get('ndf', 0.0), 'adf': result_data.get('adf', 0.0),
                'ee': result_data.get('ee', 0.0), 'ash': result_data.get('ash', 0.0),
                'moisture': result_data.get('moisture', 0.0), 'analysis_date': datetime.now().isoformat(),
                'analyzed_by': result_data.get('analyzed_by', ''), 'notes': result_data.get('notes', ''),
                'image_path': result_data.get('image_path', '')}
        self.db.insert_record('lab_results', data)
        return result_id

    def get_lab_results(self, limit=50):
        return self.db.execute_query("SELECT * FROM lab_results ORDER BY analysis_date DESC LIMIT ?", (limit,))

# ============================================================================
# إعدادات
# ============================================================================
st.set_page_config(page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
                   page_icon="🌾", layout="wide", initial_sidebar_state="collapsed")

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]
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
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except:
                pass
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email):
    if not SENDER_PASSWORD:
        st.error("⚠️ خطأ إعدادات SMTP.")
        return False
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود - منصة تاور العلمية v4.0"
    msg.attach(MIMEText("السلام عليكم، مرفق الكود الكامل للمنصة.", 'plain', 'utf-8'))
    try:
        try:
            with open(__file__, "r", encoding="utf-8") as f:
                code = f.read()
        except NameError:
            code = "# أرشيف داخلي"
        file_hash = hashlib.md5(code.encode()).hexdigest()
        code = f"# Digital Signature: {file_hash}\n# Generated: {datetime.now().isoformat()}\n\n{code}"
        attachment = MIMEText(code, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_platform_v4.py")
        msg.attach(attachment)
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل الإرسال: {e}")
        return False

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text):
        return get_display(arabic_reshaper.reshape(text))

arabic_processor = ArabicTextProcessor()

# ============================================================================
# مولد PDF
# ============================================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass

    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe, ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                                                  alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))
        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        for line in [f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور",
                     f"الموقع الجغرافي: {city}", f"الفصيل المستهدف: {breed}",
                     f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))
        tdata = [[arabic_processor.fix_arabic_text('المعيار'), arabic_processor.fix_arabic_text('القيمة')],
                 [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'), f'{target_dp:.2f}%'],
                 [arabic_processor.fix_arabic_text('معادل النشاء (SE)'), f'{computed_se:.2f}'],
                 [arabic_processor.fix_arabic_text('التكلفة للطن'), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']]
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
                                ('TEXTCOLOR', (0,0), (-1,0), white),
                                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                ('FONTNAME', (0,0), (-1,-1), self.font_name),
                                ('FONTSIZE', (0,0), (-1,-1), 11),
                                ('BACKGROUND', (0,1), (-1,-1), HexColor('#f5f5f5')),
                                ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32'))]))
        story.append(t)
        story.append(Spacer(1, 20))
        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", size=14, color=HexColor('#2e7d32')))
        story.append(Spacer(1, 10))
        ing_data = [[arabic_processor.fix_arabic_text('المكون'), arabic_processor.fix_arabic_text('النسبة %'), arabic_processor.fix_arabic_text('كجم/طن')]]
        for ing, pct in formula.items():
            if pct > 0.01:
                ing_data.append([arabic_processor.fix_arabic_text(ing), f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table(ing_data, colWidths=[200, 150, 150])
        t2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
                                 ('TEXTCOLOR', (0,0), (-1,0), white),
                                 ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                 ('FONTNAME', (0,0), (-1,-1), self.font_name),
                                 ('FONTSIZE', (0,0), (-1,-1), 10),
                                 ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
                                 ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')])]))
        story.append(t2)
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", size=9, align=TA_CENTER, color=HexColor('#666666')))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ============================================================================
# مكتبة الأعلاف الموحدة (من الكودين)
# ============================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0},
        "تفل العنب المجفف": {"CP": 12.0, "DC": 0.50, "SE": 45.0, "NDF": 45.0, "ADF": 30.0, "EE": 5.0, "ASH": 8.0},
        "نخالة الأرز الدهنية": {"CP": 12.5, "DC": 0.70, "SE": 55.0, "NDF": 30.0, "ADF": 15.0, "EE": 15.0, "ASH": 8.0},
        "علف الشعير المستنبت": {"CP": 15.0, "DC": 0.75, "SE": 60.0, "NDF": 25.0, "ADF": 12.0, "EE": 3.0, "ASH": 5.0}
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5},
        "كسب بذرة القطن غير المقشور": {"CP": 35.0, "DC": 0.70, "SE": 48.0, "NDF": 35.0, "ADF": 22.0, "EE": 2.0, "ASH": 7.0},
        "كسب بذور اللفت (كانولا)": {"CP": 38.0, "DC": 0.82, "SE": 62.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 7.5},
        "كسب زهرة الشمس الكامل": {"CP": 30.0, "DC": 0.74, "SE": 40.0, "NDF": 42.0, "ADF": 28.0, "EE": 3.0, "ASH": 6.0}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "مخلفات مصانع البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0, "EE": 12.0, "ASH": 3.0},
        "قش الأرز المعالج": {"CP": 4.0, "DC": 0.40, "SE": 25.0, "NDF": 65.0, "ADF": 40.0, "EE": 1.5, "ASH": 12.0}
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
        "بروتين مصل الحليب (WPC)": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0},
        "بروتين الدم المجفف": {"CP": 85.0, "DC": 0.92, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.5, "ASH": 5.0}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان نقي": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1},
        "فالين نقي": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "كبريتات الحديدوز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0},
        "مستخلص الخمائر MOS": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0},
        "كلوريد الكولين": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 75.0}
    }
}

# ============================================================================
# أسعار المدن والمخازن
# ============================================================================
CITY_PRICES_FILE = "city_prices.json"
def load_city_prices():
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

CITY_CUSTOM_PRICES = load_city_prices()

class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for items in BIG_FEEDS_LIBRARY.values():
                for ing in items:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0, "min_threshold": 5.0, "unit": "طن",
                        "last_updated": datetime.now().isoformat(), "supplier": "غير محدد"}

    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"] if isinstance(data, dict) else data
            threshold = data.get("min_threshold", 5.0) if isinstance(data, dict) else 5.0
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings

InventoryManager.initialize_inventory()

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين ($)": 1350.0, "أبقار كنانة وبطانة ($)": 900.0,
        "ضأن محلي ($)": 180.0, "ماعز نوبي ($)": 130.0,
        "خيول عربية أصيلة ($)": 4500.0, "كتكوت لاحم يوم ($)": 0.65, "دجاج بياض بشاير ($)": 5.50}
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 ($)": 4.20,
        "لتر حليب خام ($)": 0.90, "كيلو جبن أبيض ($)": 5.00, "كيلو جبن شيدر ($)": 8.50}
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = (
        "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا.\n"
        "• [ملاحظة مختص]: تم مراجعة جودة كسب زهرة الشمس المتاح بالأسواق.\n")

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "LIBYA": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD"}
}

class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country, state_or_region, city):
        feed_prices = {ing: 230.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
        base_prices = {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
            "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0,
            "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0,
            "كسب بذور القطن (مقشور)": 290.0, "نخالة قمح (ردة)": 150.0,
            "البرسيم الجاف (الدريس)": 170.0, "مولاس قصب السكر": 120.0,
            "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0,
            "مركزات خيول ومجترات": 600.0, "الحجر الجيري (بودرة بلاط)": 40.0,
            "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام": 30.0,
            "مضاد سموم فطرية": 950.0, "بيكربونات الصوديوم": 340.0,
            "خميرة الخبز (Yeast)": 450.0, "يوريا علفية": 350.0
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

# ============================================================================
# حالة الجلسة
# ============================================================================
defaults = {
    "approved": False, "user_role": None, "login_welcome_shown": False,
    "login_attempts": 0, "last_login_time": None, "session_token": None,
    "farms": {}, "selected_farm_id": None, "selected_cycle_id": None,
    "whatsapp_alerts_sent": {}, "query_history": [], "audio_played": False,
    "advanced_dp": None, "advanced_se": None,
    "active_formula": {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0},
    "active_cp_tag": 12.0, "active_se_tag": 65.0,
    "active_breed_tag": "سلالة عامة",
    "active_animal_img": ANIMAL_IMAGES_RESOURCES["عام"],
    "active_stage_title": "إنتاج عام", "computed_ton_cost": 280.0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "lab_system" not in st.session_state:
    try:
        st.session_state["lab_system"] = SmartLabSystem()
    except:
        st.session_state["lab_system"] = None

farm_system = FarmManagementSystem()

def load_farms_from_db():
    farms = farm_system.db.get_records('farms')
    for farm in farms:
        fid = farm[0]
        if fid not in st.session_state["farms"]:
            st.session_state["farms"][fid] = {
                'farm_name': farm[1], 'farm_type': farm[2], 'owner_name': farm[3],
                'owner_phone': farm[4], 'location': farm[5], 'created_date': farm[6]}

if not st.session_state["farms"]:
    load_farms_from_db()

def send_whatsapp_broiler_alert(phone_number, message):
    encoded = urllib.parse.quote(message)
    url = f"https://wa.me/{phone_number}?text={encoded}"
    st.markdown(f"<div style='background:#e8f5e9; padding:10px; border-radius:8px; direction:rtl;'>📲 <b>تنبيه واتساب:</b> <a href='{url}' target='_blank'>اضغط للإرسال</a><br>{message}</div>", unsafe_allow_html=True)

# ============================================================================
# CSS
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Cairo', 'Tajawal', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
    background-size: cover; background-position: center; background-attachment: fixed;
}
.stApp { background: transparent; }
.main-box {
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px; border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
    margin-bottom: 50px; backdrop-filter: blur(5px);
}
h1, h2, h3, h4, h5, p, span, li, div, label, .stMarkdown { color: #1a1a1a !important; text-shadow: none !important; }
.formula-item {
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(232,245,233,0.95) 100%);
    padding: 15px 20px; border-radius: 12px; margin-bottom: 10px;
    font-weight: bold; color: #1b5e20 !important;
    border-right: 5px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    text-align: right; transition: transform 0.3s ease;
}
.formula-item:hover { transform: translateX(-5px); }
.section-title {
    color: #1b5e20 !important; border-right: 6px solid #2e7d32;
    padding-right: 15px; text-align: right; font-size: 1.5rem; font-weight: bold;
    margin: 30px 0 20px 0;
    background: linear-gradient(to left, rgba(46,125,50,0.1), transparent);
    padding: 10px 15px; border-radius: 8px;
}
.sack-tag {
    border: 3px dashed #1b5e20; padding: 30px; border-radius: 15px;
    background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
    direction: rtl; text-align: right; box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
}
.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%; object-fit: cover;
    border: 4px solid #d4af37; box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
    display: block; margin: 0 auto; transition: transform 0.3s ease;
}
.profile-img-style:hover { transform: scale(1.05); }
.animal-banner-img {
    width: 100%; max-height: 200px; object-fit: cover; border-radius: 12px;
    margin-bottom: 20px; border: 3px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
}
.mini-left-signature {
    position: fixed; left: 20px; bottom: 20px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 8px 20px; font-size: 0.85rem;
    border-radius: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    z-index: 9999; direction: rtl; backdrop-filter: blur(5px);
}
.stock-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 8px 12px; border-radius: 8px; color: #c62828 !important;
    font-weight: bold; border: 1px solid #ef5350;
}
.stock-normal {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 8px 12px; border-radius: 8px; color: #2e7d32 !important; border: 1px solid #66bb6a;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 12px; border-right: 5px solid #2e7d32;
    margin-bottom: 20px; direction: rtl; text-align: right;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}
.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 15px; border-radius: 12px; border-right: 5px solid #f57c00;
    margin-bottom: 15px; direction: rtl; text-align: right;
    color: #e65100 !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}
.manual-book {
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    padding: 35px; border-radius: 15px; border: 1px solid #e0e0e0;
    box-shadow: 0px 8px 30px rgba(0,0,0,0.08); direction: rtl; text-align: right;
}
.book-chapter {
    background: linear-gradient(135deg, #1a237e, #283593);
    color: #ffffff !important; padding: 15px 20px; border-radius: 10px;
    font-weight: bold; margin-top: 25px; font-size: 1.2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.book-body {
    padding: 20px 25px; font-size: 1.1rem; line-height: 1.8;
    color: #2c3e50 !important; border-left: 4px solid #3498db;
    margin-bottom: 20px; background: linear-gradient(to right, #f8f9fa, #ffffff);
    border-radius: 0 10px 10px 0; box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
}
.metric-card {
    background: white; padding: 20px; border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1); text-align: center;
    transition: transform 0.3s ease;
}
.metric-card:hover { transform: translateY(-5px); box-shadow: 0px 8px 30px rgba(0,0,0,0.15); }
.equation-box {
    background: linear-gradient(135deg, #f3e5f5, #e1bee7);
    padding: 15px 20px; border-radius: 12px; border-right: 5px solid #7b1fa2;
    margin: 10px 0; direction: rtl; text-align: right;
    font-family: 'Courier New', monospace;
}
.stButton > button {
    color: #1a1a1a !important; background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important; font-weight: bold !important;
}
.stButton > button:hover { background-color: #c8e6c9 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# بوابة الدخول
# ============================================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.error(f"🔒 قفل مؤقت. المتبقي {LOCKOUT_TIME - time_diff} ثانية")
                st.stop()
            else:
                st.session_state["login_attempts"] = 0

    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    play_surah_fatiha()
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابة الدخول الذكية</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>منصة تاور العلمية v4.0 - للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{qr_b64}" width="150"></div>', unsafe_allow_html=True)
    except:
        pass

    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)

    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 كود الدخول:", type="password")
        if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
            if input_code.strip() in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = CODES_DB[input_code.strip()]["role"]
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                st.error(f"❌ كود غير صحيح. متبقي {MAX_LOGIN_ATTEMPTS - st.session_state['login_attempts']}")
    else:
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
            user = AuthManager().authenticate(username, password)
            if user:
                st.session_state["approved"] = True
                st.session_state["user_role"] = user['role']
                st.session_state["user"] = user
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                st.error(f"❌ بيانات غير صحيحة. متبقي {MAX_LOGIN_ATTEMPTS - st.session_state['login_attempts']}")
        st.caption("💡 الافتراضي: admin / admin123")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state["approved"] and not st.session_state.get("audio_played", False):
    play_welcome_audio()
    st.session_state["audio_played"] = True

if not st.session_state["login_welcome_shown"]:
    role_msgs = {"owner": "👋 مرحباً بك الاختصاصي م. عبد القادر إسماعيل تاور",
                 "specialist": "🔬 أهلاً بالزملاء المختصين",
                 "breeder": "🚜 أهلاً بالمربين"}
    st.toast(role_msgs.get(st.session_state["user_role"], "مرحباً"), icon="🌾")
    st.session_state["login_welcome_shown"] = True

# ============================================================================
# الواجهة الرئيسية
# ============================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# زر إرسال الكود للمالك
if st.session_state["user_role"] == "owner":
    with st.expander("📧 إرسال السورس كود إلى البريد", expanded=False):
        target_email = st.text_input("البريد:", value=OWNER_EMAIL, key="mail_recipient")
        if st.button("📤 إرسال الكود"):
            if send_code_to_mail(target_email):
                st.success(f"✅ تم الإرسال إلى {target_email}")

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_info = {"owner": "الاختصاصي م. عبد القادر إسماعيل تاور 👑",
                 "specialist": "المختص والزملاء 👨‍🔬",
                 "breeder": "المربي 🌾"}
    st.markdown(f"""<div style='text-align:left; font-size:0.9rem; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); padding:10px; border-radius:10px;'>
    الحساب: <b>{role_info.get(st.session_state["user_role"], "مستخدم")}</b><br>
    <small>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></div>""", unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory", "farms", "lab_system"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    img = img_base64 or None
    if img:
        st.markdown(f'<img src="data:image/jpeg;base64,{img}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color:#1b5e20; text-align:right;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>v4.0 - محرك خطي + مختبر ذكي + معادلات NRC</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#c62828; text-align:right;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)

# ============================================================================
# التبويبات
# ============================================================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية", "🧪 المختبر الذكي",
        "🐔 إدارة المزارع والدورات", "📊 بورصة الأسعار",
        "🏭 إدارة المستودعات", "🧾 التسويق والفواتير",
        "🖨️ مصمم الديباجة", "📈 التحليلات المتقدمة",
        "💬 تعليقات المختصين", "📚 المراجع العلمية",
        "💡 المساعدة الذكية", "📖 دليل المستخدم"
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية", "🧪 المختبر الذكي",
        "🐔 إدارة المزارع والدورات", "📊 بورصة الأسعار",
        "🏭 إدارة المستودعات", "🧾 التسويق والفواتير",
        "🖨️ مصمم الديباجة", "📈 التحليلات المتقدمة",
        "💬 تعليقات المختصين", "📚 المراجع العلمية",
        "💡 المساعدة الذكية", "📖 دليل المستخدم"
    ]
else:
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "🧪 المختبر الذكي",
                   "📚 المراجع العلمية", "💡 المساعدة الذكية", "📖 دليل المستخدم"]

tabs = st.tabs(tabs_titles)

# ============================================================================
# أدلة
# ============================================================================
guides = {
    "النمذجة": "اختر الموقع والقطاع والمكونات، ثم شغّل المحرك. يمكنك أيضاً استخدام المعادلات الإنتاجية المتقدمة (NRC) لحساب الاحتياجات من الوزن الحي والإنتاج.",
    "المختبر": "ارفع صورة تركيبة علفية، وسيستخرج النظام البيانات الغذائية (CP، DC، SE، NDF، ADF) تلقائياً. يمكنك حفظ النتائج وإعادة استخدامها.",
    "المزارع": "أنشئ مزارع ودورات إنتاجية، سجّل البيانات اليومية والتحصينات، وتلقَّ تنبيهات واتساب تلقائية.",
    "البورصة": "أسعار الماشية والمنتجات الحيوانية قابلة للتحديث من المالك.",
    "المستودعات": "تتبع أرصدة المواد العلفية مع تنبيهات المخزون المنخفض.",
    "الفواتير": "إصدار فواتير مع خصم تلقائي للمكونات من المستودع.",
    "الديباجة": "صمم ديباجة جوالات الأعلاف مع الصور والشعارات.",
    "التحليلات": "مؤشرات الأداء، تنبؤات الأسعار، ورسوم بيانية.",
    "التعليقات": "قناة لتبادل الخبرات بين المختصين.",
    "المراجع": "مراجع علمية موثقة وبنك معرفة.",
    "المساعدة": "أسئلة شائعة ودعم فني.",
    "الدليل": "دليل شامل خطوة بخطوة."
}

# ============================================================================
# تبويب 0: النمذجة
# ============================================================================
with tabs[0]:
    guide_section("النمذجة والحسابات العلفية", guides["النمذجة"])
    st.markdown('<div class="section-title">🌍 تحديد الموقع الجغرافي</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        user_country = st.selectbox("الدولة:", ["السودان", "LIBYA", "مصر", "باقي دول العالم"])
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate, local_sym = c_info["rate"], c_info["sym"]

    chosen_state = "عام"
    with c2:
        if user_country == "السودان":
            chosen_state = st.selectbox("الولاية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف",
                                                     "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان",
                                                     "إقليم النيل الأزرق", "ولاية البحر الأحمر", "ولاية نهر النيل"])
        elif user_country == "LIBYA":
            chosen_state = st.selectbox("الإقليم:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else:
            chosen_state = st.selectbox("الإقليم:", ["المركز الرئيسي", "الأسواق المفتوحة"])

    with c3:
        cities_map = {
            "السودان": {"ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
                        "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"],
                        "ولاية القضارف": ["القضارف", "الفاو"],
                        "ولاية شمال كردفان": ["الأبيض", "بارا", "أم روابة"],
                        "ولاية جنوب كردفان": ["كادوقلي", "الدلنج"],
                        "ولاية غرب كردفان": ["الفوله", "النهود", "بابنوسة"],
                        "إقليم النيل الأزرق": ["الدمازين", "الروصيرص"],
                        "ولاية البحر الأحمر": ["بورتسودان", "سواكن"],
                        "ولاية نهر النيل": ["شندي", "عطبرة", "الدامر"]},
            "LIBYA": {"المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء", "درنة"],
                      "المنطقة الغربية": ["طرابلس", "مصراتة", "الزاوية"],
                      "المنطقة الجنوبية": ["سبها", "مرزق", "غات"]}
        }
        if user_country in ["السودان", "LIBYA"]:
            user_city = st.selectbox("المدينة:", cities_map.get(user_country, {}).get(chosen_state, ["عام"]))
        else:
            user_city = st.text_input("المدينة:", "طبرق")

    live_prices = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)

    # البورصة
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية في {user_city}:</b><br>' +
                    "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> ({v*local_rate:,.2f} {local_sym})'
                                 for k, v in st.session_state["global_livestock_prices"].items()]) + "</div>", unsafe_allow_html=True)
    with col_v2:
        st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات في {user_city}:</b><br>' +
                    "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> ({v*local_rate:,.2f} {local_sym})'
                                 for k, v in st.session_state["global_products_prices"].items()]) + "</div>", unsafe_allow_html=True)

    # القطاع
    st.markdown('<div class="section-title">⚖️ القطاع والإنتاج</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec:
        main_sector = st.selectbox("القطاع:", ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها",
                                                "الخيول والفروسية", "الطيور والسمان", "الأسماك والأحياء المائية"])

    show_measurements, weight_factor, feed_factor = False, 10000, 0.02
    default_dp, default_se = 11.0, 60.0
    dynamic_img_key, chosen_concentrate = "عام", None
    gender_option = "إناث"

    if main_sector in ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها"]:
        with col_sec:
            gender_option = st.radio("الجنس:", ["ذكور (تسمين)", "إناث (حليب/أمهات)"], horizontal=True)

    with col_sub:
        if main_sector == "الأغنام وسلالاتها 🐏":
            sub_type = st.selectbox("السلالة:", ["الضأن الصحراوي السوداني", "البربري", "النعيمي", "محلية/هجين"])
            dynamic_img_key = "أغنام"; show_measurements = True
            weight_factor, feed_factor, chosen_concentrate = 15500, 0.035, "مركزات خيول ومجترات"
        elif main_sector == "الماعز وسلالاتها":
            sub_type = st.selectbox("السلالة:", ["الماعز النوبي", "الصحراوي", "بور/محسن"])
            dynamic_img_key = "ماعز"; show_measurements = True
            weight_factor, feed_factor, chosen_concentrate = 15000, 0.032, "مركزات خيول ومجترات"
        elif main_sector == "الأبقار وسلالاتها":
            sub_type = st.selectbox("السلالة:", ["كنانة", "بطانة", "هولشتاين/محسن"])
            dynamic_img_key = "أبقار"; show_measurements = True
            weight_factor, feed_factor, chosen_concentrate = 10838, 0.025, "مركزات خيول ومجترات"
        elif main_sector == "الخيول والفروسية":
            sub_type = st.selectbox("السلالة:", ["خيل عربي أصيل", "ثوروبريد", "محلية هجين"])
            dynamic_img_key = "خيول"; show_measurements = True
            weight_factor, feed_factor, chosen_concentrate = 11877, 0.022, "مركزات خيول ومجترات"
        elif main_sector == "الطيور والسمان":
            sub_type = st.selectbox("النوع:", ["طائر السمان", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"])
            dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"
            chosen_concentrate = "مركزات دواجن وسمان"
        else:
            sub_type = st.selectbox("النوع:", ["البلطي النيلي", "القرموط"])
            dynamic_img_key = "أسماك"; chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

    with col_prod:
        if main_sector == "الأغنام وسلالاتها 🐏":
            if gender_option == "ذكور (تسمين)":
                prod_stage = st.selectbox("الإنتاج:", ["تسمين حملان مكثف", "حملان تيد/كباش"])
                default_dp = 12.0 if "مكثف" in prod_stage else 9.5
                default_se = 64.0 if "مكثف" in prod_stage else 58.0
            else:
                prod_stage = st.selectbox("الإنتاج:", ["نعاج مرضعات", "نعاج حامل", "نعاج جافة/صيانة"])
                default_dp = 12.8 if "مرضعات" in prod_stage else (10.5 if "حامل" in prod_stage else 8.0)
                default_se = 66.0 if "مرضعات" in prod_stage else (60.0 if "حامل" in prod_stage else 50.0)
        elif main_sector == "الماعز وسلالاتها":
            if gender_option == "ذكور (تسمين)":
                prod_stage = st.selectbox("الإنتاج:", ["تسمين جديان", "تيوس للتسويق"])
                default_dp = 11.5 if "جديان" in prod_stage else 9.0
                default_se = 62.0 if "جديان" in prod_stage else 55.0
            else:
                prod_stage = st.selectbox("الإنتاج:", ["عنزات حلابة", "عنزات حامل", "صيانة"])
                default_dp = 12.8 if "حلابة" in prod_stage else (10.0 if "حامل" in prod_stage else 7.8)
                default_se = 65.0 if "حلابة" in prod_stage else (58.0 if "حامل" in prod_stage else 48.0)
        elif main_sector == "الأبقار وسلالاتها":
            prod_stage = st.selectbox("الإنتاج:", ["إنتاج حليب وغزارة", "تسمين عجول"])
            default_dp = 12.5 if "حليب" in prod_stage else 10.0
            default_se = 68.0 if "حليب" in prod_stage else 65.0
        elif main_sector == "الخيول والفروسية":
            prod_stage = st.selectbox("الإنتاج:", ["خيول رياضة", "أمهار نامية", "فرسات مرضعات"])
            default_dp = 12.5 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 9.5
            default_se = 65.0 if "رياضة" in prod_stage else 60.0
        elif main_sector == "الطيور والسمان":
            if "السمان" in sub_type:
                prod_stage = st.selectbox("الإنتاج:", ["سمان بادي/نامي", "سمان بياض"])
                default_dp = 20.0 if "بادي" in prod_stage else 16.5
                default_se = 72.0 if "بادي" in prod_stage else 68.0
            else:
                prod_stage = st.selectbox("الإنتاج:", ["بادي دواجن", "نامي", "ناهي", "بياض"])
                default_dp = 20.0 if "بادي" in prod_stage else (18.5 if "نامي" in prod_stage else (16.5 if "ناهي" in prod_stage else 15.0))
                default_se = 76.0 if "بادي" in prod_stage else (74.0 if "نامي" in prod_stage else (75.0 if "ناهي" in prod_stage else 70.0))
        else:
            prod_stage = st.selectbox("الإنتاج:", ["بادئ زريعة", "نمو وتسمين"])
            default_dp = 29.5 if "زريعة" in prod_stage else 25.0
            default_se = 70.0

    # ===== المعادلات المتقدمة =====
    use_advanced = main_sector in ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها"]
    if use_advanced:
        st.markdown('<div class="section-title">🧮 المعادلات الإنتاجية المتقدمة (NRC)</div>', unsafe_allow_html=True)
        st.info("📊 حساب الاحتياجات من الوزن الحي والإنتاج الفعلي - المرجع: NRC 2000/2001")

        col_w, col_p = st.columns(2)
        with col_w:
            animal_weight = st.number_input("⚖️ الوزن الحي (كجم):", min_value=10.0,
                                            value=450.0 if "أبقار" in main_sector else 35.0, step=5.0)
        with col_p:
            if "أبقار" in main_sector and "حليب" in prod_stage:
                daily_milk = st.number_input("🥛 إنتاج الحليب (لتر/يوم):", min_value=0.0, value=15.0)
                milk_fat = st.slider("دهن الحليب (%)", 2.5, 6.0, 3.5, 0.1)
                prod_type = "dairy"
            elif (main_sector == "الأغنام وسلالاتها 🐏" or main_sector == "الماعز وسلالاتها") and gender_option == "إناث (حليب/أمهات)":
                daily_milk = st.number_input("🥛 إنتاج الحليب (لتر/يوم):", min_value=0.0, value=2.0)
                milk_fat = st.slider("دهن الحليب (%)", 2.5, 6.0, 4.0, 0.1)
                prod_type = "dairy"
            else:
                daily_gain = st.number_input("📈 الزيادة اليومية (كجم):", min_value=0.0,
                                             value=0.8 if "أبقار" in main_sector else 0.15, step=0.05)
                prod_type = "fattening"

        if st.button("🧮 حساب الاحتياجات الغذائية", type="secondary"):
            if prod_type == "dairy":
                pr = AdvancedProductionEquations.calculate_total_protein_for_dairy(animal_weight, daily_milk, milk_fat)
                er = AdvancedProductionEquations.calculate_energy_for_dairy(animal_weight, daily_milk, milk_fat)
                dp_pct = pr['dp_requirement']
                se_val = er['se_requirement']
                ratio = er['total_energy'] / pr['total'] if pr['total'] > 0 else 0
                st.success(f"📊 **النتائج:** DP = {dp_pct:.2f}% | SE = {se_val:.0f} | SE/DP = {ratio:.2f}")
                st.session_state['advanced_dp'] = dp_pct
                st.session_state['advanced_se'] = se_val
                with st.expander("📐 عرض المعادلات"):
                    st.markdown("""<div class="equation-box"><b>معادلات NRC 2001 للألبان:</b><br>
                    بروتين الإدامة = 2.5 × الوزن<sup>0.75</sup><br>
                    بروتين الأيض = 1.2 × الوزن<sup>0.75</sup><br>
                    بروتين الإنتاج = (الحليب × % بروتين) / 0.65<br>
                    طاقة الإدامة = 0.08 × الوزن<sup>0.75</sup><br>
                    طاقة الإنتاج = 5.3 × الحليب × تصحيح الدهن</div>""", unsafe_allow_html=True)
            else:
                pr = AdvancedProductionEquations.calculate_total_protein_for_fattening(animal_weight, daily_gain)
                er = AdvancedProductionEquations.calculate_total_energy_for_fattening(animal_weight, daily_gain)
                dp_pct = pr['dp_requirement']
                se_val = er['se_requirement']
                ratio = er['total_energy'] / pr['total'] if pr['total'] > 0 else 0
                st.success(f"📊 **النتائج:** DP = {dp_pct:.2f}% | SE = {se_val:.0f} | SE/DP = {ratio:.2f}")
                st.session_state['advanced_dp'] = dp_pct
                st.session_state['advanced_se'] = se_val

        if st.session_state.get('advanced_dp'):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                if st.button("📥 تطبيق DP المحسوب"):
                    st.success(f"✅ DP = {st.session_state['advanced_dp']:.1f}%")
            with col_a2:
                if st.button("📥 تطبيق SE المحسوب"):
                    st.success(f"✅ SE = {st.session_state['advanced_se']:.0f}")

    # القياسات
    if show_measurements:
        st.markdown('<div class="section-title">📐 القياسات الجسدية</div>', unsafe_allow_html=True)
        col_h, col_l, col_ag = st.columns(3)
        with col_h:
            h_girth = st.number_input("محيط الصدر (سم):", value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 75.0)
        with col_l:
            b_length = st.number_input("طول الجسم (سم):", value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 65.0)
        with col_ag:
            a_months = st.number_input("العمر (أشهر):", value=12)
        calc_weight = (h_girth ** 2 * b_length) / weight_factor
        st.success(f"📊 الوزن المتوقع: **{calc_weight:.1f} كجم** | الاحتياج اليومي: **{calc_weight * feed_factor:.2f} كجم**")

    # الحدود المستهدفة
    st.markdown('<div class="section-title">📋 حدود الموازنة الذكية</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    use_cp_basis = st.checkbox("⚡ استخدام CP بدلاً من DP", value=False)
    final_target_dp, final_target_cp = None, None
    if use_cp_basis:
        default_cp = default_dp / 0.82
        with col_p1:
            st.metric("بروتين خام (CP) مقترح:", f"{default_cp:.1f}%")
            if st.checkbox("⚙️ تعديل CP"):
                final_target_cp = st.slider("CP:", 5.0, 60.0, value=float(default_cp))
            else:
                final_target_cp = default_cp
    else:
        with col_p1:
            st.metric("بروتين مهضوم (DP) مقترح:", f"{default_dp}%")
            if st.checkbox("⚙️ تعديل DP"):
                final_target_dp = st.slider("DP:", 5.0, 40.0, value=default_dp)
            else:
                final_target_dp = default_dp
    with col_p2:
        st.metric("معادل النشاء (SE) مقترح:", f"{default_se}")
        if st.checkbox("⚙️ تعديل SE"):
            final_target_se = st.slider("SE:", 10.0, 90.0, value=default_se)
        else:
            final_target_se = default_se

    # اختيار المكونات
    selected_ingredients, ingredient_prices = [], {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded="الحبوب" in cat_name or "الأكساب" in cat_name):
            cols = st.columns(3)
            for idx, ing_name in enumerate(items.keys()):
                with cols[idx % 3]:
                    is_def = ing_name == chosen_concentrate or ing_name in [
                        "ذرة صفراء", "سورجم (فتريتة)", "أمباز الفول السوداني (كسب)",
                        "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام",
                        "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                        "بيكربونات الصوديوم", "مضاد سموم فطرية", "خميرة الخبز (Yeast)"]
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    price = live_prices.get(ing_name, 350.0)
                    if st.session_state["user_role"] == "owner":
                        price = st.number_input(f"$", min_value=5.0, value=float(price), key=f"price_{ing_name}")
                    else:
                        st.caption(f"💰 ${price:.2f}/طن")
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price

    # الإضافات
    fixed_add = {"ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2,
                 "الحجر الجيري (بودرة بلاط)": 2.5 if "بياض" in prod_stage else 1.5,
                 "فوسفات ثنائي الكالسيوم (DCP)": 1.0}
    auto_add, warnings_list = {}, []

    if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاتها", "الأغنام وسلالاتها 🐏"]:
        auto_add["بيكربونات الصوديوم"] = 0.75
        warnings_list.append("🚨 <b>إضافة إلزامية - بيكربونات الصوديوم:</b> 0.75% لمنع التحمض الكرشي.")
    elif main_sector == "الطيور والسمان":
        auto_add["بيكربونات الصوديوم"] = 0.20
    if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
        auto_add["إنزيم الفايتيز"] = 0.05
        warnings_list.append("🚨 <b>إنزيم الفايتيز:</b> 0.05% لتحرير الفسفور النباتي.")
    if "كسب بذور القطن (مقشور)" in selected_ingredients and main_sector == "الطيور والسمان":
        auto_add["كبريتات الحديدوز"] = 0.15
        warnings_list.append("⚠️ <b>كبريتات الحديدوز:</b> 0.15% لربط الجوسيبول.")
    if main_sector == "الطيور والسمان" and any(x in selected_ingredients for x in ["شعير مطحون", "قمح محلي مصنّع"]):
        auto_add["إنزيم NSP"] = 0.08
        warnings_list.append("⚠️ <b>إنزيم NSP:</b> 0.08% لمنع البراز الرطب.")

    all_fixed = {**fixed_add, **auto_add}
    for item in all_fixed:
        if item not in selected_ingredients:
            selected_ingredients.append(item)
            ingredient_prices[item] = live_prices.get(item, 40.0)

    # المحرك الخطي
    if st.button("🚀 تشغيل المحرك الخطي", type="primary", use_container_width=True):
        if len(selected_ingredients) < 2:
            st.warning("⚠️ اختر مكونين على الأقل.")
        else:
            c_vec, cp_row, se_row = [], [], []
            for ing in selected_ingredients:
                c_vec.append(ingredient_prices[ing])
                for cat in BIG_FEEDS_LIBRARY.values():
                    if ing in cat:
                        d = cat[ing]
                        dp_val = d.get("CP", 0) if use_cp_basis else d.get("CP", 0) * d.get("DC", 0)
                        cp_row.append(dp_val)
                        se_row.append(d.get("SE", 0))
                        break

            A_eq = [[1.0] * len(selected_ingredients)]
            b_eq = [100.0]
            A_ub, b_ub = [], []

            A_ub.append([-x for x in cp_row])
            b_ub.append(-(final_target_cp if use_cp_basis else final_target_dp) * 100.0)
            A_ub.append([-x for x in se_row])
            b_ub.append(-final_target_se * 100.0)

            grain_idx = [1.0 if ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة"] else 0.0 for ing in selected_ingredients]
            if sum(grain_idx) > 0:
                A_ub.append([-x for x in grain_idx]); b_ub.append(-50.0)

            bounds = [(all_fixed.get(ing, 0.0), 100.0) for ing in selected_ingredients]

            res = linprog(c_vec, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

            if res.success:
                formula = {selected_ingredients[i]: res.x[i] for i in range(len(selected_ingredients)) if res.x[i] > 0.001}
                computed_dp = sum(res.x[i] * cp_row[i] for i in range(len(selected_ingredients))) / 100
                computed_se = sum(res.x[i] * se_row[i] for i in range(len(selected_ingredients))) / 100
                cost = res.fun

                st.session_state["active_formula"] = formula
                st.session_state["computed_ton_cost"] = cost
                st.session_state["active_cp_tag"] = computed_dp
                st.session_state["active_se_tag"] = computed_se
                st.session_state["active_breed_tag"] = sub_type
                st.session_state["active_stage_title"] = prod_stage

                st.success(f"✅ تم الحل! التكلفة: ${cost:.2f} ({cost * local_rate:,.1f} {local_sym})")

                if warnings_list:
                    for w in warnings_list:
                        st.markdown(f'<div class="warning-card">{w}</div>', unsafe_allow_html=True)

                st.markdown("#### 📋 المكونات:")
                for name, pct in sorted(formula.items(), key=lambda x: -x[1]):
                    st.markdown(f'<div class="formula-item">▪️ <b>{name}:</b> {pct:.2f}% ({pct * 10:.1f} كجم/طن)</div>', unsafe_allow_html=True)

                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("التكلفة", f"${cost:.2f}")
                col_m2.metric("DP المحقق", f"{computed_dp:.2f}%")
                col_m3.metric("SE المحقق", f"{computed_se:.2f}")

                # حفظ + PDF + مشاركة
                col_act1, col_act2, col_act3 = st.columns(3)
                with col_act1:
                    if st.button("💾 حفظ الخلطة"):
                        fid = secrets.token_hex(16)
                        try:
                            farm_system.db.insert_record('feed_formulas', {
                                'formula_id': fid, 'formula_name': f"{sub_type}-{prod_stage}",
                                'animal_type': sub_type, 'target_dp': computed_dp, 'target_se': computed_se,
                                'ingredients': json.dumps(formula, ensure_ascii=False),
                                'total_cost': cost,
                                'created_by': st.session_state.get("user", {}).get("full_name", "مستخدم"),
                                'created_date': datetime.now().isoformat()})
                            st.success("✅ تم الحفظ!")
                        except Exception as e:
                            st.error(f"خطأ: {e}")
                with col_act2:
                    try:
                        pdf = pdf_generator.generate_comprehensive_report(
                            formula, computed_dp, f"{sub_type}-{prod_stage}", cost,
                            user_city, cost * local_rate, local_sym, computed_se)
                        st.download_button("📄 تحميل PDF", pdf,
                                           file_name=f"taour_{datetime.now().strftime('%Y%m%d')}.pdf",
                                           mime="application/pdf")
                    except Exception as e:
                        st.warning(f"PDF: {e}")
                with col_act3:
                    msg = f"خلطة تاور: {sub_type} | DP: {computed_dp:.1f}% | SE: {computed_se:.0f} | ${cost:.2f}/طن"
                    st.link_button("📲 واتساب", f"https://wa.me/?text={urllib.parse.quote(msg)}")

                # رسم
                try:
                    fig, ax = plt.subplots(figsize=(7, 5))
                    names = [n for n, p in formula.items() if p > 0.5]
                    vals = [p for n, p in formula.items() if p > 0.5]
                    ax.pie(vals, labels=names, autopct='%1.1f%%',
                           colors=['#1b5e20', '#2e7d32', '#388e3c', '#43a047', '#4caf50', '#66bb6a'])
                    ax.set_title('توزيع المكونات')
                    st.pyplot(fig)
                except:
                    pass
            else:
                st.error(f"❌ فشل الحل: {res.message}")

# ============================================================================
# تبويب 1: المختبر الذكي
# ============================================================================
with tabs[1]:
    guide_section("المختبر الذكي", guides["المختبر"])
    st.markdown('<div class="section-title">🧪 المختبر الذكي لتحليل الأعلاف</div>', unsafe_allow_html=True)

    if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
        st.warning("⚠️ مكتبات OCR غير مثبتة. قم بتثبيت easyocr أو pytesseract. يمكنك إدخال البيانات يدوياً.")

    uploaded = st.file_uploader("📸 ارفع صورة التركيبة (كتب، أوراق، هاتف)",
                                 type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'])

    if uploaded is not None:
        try:
            image = PILImage.open(uploaded)
            st.image(image, caption="الصورة المرفوعة", use_container_width=True)
        except:
            image = None

        if st.session_state.get("lab_system") and st.button("🔍 تحليل الصورة", type="primary"):
            with st.spinner("جاري التحليل..."):
                result, error = st.session_state["lab_system"].analyze_image(image)
                if error:
                    st.error(f"❌ {error}")
                    result = {}
                else:
                    st.success("✅ تم التحليل!")
                    st.session_state["lab_cp"] = result.get('cp') or 0.0
                    st.session_state["lab_dc"] = result.get('dc') or 0.0
                    st.session_state["lab_se"] = result.get('se') or 0.0
                    st.session_state["lab_ndf"] = result.get('ndf') or 0.0
                    st.session_state["lab_adf"] = result.get('adf') or 0.0
                    st.session_state["lab_ee"] = result.get('ee') or 0.0
                    st.session_state["lab_ash"] = result.get('ash') or 0.0
                    st.session_state["lab_moisture"] = result.get('moisture') or 0.0
                    st.session_state["lab_sample_name"] = result.get('sample_name', '')

    st.markdown("### ✍️ إدخال/تعديل بيانات التحليل")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("اسم العينة:", key="lab_sample_name", value=st.session_state.get("lab_sample_name", ""))
        st.number_input("CP %:", min_value=0.0, value=float(st.session_state.get("lab_cp", 0.0)), step=0.1, key="lab_cp")
        st.number_input("DC:", min_value=0.0, max_value=1.0, value=float(st.session_state.get("lab_dc", 0.0)), step=0.01, key="lab_dc")
        st.number_input("SE:", min_value=0.0, value=float(st.session_state.get("lab_se", 0.0)), step=0.1, key="lab_se")
    with col2:
        st.number_input("NDF %:", min_value=0.0, value=float(st.session_state.get("lab_ndf", 0.0)), step=0.1, key="lab_ndf")
        st.number_input("ADF %:", min_value=0.0, value=float(st.session_state.get("lab_adf", 0.0)), step=0.1, key="lab_adf")
        st.number_input("EE %:", min_value=0.0, value=float(st.session_state.get("lab_ee", 0.0)), step=0.1, key="lab_ee")
        st.number_input("ASH %:", min_value=0.0, value=float(st.session_state.get("lab_ash", 0.0)), step=0.1, key="lab_ash")
        st.number_input("الرطوبة %:", min_value=0.0, value=float(st.session_state.get("lab_moisture", 0.0)), step=0.1, key="lab_moisture")

    st.text_area("ملاحظات:", key="lab_notes")

    if st.button("💾 حفظ نتيجة التحليل", type="secondary"):
        if st.session_state.get("lab_system"):
            lab_data = {
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
                'notes': st.session_state.get('lab_notes', ''),
                'image_path': uploaded.name if uploaded else ''
            }
            rid = st.session_state["lab_system"].save_lab_result(lab_data)
            st.success(f"✅ تم الحفظ! ID: {rid[:8]}")

    st.markdown("---")
    st.markdown("### 📋 نتائج التحاليل السابقة")
    if st.session_state.get("lab_system"):
        results = st.session_state["lab_system"].get_lab_results(20)
        if results:
            df_data = [{'التاريخ': r[10][:16] if r[10] else '', 'العينة': r[1], 'CP': r[3],
                        'DC': r[4], 'SE': r[5], 'NDF': r[6], 'ADF': r[7], 'EE': r[8], 'ASH': r[9]}
                       for r in results]
            st.dataframe(pd.DataFrame(df_data), use_container_width=True)
        else:
            st.info("📭 لا توجد نتائج سابقة.")

# ============================================================================
# تبويب 2: إدارة المزارع
# ============================================================================
if len(tabs) > 2 and st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[2]:
        guide_section("إدارة المزارع والدورات", guides["المزارع"])
        st.markdown('<div class="section-title">🐔 إدارة المزارع والدورات الإنتاجية</div>', unsafe_allow_html=True)

        with st.expander("🏗️ إنشاء مزرعة جديدة"):
            c1, c2, c3 = st.columns(3)
            with c1: farm_name = st.text_input("اسم المزرعة:")
            with c2: farm_type = st.selectbox("النوع:", ["دواجن لاحم", "دواجن بياض", "أبقار", "أغنام", "ماعز", "مختلط"])
            with c3: owner_name = st.text_input("المالك:")
            c4, c5 = st.columns(2)
            with c4: owner_phone = st.text_input("الهاتف:", value=WHATSAPP_NUMBER)
            with c5: location = st.text_input("الموقع:")
            if st.button("➕ إنشاء المزرعة", type="secondary"):
                if farm_name and owner_name:
                    farm_system.create_farm(farm_name, farm_type, owner_name, owner_phone, location)
                    st.session_state["farms"] = {}
                    load_farms_from_db()
                    st.success(f"✅ تم إنشاء '{farm_name}'")
                    st.rerun()
                else:
                    st.warning("⚠️ أدخل اسم المزرعة والمالك.")

        if st.session_state["farms"]:
            st.markdown("#### 🏠 المزارع المسجلة:")
            for fid, fdata in st.session_state["farms"].items():
                with st.expander(f"🏠 {fdata['farm_name']} ({fdata['farm_type']})"):
                    st.markdown(f"**المالك:** {fdata['owner_name']} | **هاتف:** {fdata['owner_phone']}")

                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"➕ دورة جديدة", key=f"cycle_btn_{fid}"):
                            st.session_state["selected_farm_id"] = fid
                    with c2:
                        if st.button(f"🗑️ حذف المزرعة", key=f"del_{fid}"):
                            st.warning("غير متاح بعد")

                    if st.session_state.get("selected_farm_id") == fid:
                        c1, c2, c3 = st.columns(3)
                        with c1: ct = st.selectbox("النوع:", ["لاحم", "بياض"], key=f"ct_{fid}")
                        with c2: ic = st.number_input("العدد:", min_value=1, value=1000, step=100, key=f"ic_{fid}")
                        with c3: br = st.text_input("السلالة:", value="Ross 308", key=f"br_{fid}")
                        if st.button("✅ إنشاء الدورة", key=f"create_{fid}"):
                            cid = farm_system.create_production_cycle(fid, ct, ic, br)
                            st.success(f"✅ تم إنشاء الدورة: {cid[:8]}")
                            st.session_state["selected_farm_id"] = None
                            st.rerun()

        st.markdown("#### 🔄 الدورات النشطة:")
        active = farm_system.get_active_cycles()
        if active:
            for cycle in active:
                cid = cycle[0]
                fname = st.session_state["farms"].get(cycle[1], {}).get("farm_name", "غير معروف")
                st.markdown(f"""
                <div style="background:#f0fdf4; padding:10px; border-radius:8px; border-right:4px solid #16a34a; margin-bottom:5px;">
                <b>الدورة:</b> {cycle[2]} - {cycle[6]} | <b>المزرعة:</b> {fname} | <b>العدد:</b> {cycle[5]}
                </div>""", unsafe_allow_html=True)

                with st.expander(f"📊 تفاصيل الدورة {cid[:8]}"):
                    st.markdown("### 📝 تسجيل بيانات يومية")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        age = st.number_input("العمر (يوم):", min_value=0, value=1, key=f"age_{cid}")
                        live = st.number_input("الطيور الحية:", min_value=0, value=cycle[5], key=f"live_{cid}")
                    with c2:
                        avg_wt = st.number_input("متوسط الوزن (كجم):", min_value=0.0, value=0.045, step=0.005, key=f"wt_{cid}")
                        feed = st.number_input("العلف (كجم):", min_value=0.0, value=0.0, step=10.0, key=f"feed_{cid}")
                    with c3:
                        dead = st.number_input("النافق:", min_value=0, value=0, key=f"dead_{cid}")
                        temp = st.number_input("الحرارة:", min_value=10.0, max_value=45.0, value=33.0, key=f"temp_{cid}")

                    if st.button("💾 حفظ البيانات اليومية", key=f"save_{cid}"):
                        farm_system.add_daily_record(cid, {
                            'age_days': age, 'live_birds': live, 'avg_weight': avg_wt,
                            'feed_consumed': feed, 'dead_count': dead, 'temperature': temp,
                            'initial_count': cycle[5]})
                        st.success("✅ تم الحفظ!")
                        # فحص التنبيهات
                        alerts = farm_system.check_vaccine_alerts(cid)
                        for a in alerts:
                            msg = f"🔔 تنبيه مزرعة {fname}: {a['vaccine_type']} {a['vaccine_name']} - {a['dose']}"
                            send_whatsapp_broiler_alert(st.session_state["farms"][cycle[1]]['owner_phone'], msg)

                    if st.button("🔚 إنهاء الدورة", key=f"close_{cid}"):
                        farm_system.close_cycle(cid)
                        st.success("✅ تم الإغلاق")
                        st.rerun()
        else:
            st.info("📭 لا توجد دورات نشطة.")

# ============================================================================
# تبويب 3: بورصة الأسعار
# ============================================================================
if len(tabs) > 3 and st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[3]:
        guide_section("بورصة الأسعار", guides["البورصة"])
        st.markdown('<div class="section-title">📊 بورصة تاور المركزية</div>', unsafe_allow_html=True)

        tab_l, tab_p = st.tabs(["🐄 الماشية", "🥛 المنتجات"])
        with tab_l:
            for animal, price in list(st.session_state["global_livestock_prices"].items()):
                if st.session_state["user_role"] == "owner":
                    st.session_state["global_livestock_prices"][animal] = st.number_input(
                        f"{animal}", min_value=0.0, value=float(price), step=0.1, key=f"ls_{animal}")
                else:
                    st.markdown(f"▪️ {animal}: **${price:.2f}**")
        with tab_p:
            for product, price in list(st.session_state["global_products_prices"].items()):
                if st.session_state["user_role"] == "owner":
                    st.session_state["global_products_prices"][product] = st.number_input(
                        f"{product}", min_value=0.0, value=float(price), step=0.05, key=f"pr_{product}")
                else:
                    st.markdown(f"▪️ {product}: **${price:.2f}**")

# ============================================================================
# تبويب 4: المستودعات
# ============================================================================
if len(tabs) > 4 and st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[4]:
        guide_section("المستودعات", guides["المستودعات"])
        st.markdown('<div class="section-title">🏭 إدارة المستودعات الذكية</div>', unsafe_allow_html=True)

        warns = InventoryManager.check_stock_levels()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي المواد", len(st.session_state["inventory"]))
        c2.metric("نفذ", sum(1 for v in warns.values() if v == "نفذ المخزون"))
        c3.metric("منخفض", sum(1 for v in warns.values() if v == "منخفض"))
        c4.metric("آمن", len(st.session_state["inventory"]) - len(warns))

        st.markdown("---")
        cols = st.columns(3)
        for idx, (name, data) in enumerate(st.session_state["inventory"].items()):
            with cols[idx % 3]:
                qty = data["quantity"] if isinstance(data, dict) else data
                thr = data.get("min_threshold", 5.0) if isinstance(data, dict) else 5.0
                if qty <= 0:
                    badge = f'<span class="stock-critical">⚠️ نفذ: {qty:.2f}</span>'
                elif qty < thr:
                    badge = f'<span class="stock-critical">⚠️ منخفض: {qty:.2f}</span>'
                else:
                    badge = f'<span class="stock-normal">✅ {qty:.2f} طن</span>'
                st.markdown(f"**{name}** | {badge}", unsafe_allow_html=True)
                if st.session_state["user_role"] == "owner":
                    new_q = st.number_input(f"طن:", min_value=0.0, value=float(qty), key=f"inv_{name}")
                    if isinstance(st.session_state["inventory"][name], dict):
                        st.session_state["inventory"][name]["quantity"] = new_q

# ============================================================================
# تبويب 5: الفواتير
# ============================================================================
if len(tabs) > 5 and st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[5]:
        guide_section("الفواتير", guides["الفواتير"])
        st.markdown('<div class="section-title">🧾 التسويق والفواتير</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1: client = st.text_input("العميل:", "مزرعة نموذجية")
        with c2: tons = st.number_input("الكمية (طن):", min_value=0.1, value=2.0, step=0.5)
        with c3: profit = st.number_input("هامش الربح ($/طن):", min_value=0.0, value=50.0)

        selling = st.session_state["computed_ton_cost"] + profit
        total = selling * tons

        st.markdown(f"""<div class="price-card">
        <h4>تفاصيل الفاتورة:</h4>
        <p>العميل: <b>{client}</b></p>
        <p>الكمية: <b>{tons} طن</b> | سعر الطن: <b>${selling:.2f}</b></p>
        <p style="font-size:1.2rem; color:#1b5e20;">الإجمالي: <b>${total:.2f}</b></p>
        </div>""", unsafe_allow_html=True)

        if st.session_state["user_role"] == "owner" and st.button("✅ تأكيد البيع وخصم المخزون", type="primary"):
            can = True
            for name, pct in st.session_state["active_formula"].items():
                need = (pct / 100) * tons
                cur = st.session_state["inventory"].get(name, {}).get("quantity", 0.0)
                if cur < need:
                    can = False
                    st.error(f"❌ رصيد غير كافٍ: {name}")
                    break
            if can:
                for name, pct in st.session_state["active_formula"].items():
                    need = (pct / 100) * tons
                    st.session_state["inventory"][name]["quantity"] -= need
                st.success("✅ تم الخصم!")
                st.balloons()

# ============================================================================
# تبويب 6: الديباجة
# ============================================================================
if len(tabs) > 6 and st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[6]:
        guide_section("الديباجة", guides["الديباجة"])
        st.markdown('<div class="section-title">🖨️ مصمم الديباجة</div>', unsafe_allow_html=True)

        brand = st.text_input("اسم البراند:", "منصة تاور العلمية للإنتاج الحيواني")
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{st.session_state['active_animal_img']}" class="animal-banner-img">
            <h2 style="text-align:center; color:#1b5e20;">🌟 {brand} 🌟</h2>
            <h3 style="text-align:center; color:#c62828;">الاختصاصي م. عبد القادر إسماعيل تاور</h3>
            <p style="text-align:center; background:#e8f5e9; padding:10px; border-radius:8px;">
            🎯 {st.session_state['active_stage_title']} | DP: {st.session_state['active_cp_tag']:.1f}% |
            SE: {st.session_state['active_se_tag']:.1f}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# تبويب 7: التحليلات
# ============================================================================
if len(tabs) > 7 and st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[7]:
        guide_section("التحليلات المتقدمة", guides["التحليلات"])
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown('<div class="metric-card"><h3>الخلطات</h3><h2 style="color:#2e7d32;">1,247</h2></div>', unsafe_allow_html=True)
        c2.markdown('<div class="metric-card"><h3>متوسط التكلفة</h3><h2 style="color:#1976D2;">$285</h2></div>', unsafe_allow_html=True)
        c3.markdown('<div class="metric-card"><h3>التوفير</h3><h2 style="color:#F57C00;">18%</h2></div>', unsafe_allow_html=True)
        c4.markdown('<div class="metric-card"><h3>الرضا</h3><h2 style="color:#388E3C;">96%</h2></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🔮 تنبؤات الأسعار")
        predictor = PricePredictor()
        for ing in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)"]:
            pred = predictor.predict_price(ing, 7)
            if pred.get('prediction'):
                st.metric(f"{ing}", f"${pred['prediction']:.2f}",
                          delta=f"{pred['prediction'] - pred.get('current_price', 0):.2f}")

        st.markdown("---")
        st.subheader("📊 الرسوم البيانية")
        dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
        trend = pd.DataFrame({'التاريخ': dates,
                              'الذرة': [220, 225, 230, 228, 235, 240, 238, 242, 245, 248, 250, 252],
                              'الصويا': [440, 445, 442, 448, 450, 455, 452, 458, 460, 462, 465, 468]})
        fig = go.Figure() if 'go' in globals() else None
        st.line_chart(trend.set_index('التاريخ'))

# ============================================================================
# تبويب 8: التعليقات
# ============================================================================
if len(tabs) > 8 and st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[8]:
        guide_section("التعليقات", guides["التعليقات"])
        st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
        st.text_area("التعليقات:", value=st.session_state["shared_comments"], height=200, disabled=True)
        new_c = st.text_area("إضافة تعليق:")
        if st.button("➕ نشر"):
            if new_c:
                role = "المالك" if st.session_state["user_role"] == "owner" else "مختص"
                st.session_state["shared_comments"] += f"\n• [{role} {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {new_c}"
                st.success("تم!")
                st.rerun()

# ============================================================================
# تبويب المراجع
# ============================================================================
ref_idx = len(tabs) - 3 if st.session_state["user_role"] in ["owner", "specialist"] else 2
with tabs[ref_idx]:
    guide_section("المراجع العلمية", guides["المراجع"])
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)

    for cat, data in ScientificReferenceSystem.REFERENCES.items():
        st.markdown(f"<div class='book-chapter'>📖 {data['title']}</div>", unsafe_allow_html=True)
        for ref in data.get("references", []):
            st.markdown(f"""<div class='book-body'>
            <b>{ref.get('authors', '')}</b> ({ref.get('year', '')})<br>
            <i>{ref.get('title', '')}</i><br>
            {ref.get('publisher', '')} - {ref.get('edition', '')}<br>
            <small>{ref.get('summary', '')}</small>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">🧠 بنك المعرفة</div>', unsafe_allow_html=True)
    q = st.text_input("اسأل:")
    if q:
        ans = ScientificReferenceSystem.get_knowledge_answer(q)
        if ans:
            st.success(f"📝 {ans['answer']}")
        else:
            st.info("❓ لم أجد إجابة.")

# ============================================================================
# تبويب المساعدة
# ============================================================================
help_idx = ref_idx + 1
if help_idx < len(tabs):
    with tabs[help_idx]:
        guide_section("المساعدة الذكية", guides["المساعدة"])
        st.markdown('<div class="section-title">💡 المساعدة الذكية</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#e3f2fd; padding:20px; border-radius:12px; direction:rtl;'>
        <h3>الأسئلة المتكررة:</h3>
        <ul>
        <li><b>كيف أبدأ؟</b> اختر القطاع والموقع، ثم المكونات، وشغّل المحرك.</li>
        <li><b>ما هو DP؟</b> البروتين المهضوم - أدق من البروتين الخام.</li>
        <li><b>ما هو SE؟</b> معادل النشاء - يقيس الطاقة في العلف.</li>
        <li><b>هل يمكن تعديل الأسعار؟</b> نعم، المالك فقط.</li>
        <li><b>كيف أحصل على PDF؟</b> بعد تشغيل المحرك.</li>
        </ul>
        <p>📧 الدعم: abukram128@gmail.com</p>
        </div>""", unsafe_allow_html=True)

# ============================================================================
# تبويب الدليل
# ============================================================================
guide_idx = help_idx + 1
if guide_idx < len(tabs):
    with tabs[guide_idx]:
        guide_section("دليل المستخدم", guides["الدليل"])
        st.markdown('<div class="section-title">📖 دليل المستخدم الشامل</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="manual-book">
        <h3>🎯 الغرض</h3>
        <p>أداة ذكية لتركيب الأعلاف بأقل تكلفة مع توازن غذائي دقيق.</p>

        <div class="book-chapter">الفصل الأول: الدخول</div>
        <div class="book-body">
        كود المالك: <b>202687</b> | المختص: 2020 | المربي: 2026
        </div>

        <div class="book-chapter">الفصل الثاني: تركيب العلفة</div>
        <div class="book-body">
        <ol>
        <li>اختر الموقع الجغرافي</li>
        <li>اختر القطاع الحيواني والسلالة</li>
        <li>استخدم المعادلات المتقدمة (NRC) لحساب الاحتياجات</li>
        <li>حدد DP و SE</li>
        <li>اختر المكونات</li>
        <li>شغّل المحرك الخطي</li>
        <li>حمّل PDF أو شارك عبر واتساب</li>
        </ol>
        </div>

        <div class="book-chapter">الفصل الثالث: المختبر الذكي</div>
        <div class="book-body">
        ارفع صورة تركيبة → استخرج القيم تلقائياً → احفظ النتيجة.
        </div>

        <div class="book-chapter">الفصل الرابع: إدارة المزارع</div>
        <div class="book-body">
        إنشاء مزارع، دورات إنتاجية، تسجيل يومي، تنبيهات واتساب تلقائية.
        </div>

        <div class="book-chapter">الفصل الخامس: المخازن والفواتير</div>
        <div class="book-body">
        خصم تلقائي للمكونات عند إصدار الفواتير.
        </div>
        </div>""", unsafe_allow_html=True)

# ============================================================================
# التذييل
# ============================================================================
st.markdown('<div class="mini-left-signature">🌾 منصة تاور العلمية v4.0 | م. عبد القادر إسماعيل تاور © 2026</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
