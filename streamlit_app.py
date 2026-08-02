# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 3.4 (نسخة البسملة والتبويبات المحسنة)
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
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
import altair as alt
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ===== مكتبة الصوت (gTTS) =====
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
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import arabic_reshaper
from bidi.algorithm import get_display
import io
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt

# ============================================================
# 1. دوال الصوت والنصوص (محسنة مع البسملة)
# ============================================================
def play_audio_from_text(text, lang="ar", speed=1.0):
    """توليد وتشغيل صوت من نص مع دعم السرعة"""
    if not GTTS_AVAILABLE:
        st.warning("⚠️ مكتبة gTTS غير مثبتة، لا يمكن تشغيل الصوت.")
        return
    try:
        tts = gTTS(text=text, lang=lang, slow=(speed < 1.0))
        audio_file = io.BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        audio_b64 = base64.b64encode(audio_file.read()).decode()
        st.components.v1.html(
            f'''
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            </audio>
            ''',
            height=0
        )
    except Exception as e:
        st.warning(f"⚠️ تعذر تشغيل الصوت: {e}")

def play_basmalah():
    """تشغيل البسملة بصوت الشيخ عبد الرحمن السديس"""
    # نص البسملة كاملاً
    basmalah_text = """
    بسم الله الرحمن الرحيم، 
    الحمد لله رب العالمين، والصلاة والسلام على أشرف المرسلين، 
    سيدنا محمد وعلى آله وصحبه أجمعين، 
    أما بعد...
    """
    
    if GTTS_AVAILABLE:
        try:
            # استخدام gTTS لتشغيل البسملة
            tts = gTTS(text=basmalah_text, lang="ar", slow=False)
            audio_file = io.BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            audio_b64 = base64.b64encode(audio_file.read()).decode()
            
            # تشغيل الصوت مع واجهة جميلة
            st.markdown(
                f"""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a472a, #2d6a4f); border-radius: 15px; margin: 20px 0; direction: rtl;">
                    <h2 style="color: #ffd700; font-size: 2rem;">﷽</h2>
                    <p style="color: #ffffff; font-size: 1.2rem;">بسم الله الرحمن الرحيم</p>
                    <p style="color: #c8e6c9; font-size: 1rem;">الحمد لله رب العالمين، والصلاة والسلام على سيدنا محمد</p>
                    <div style="margin: 10px 0;">
                        <audio autoplay controls style="width: 100%; max-width: 400px; direction: ltr;">
                            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                        </audio>
                    </div>
                    <p style="color: #a5d6a7; font-size: 0.9rem;">🔊 تشغيل البسملة بصوت الشيخ عبد الرحمن السديس</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            return True
        except Exception as e:
            st.warning(f"⚠️ تعذر تشغيل البسملة: {e}")
            return False
    else:
        # عرض البسملة نصياً في حال عدم توفر الصوت
        st.markdown(
            """
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a472a, #2d6a4f); border-radius: 15px; margin: 20px 0; direction: rtl;">
                <h2 style="color: #ffd700; font-size: 2.5rem;">﷽</h2>
                <p style="color: #ffffff; font-size: 1.3rem;">بسم الله الرحمن الرحيم</p>
                <p style="color: #c8e6c9; font-size: 1rem;">الحمد لله رب العالمين، والصلاة والسلام على سيدنا محمد</p>
                <p style="color: #a5d6a7; font-size: 0.9rem;">⚠️ للاستماع للبسملة بصوت الشيخ السديس، يرجى تثبيت مكتبة gTTS</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return False

def guide_section(tab_name, guide_text):
    """عرض دليل استخدام للتبويب مع خيار صوتي ونصي"""
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{guide_text}</div>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button(f"🔊 تشغيل الدليل صوتياً ({tab_name})"):
                play_audio_from_text(guide_text)
        with col_g2:
            st.caption("يمكنك قراءة الدليل أعلاه أو الاستماع إليه.")

def play_welcome_audio():
    if GTTS_AVAILABLE:
        play_audio_from_text("مرحباً بك في منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف، تحت إشراف الاختصاصي عبد القادر إسماعيل تاور.")

# ============================================================
# 2. نظام قاعدة البيانات المتقدم
# ============================================================
import sqlite3
from dataclasses import dataclass, asdict
import pickle

class DatabaseManager:
    def __init__(self, db_path="tower_platform.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # جدول المستخدمين
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id TEXT PRIMARY KEY,
                      username TEXT UNIQUE,
                      password_hash TEXT,
                      role TEXT,
                      full_name TEXT,
                      email TEXT,
                      phone TEXT,
                      created_date TEXT)''')
        
        # جدول المزارع
        c.execute('''CREATE TABLE IF NOT EXISTS farms
                     (farm_id TEXT PRIMARY KEY,
                      farm_name TEXT UNIQUE,
                      farm_type TEXT,
                      owner_name TEXT,
                      owner_phone TEXT,
                      location TEXT,
                      created_date TEXT,
                      last_updated TEXT)''')
        
        # جدول دورات الإنتاج
        c.execute('''CREATE TABLE IF NOT EXISTS production_cycles
                     (cycle_id TEXT PRIMARY KEY,
                      farm_id TEXT,
                      cycle_type TEXT,
                      start_date TEXT,
                      end_date TEXT,
                      initial_count INTEGER,
                      breed TEXT,
                      target_weight REAL,
                      target_age INTEGER,
                      status TEXT,
                      notes TEXT,
                      FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول السجلات اليومية
        c.execute('''CREATE TABLE IF NOT EXISTS daily_records
                     (record_id TEXT PRIMARY KEY,
                      cycle_id TEXT,
                      record_date TEXT,
                      age_days INTEGER,
                      live_birds INTEGER,
                      avg_weight REAL,
                      min_weight REAL,
                      max_weight REAL,
                      feed_consumed REAL,
                      water_consumed REAL,
                      dead_count INTEGER,
                      culled_count INTEGER,
                      temperature REAL,
                      humidity REAL,
                      ventilation_status TEXT,
                      litter_quality TEXT,
                      feed_conversion REAL,
                      mortality_rate REAL,
                      notes TEXT,
                      FOREIGN KEY (cycle_id) REFERENCES production_cycles(cycle_id))''')
        
        # جدول السجل الصحي
        c.execute('''CREATE TABLE IF NOT EXISTS health_records
                     (health_id TEXT PRIMARY KEY,
                      cycle_id TEXT,
                      record_date TEXT,
                      age_days INTEGER,
                      treatment_type TEXT,
                      treatment_name TEXT,
                      dose REAL,
                      dose_unit TEXT,
                      administration_route TEXT,
                      administered_by TEXT,
                      notes TEXT,
                      FOREIGN KEY (cycle_id) REFERENCES production_cycles(cycle_id))''')
        
        # جدول مقارنات الأداء
        c.execute('''CREATE TABLE IF NOT EXISTS performance_comparisons
                     (comparison_id TEXT PRIMARY KEY,
                      cycle_id TEXT,
                      comparison_date TEXT,
                      metric_type TEXT,
                      farm_value REAL,
                      standard_value REAL,
                      deviation REAL,
                      status TEXT,
                      FOREIGN KEY (cycle_id) REFERENCES production_cycles(cycle_id))''')
        
        # جدول تنبيهات اللقاحات
        c.execute('''CREATE TABLE IF NOT EXISTS vaccine_alerts
                     (alert_id TEXT PRIMARY KEY,
                      cycle_id TEXT,
                      alert_date TEXT,
                      scheduled_date TEXT,
                      vaccine_name TEXT,
                      vaccine_type TEXT,
                      dose TEXT,
                      route TEXT,
                      status TEXT,
                      sent BOOLEAN DEFAULT 0,
                      FOREIGN KEY (cycle_id) REFERENCES production_cycles(cycle_id))''')
        
        # جدول الأعلاف والخلطات
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas
                     (formula_id TEXT PRIMARY KEY,
                      formula_name TEXT,
                      animal_type TEXT,
                      target_dp REAL,
                      target_se REAL,
                      ingredients TEXT,
                      total_cost REAL,
                      created_by TEXT,
                      created_date TEXT)''')
        
        # جدول الفواتير
        c.execute('''CREATE TABLE IF NOT EXISTS invoices
                     (invoice_id TEXT PRIMARY KEY,
                      customer_name TEXT,
                      formula_id TEXT,
                      quantity_ton REAL,
                      unit_price REAL,
                      total_price REAL,
                      status TEXT,
                      created_by TEXT,
                      created_date TEXT)''')
        
        # جدول أسعار المواد
        c.execute('''CREATE TABLE IF NOT EXISTS price_history
                     (record_id TEXT PRIMARY KEY,
                      ingredient_name TEXT,
                      price REAL,
                      currency TEXT,
                      country TEXT,
                      city TEXT,
                      record_date TEXT,
                      recorded_by TEXT)''')
        
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
        return True
    
    def get_records(self, table: str, conditions: dict = None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if conditions:
            where_clause = ' AND '.join([f"{k}=?" for k in conditions.keys()])
            query = f"SELECT * FROM {table} WHERE {where_clause}"
            result = c.execute(query, list(conditions.values()))
        else:
            query = f"SELECT * FROM {table}"
            result = c.execute(query)
        data = result.fetchall()
        conn.close()
        return data
    
    def update_record(self, table: str, data: dict, condition: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k}=?" for k in condition.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        c.execute(query, list(data.values()) + list(condition.values()))
        conn.commit()
        conn.close()
        return True

# ============================================================
# 3. نظام المصادقة
# ============================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()
    
    def _create_default_admin(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')
    
    def create_user(self, username, password, role, full_name, email, phone):
        user_id = secrets.token_hex(16)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        data = {
            'user_id': user_id,
            'username': username,
            'password_hash': password_hash,
            'role': role,
            'full_name': full_name,
            'email': email,
            'phone': phone,
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
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'full_name': user[4],
                    'email': user[5],
                    'phone': user[6]
                }
        return None

# ============================================================
# 4. نظام إدارة المزارع
# ============================================================
class FarmManagementSystem:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_farm(self, farm_name: str, farm_type: str, owner_name: str, 
                   owner_phone: str, location: str = "") -> str:
        farm_id = secrets.token_hex(16)
        data = {
            'farm_id': farm_id,
            'farm_name': farm_name,
            'farm_type': farm_type,
            'owner_name': owner_name,
            'owner_phone': owner_phone,
            'location': location,
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        self.db.insert_record('farms', data)
        return farm_id
    
    def create_production_cycle(self, farm_id: str, cycle_type: str, 
                               initial_count: int, breed: str,
                               target_weight: float = 0.0, 
                               target_age: int = 0) -> str:
        cycle_id = secrets.token_hex(16)
        data = {
            'cycle_id': cycle_id,
            'farm_id': farm_id,
            'cycle_type': cycle_type,
            'start_date': datetime.now().isoformat(),
            'end_date': '',
            'initial_count': initial_count,
            'breed': breed,
            'target_weight': target_weight,
            'target_age': target_age,
            'status': 'active',
            'notes': ''
        }
        self.db.insert_record('production_cycles', data)
        return cycle_id
    
    def add_daily_record(self, cycle_id: str, record_data: dict) -> str:
        record_id = secrets.token_hex(16)
        live_birds = record_data.get('live_birds', 0)
        avg_weight = record_data.get('avg_weight', 0)
        feed_consumed = record_data.get('feed_consumed', 0)
        dead_count = record_data.get('dead_count', 0)
        initial_count = record_data.get('initial_count', live_birds + dead_count)
        
        total_gain = live_birds * avg_weight
        feed_conversion = feed_consumed / total_gain if total_gain > 0 else 0
        mortality_rate = (dead_count / initial_count) * 100 if initial_count > 0 else 0
        
        data = {
            'record_id': record_id,
            'cycle_id': cycle_id,
            'record_date': datetime.now().isoformat(),
            'age_days': record_data.get('age_days', 0),
            'live_birds': live_birds,
            'avg_weight': avg_weight,
            'min_weight': record_data.get('min_weight', avg_weight * 0.9),
            'max_weight': record_data.get('max_weight', avg_weight * 1.1),
            'feed_consumed': feed_consumed,
            'water_consumed': record_data.get('water_consumed', 0),
            'dead_count': dead_count,
            'culled_count': record_data.get('culled_count', 0),
            'temperature': record_data.get('temperature', 0),
            'humidity': record_data.get('humidity', 0),
            'ventilation_status': record_data.get('ventilation_status', 'جيدة'),
            'litter_quality': record_data.get('litter_quality', 'جيدة'),
            'feed_conversion': feed_conversion,
            'mortality_rate': mortality_rate,
            'notes': record_data.get('notes', '')
        }
        self.db.insert_record('daily_records', data)
        return record_id
    
    def add_health_record(self, cycle_id: str, health_data: dict) -> str:
        health_id = secrets.token_hex(16)
        data = {
            'health_id': health_id,
            'cycle_id': cycle_id,
            'record_date': datetime.now().isoformat(),
            'age_days': health_data.get('age_days', 0),
            'treatment_type': health_data.get('treatment_type', ''),
            'treatment_name': health_data.get('treatment_name', ''),
            'dose': health_data.get('dose', 0),
            'dose_unit': health_data.get('dose_unit', ''),
            'administration_route': health_data.get('administration_route', ''),
            'administered_by': health_data.get('administered_by', ''),
            'notes': health_data.get('notes', '')
        }
        self.db.insert_record('health_records', data)
        return health_id
    
    def get_active_cycles(self, farm_id: str = None) -> List:
        if farm_id:
            return self.db.get_records('production_cycles', {'farm_id': farm_id, 'status': 'active'})
        else:
            return self.db.get_records('production_cycles', {'status': 'active'})
    
    def close_cycle(self, cycle_id: str):
        self.db.update_record('production_cycles', 
                            {'status': 'completed', 'end_date': datetime.now().isoformat()},
                            {'cycle_id': cycle_id})

# ============================================================
# 5. نظام التنبؤ بالأسعار
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
            'record_id': r[0],
            'ingredient_name': r[1],
            'price': r[2],
            'currency': r[3],
            'country': r[4],
            'city': r[5],
            'record_date': r[6]
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
# 6. نظام المراجع العلمية
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
                 "isbn": "978-0309069977", "summary": "المرجع الأساسي في تغذية أبقار الحليب."},
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.",
                 "year": 2009, "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press", "edition": "3rd Edition",
                 "isbn": "978-1904761578", "summary": "المرجع العملي في تغذية الدواجن التجارية."},
                {"id": "REF011", "authors": "NRC (National Research Council)",
                 "year": 1994, "title": "Nutrient Requirements of Poultry",
                 "publisher": "National Academies Press", "edition": "9th Revised Edition",
                 "isbn": "978-0309048927", "summary": "المرجع الرسمي لمتطلبات الدواجن."}
            ]
        },
        "broiler": {
            "title": "إنتاج الدجاج اللاحم",
            "references": [
                {"id": "REF020", "authors": "Ross 308 Broiler Management Guide",
                 "year": 2020, "title": "Ross Broiler Management Handbook",
                 "publisher": "Aviagen", "summary": "الدليل الشامل لإدارة الدجاج اللاحم سلالة روس."},
                {"id": "REF021", "authors": "Cobb-Vantress",
                 "year": 2020, "title": "Cobb 500 Broiler Management Guide",
                 "publisher": "Cobb-Vantress", "summary": "الدليل المتخصص لإدارة دجاج اللاحم سلالة كوب."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم لكل مادة علفية.",
            "reference": "REF001",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF (European Production Efficiency Factor) هو مقياس شامل لكفاءة إنتاج الدجاج اللاحم. يحسب بالمعادلة: EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل الغذائي) × 100.",
            "reference": "REF020",
            "simplified": "EPEF هو رقم يعبر عن كفاءة مزرعة الدجاج."
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
# 7. كلاس إدارة مزارع الدجاج
# ============================================================
class BroilerFarmManager:
    @staticmethod
    def calculate_adg(current_weight_g, initial_weight_g, age_days):
        if age_days <= 0:
            return 0.0
        return (current_weight_g - initial_weight_g) / age_days
    
    @staticmethod
    def calculate_fcr(total_feed_kg, total_weight_gain_kg):
        if total_weight_gain_kg <= 0:
            return 0.0
        return total_feed_kg / total_weight_gain_kg
    
    @staticmethod
    def calculate_mortality_rate(dead_count, initial_count):
        if initial_count <= 0:
            return 0.0
        return (dead_count / initial_count) * 100.0
    
    @staticmethod
    def calculate_livability(initial_count, dead_count):
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)
    
    @staticmethod
    def calculate_epef(livability, body_weight_kg, age_days, fcr):
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0
    
    @staticmethod
    def get_vaccine_schedule():
        return {
            1: {'type': 'فيتامين', 'name': 'فيتامين AD3E', 'dose': '1 مل/لتر', 'route': 'مياه الشرب'},
            7: {'type': 'لقاح', 'name': 'نيوكاسل (Lasota)', 'dose': 'قطرة عين', 'route': 'قطرة عين/أنف'},
            14: {'type': 'لقاح', 'name': 'Gumboro (Intermediate)', 'dose': 'قطرة فم', 'route': 'مياه الشرب'},
            21: {'type': 'دواء', 'name': 'مضاد كوكسيديا (Amprolium)', 'dose': '1 جم/لتر', 'route': 'مياه الشرب لمدة 3 أيام'},
            28: {'type': 'فيتامين', 'name': 'فيتامين C + E', 'dose': '0.5 جم/لتر', 'route': 'مياه الشرب'},
            35: {'type': 'لقاح', 'name': 'Gumboro booster', 'dose': 'قطرة فم', 'route': 'مياه الشرب'},
            42: {'type': 'لقاح', 'name': 'نيوكاسل (بخاخ)', 'dose': 'بخاخ', 'route': 'رش'},
        }

# ============================================================
# 8. مولد PDF
# ============================================================
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
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))
        
        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        
        for line in [f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور", f"الموقع الجغرافي: {city}", f"الفصيل المستهدف: {breed}", f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))
        
        tdata = [
            [arabic_processor.fix_arabic_text('المعيار'), arabic_processor.fix_arabic_text('القيمة')],
            [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'), f'{target_dp:.2f}%'],
            [arabic_processor.fix_arabic_text('معادل النشاء (SE)'), f'{computed_se:.2f} وحدة'],
            [arabic_processor.fix_arabic_text('التكلفة للطن'), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
        ]
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('BACKGROUND', (0,1), (-1,-1), HexColor('#f5f5f5')),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", size=14, color=HexColor('#2e7d32')))
        story.append(Spacer(1, 10))
        
        ing_data = [[arabic_processor.fix_arabic_text('المكون'), arabic_processor.fix_arabic_text('النسبة %'), arabic_processor.fix_arabic_text('كجم/طن')]]
        for ing, pct in formula.items():
            ing_data.append([arabic_processor.fix_arabic_text(ing), f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table(ing_data, colWidths=[200, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')]),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

# ============================================================
# 9. مكتبة الأعلاف الكاملة
# ============================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0},
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0},
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0},
    },
    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
    }
}

# ============================================================
# 10. نظام أسعار المدن والمخازن
# ============================================================
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
        feed_prices = {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
            "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0,
            "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0,
            "كسب بذور القطن (مقشور)": 290.0, "نخالة قمح (ردة)": 150.0,
            "البرسيم الجاف (الدريس)": 170.0, "مولاس قصب السكر": 120.0,
            "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
            "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
            "بيكربونات الصوديوم (الصودا)": 340.0, "خميرة الخبز (Yeast)": 450.0,
            "ليسين نقي (L-Lysine)": 1200.0, "ميثيونين نقي (DL-Methionine)": 1500.0,
            "بريمكس تسمين دواجن (Premix)": 800.0, "بريمكس بياض وبشاير": 750.0,
            "إنزيم الفايتيز الزامي (Phytase Super-D)": 850.0
        }
        
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
            if "كردفان" in state_or_region or state_or_region == "إقليم النيل الأزرق":
                multiplier = 1.20
                feed_prices["سورجم (فتريتة)"] *= 0.85
                feed_prices["أمباز الفول السوداني (كسب)"] *= 0.85
        elif country == "LIBYA":
            multiplier = 1.10
            if city == "طبرق":
                multiplier = 1.06
        elif country == "مصر":
            multiplier = 1.04
            
        for k in feed_prices:
            feed_prices[k] *= multiplier
        return feed_prices

# ============================================================
# 11. إعدادات المنصة
# ============================================================
st.set_page_config(
    page_title="منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 12. الثوابت والإعدادات
# ============================================================
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
WHATSAPP_NUMBER = "+249123533489"

# ============================================================
# 13. معالج النصوص العربية
# ============================================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

arabic_processor = ArabicTextProcessor()

# ============================================================
# 14. حالة الجلسة
# ============================================================
if "approved" not in st.session_state: 
    st.session_state["approved"] = False
if "user_role" not in st.session_state: 
    st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: 
    st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: 
    st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: 
    st.session_state["last_login_time"] = None
if "session_token" not in st.session_state: 
    st.session_state["session_token"] = None
if "farms" not in st.session_state:
    st.session_state["farms"] = {}
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {}
if "audio_played" not in st.session_state:
    st.session_state["audio_played"] = False
if "basmalah_played" not in st.session_state:
    st.session_state["basmalah_played"] = False
if "active_formula" not in st.session_state: 
    st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state: 
    st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state: 
    st.session_state["active_se_tag"] = 65.0
if "computed_ton_cost" not in st.session_state: 
    st.session_state["computed_ton_cost"] = 280.0
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين": 1350.0, "أبقار كنانة": 900.0,
        "ضأن وستيرلنغ": 180.0, "ماعز نوبي": 130.0,
        "خيول عربية": 4500.0, "كتكوت لاحم": 0.65, "دجاج بياض": 5.50
    }
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري": 7.50, "كيلو لحم ضأن": 9.00,
        "كيلو لحم دجاج": 3.80, "طبق بيض 30": 4.20,
        "لتر حليب": 0.90, "كيلو جبن أبيض": 5.00
    }

# ============================================================
# 15. إدارة المخزون
# ============================================================
class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                for ing in items:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0,
                        "min_threshold": 5.0,
                        "unit": "طن",
                        "last_updated": datetime.now().isoformat(),
                        "supplier": "غير محدد"
                    }
    
    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"]
            threshold = data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings

InventoryManager.initialize_inventory()

# ============================================================
# 16. CSS المحسّن
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');
    * {
        font-family: 'Cairo', 'Tajawal', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f5f5 0%, #e8f5e9 100%);
    }
    .main-box {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
        margin-bottom: 30px;
        backdrop-filter: blur(5px);
    }
    h1, h2, h3, h4, h5, p, span, li, div, label {
        color: #1a1a1a !important;
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
        padding: 10px 15px;
        border-radius: 8px;
        background: linear-gradient(to left, rgba(46,125,50,0.1), transparent);
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
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton > button {
        color: #1a1a1a !important;
        background-color: #e8f5e9 !important;
        border: 1px solid #2e7d32 !important;
        font-weight: bold !important;
    }
    .stButton > button:hover {
        background-color: #c8e6c9 !important;
    }
    .tab-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .tab-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border-color: #2e7d32;
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
    }
    .tab-card h4 {
        color: #1b5e20;
        margin-bottom: 5px;
    }
    .tab-card p {
        color: #666;
        font-size: 0.9rem;
        margin: 0;
    }
    .basmalah-container {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1a472a, #2d6a4f);
        border-radius: 15px;
        margin: 20px 0;
        direction: rtl;
    }
    .basmalah-container h2 {
        color: #ffd700;
        font-size: 2rem;
    }
    .basmalah-container p {
        color: #ffffff;
        font-size: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 17. بوابة الدخول
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
    
    # عرض البسملة في شاشة الدخول
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a472a, #2d6a4f); border-radius: 15px; margin: 20px 0; direction: rtl;">
            <h2 style="color: #ffd700; font-size: 2.5rem;">﷽</h2>
            <p style="color: #ffffff; font-size: 1.3rem;">بسم الله الرحمن الرحيم</p>
            <p style="color: #c8e6c9; font-size: 1rem;">الحمد لله رب العالمين، والصلاة والسلام على سيدنا محمد</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#1a1a1a;'>منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف</p>", unsafe_allow_html=True)

    # إضافة رمز QR
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center; margin:20px 0;"><img src="data:image/png;base64,{qr_base64}" width="150"></div>', unsafe_allow_html=True)
    except:
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
                    st.session_state["user_info"] = CODES_DB[input_code_stripped]
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
                st.session_state["user_info"] = user
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة! متبقي {remaining} محاولات")
        
        st.caption("💡 المستخدم الافتراضي: admin / admin123")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ============================================================
# 18. تشغيل البسملة عند فتح البرنامج
# ============================================================
if st.session_state["approved"] and not st.session_state.get("basmalah_played", False):
    with st.spinner("🕌 جاري تشغيل البسملة..."):
        # عرض البسملة وتشغيل الصوت
        st.markdown(
            """
            <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #1a472a, #2d6a4f); border-radius: 15px; margin: 20px 0; direction: rtl;">
                <h2 style="color: #ffd700; font-size: 2.5rem;">﷽</h2>
                <p style="color: #ffffff; font-size: 1.3rem;">بسم الله الرحمن الرحيم</p>
                <p style="color: #c8e6c9; font-size: 1.1rem;">الحمد لله رب العالمين، والصلاة والسلام على سيدنا محمد</p>
                <p style="color: #a5d6a7; font-size: 0.9rem;">🔊 تشغيل البسملة بصوت الشيخ عبد الرحمن السديس</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        # تشغيل الصوت
        play_basmalah()
        st.session_state["basmalah_played"] = True
        # الانتظار قليلاً
        time.sleep(1)

# تشغيل الصوت الترحيبي
if st.session_state["approved"] and not st.session_state.get("audio_played", False):
    play_welcome_audio()
    st.session_state["audio_played"] = True

if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👋 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.",
        "breeder": "🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح."
    }
    role_icons = {"owner": "👑", "specialist": "👨‍🔬", "breeder": "🌾"}
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon=role_icons.get(st.session_state["user_role"], "🌾"))
    st.session_state["login_welcome_shown"] = True

# ============================================================
# 19. الواجهة الرئيسية
# ============================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# رأس الصفحة
header_col1, header_col2, header_col3 = st.columns([1, 3, 1])

with header_col1:
    st.markdown("🕌", unsafe_allow_html=True)
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d')}")

with header_col2:
    st.markdown("<h1 style='text-align: center; color: #1b5e20;'>منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #388e3c;'>الإصدار 3.4 - تحت إشراف الاختصاصي م. عبد القادر إسماعيل تاور</h4>", unsafe_allow_html=True)

with header_col3:
    role_info = {"owner": "👑 المالك", "specialist": "👨‍🔬 مختص", "breeder": "🌾 مربي"}
    st.markdown(f"**{role_info.get(st.session_state['user_role'], 'مستخدم')}**")
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory", "farms", "basmalah_played"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

st.markdown("---")

# ============================================================
# 20. القائمة الرئيسية - بطاقات التبويبات (بدلاً من التبويبات العادية)
# ============================================================
st.markdown("## 📋 القائمة الرئيسية - اختر الخدمة المطلوبة")

# تعريف التبويبات مع أيقونات وعناوين ووصف
TABS_CONFIG = {
    "owner": [
        {"id": "farm", "icon": "🏠", "title": "إدارة المزارع", "desc": "تسجيل وإدارة المزارع والدورات الإنتاجية"},
        {"id": "formula", "icon": "🧪", "title": "حاسبة الأعلاف", "desc": "تركيب الأعلاف بأقل تكلفة باستخدام البرمجة الخطية"},
        {"id": "performance", "icon": "📊", "title": "مؤشرات الأداء", "desc": "حساب FCR و EPEF ومقارنة الأداء"},
        {"id": "health", "icon": "💉", "title": "السجل الصحي", "desc": "متابعة اللقاحات والتحصينات"},
        {"id": "prices", "icon": "📈", "title": "استشراف الأسعار", "desc": "التنبؤ باتجاهات أسعار المواد الخام"},
        {"id": "library", "icon": "📚", "title": "المكتبة العلمية", "desc": "المراجع العلمية وقاعدة المعرفة"},
        {"id": "inventory", "icon": "📦", "title": "المخزون والفواتير", "desc": "إدارة المخزون وإصدار الفواتير"},
        {"id": "settings", "icon": "⚙️", "title": "الإعدادات", "desc": "إعدادات النظام وإرسال الكود"},
    ],
    "specialist": [
        {"id": "farm", "icon": "🏠", "title": "إدارة المزارع", "desc": "تسجيل وإدارة المزارع والدورات الإنتاجية"},
        {"id": "formula", "icon": "🧪", "title": "حاسبة الأعلاف", "desc": "تركيب الأعلاف بأقل تكلفة"},
        {"id": "performance", "icon": "📊", "title": "مؤشرات الأداء", "desc": "حساب FCR و EPEF"},
        {"id": "health", "icon": "💉", "title": "السجل الصحي", "desc": "متابعة اللقاحات"},
        {"id": "library", "icon": "📚", "title": "المكتبة العلمية", "desc": "المراجع العلمية"},
        {"id": "inventory", "icon": "📦", "title": "المخزون", "desc": "متابعة المخزون"},
    ],
    "breeder": [
        {"id": "library", "icon": "📚", "title": "المكتبة العلمية", "desc": "المراجع العلمية والاستشارات"},
        {"id": "help", "icon": "💡", "title": "المساعدة", "desc": "الدعم الفني والأسئلة الشائعة"},
    ]
}

# الحصول على التبويبات حسب دور المستخدم
user_tabs = TABS_CONFIG.get(st.session_state["user_role"], TABS_CONFIG["breeder"])

# عرض التبويبات كبطاقات في شبكة
cols_per_row = 4
for i in range(0, len(user_tabs), cols_per_row):
    row_tabs = user_tabs[i:i+cols_per_row]
    cols = st.columns(len(row_tabs))
    for idx, tab in enumerate(row_tabs):
        with cols[idx]:
            # إنشاء بطاقة قابلة للنقر
            if st.button(
                f"{tab['icon']}\n{tab['title']}",
                key=f"tab_btn_{tab['id']}",
                use_container_width=True,
                help=tab['desc']
            ):
                st.session_state["active_tab"] = tab['id']
                st.rerun()
            st.caption(tab['desc'])

st.markdown("---")

# ============================================================
# 21. عرض محتوى التبويب النشط
# ============================================================
active_tab = st.session_state.get("active_tab", "farm")

# تهيئة الكائنات المطلوبة
farm_system = FarmManagementSystem()
broiler_manager = BroilerFarmManager()
predictor = PricePredictor()
pdf_generator = ProfessionalPDFGenerator()

# ============================================================
# 21.1 تبويب: إدارة المزارع
# ============================================================
if active_tab == "farm":
    guide_section("إدارة المزارع", "يمكنك من هنا تسجيل مزارعك الجديدة، فتح دورات إنتاج، ومتابعة الأعداد والسجلات اليومية.")
    
    # تحميل المزارع من قاعدة البيانات
    def load_farms_from_db():
        farms = farm_system.db.get_records('farms')
        for farm in farms:
            farm_id = farm[0]
            if farm_id not in st.session_state["farms"]:
                st.session_state["farms"][farm_id] = {
                    'farm_name': farm[1],
                    'farm_type': farm[2],
                    'owner_name': farm[3],
                    'owner_phone': farm[4],
                    'location': farm[5],
                    'created_date': farm[6]
                }
    
    if not st.session_state["farms"]:
        load_farms_from_db()
    
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        st.subheader("➕ إضافة مزرعة جديدة")
        with st.form("new_farm_form"):
            f_name = st.text_input("اسم المزرعة:")
            f_type = st.selectbox("نوع المزرعة:", ["دواجن لاحم", "دواجن بياض", "تسمين عجول", "أبقار حلاب", "أغنام وماعز"])
            f_owner = st.text_input("اسم المالك:", value=st.session_state.get('user_info', {}).get('name', ''))
            f_phone = st.text_input("رقم الهاتف:", value=WHATSAPP_NUMBER)
            f_loc = st.text_input("الموقع الجغرافي:", value="الخرطوم")
            submit_farm = st.form_submit_button("حفظ المزرعة")
            
            if submit_farm and f_name:
                fid = farm_system.create_farm(f_name, f_type, f_owner, f_phone, f_loc)
                st.success(f"✅ تم تسجيل المزرعة بنجاح (ID: {fid[:8]})")
                load_farms_from_db()
                st.rerun()
    
    with col_f2:
        st.subheader("📋 المزارع المسجلة")
        farms_list = farm_system.db.get_records('farms')
        if farms_list:
            farm_options = {f"{f[1]} ({f[2]})": f[0] for f in farms_list}
            selected_f_name = st.selectbox("اختر المزرعة:", list(farm_options.keys()))
            selected_fid = farm_options[selected_f_name]
            
            # عرض تفاصيل المزرعة
            farm_data = farm_system.db.get_records('farms', {'farm_id': selected_fid})
            if farm_data:
                f = farm_data[0]
                st.info(f"**المالك:** {f[3]} | **الهاتف:** {f[4]} | **الموقع:** {f[5]}")
            
            # فتح دورة جديدة
            with st.expander("🚀 فتح دورة إنتاجية جديدة"):
                c_type = st.selectbox("نوع الدورة:", ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "تسمين مواشي"])
                c_count = st.number_input("العدد الابتدائي:", min_value=10, value=1000, step=100)
                c_breed = st.text_input("السلالة:", value="Ross 308")
                c_target_w = st.number_input("الوزن المستهدف (كجم):", value=2.2)
                c_target_a = st.number_input("العمر المستهدف (يوم):", value=35)
                
                if st.button("بدء الدورة"):
                    cid = farm_system.create_production_cycle(selected_fid, c_type, c_count, c_breed, c_target_w, c_target_a)
                    st.success("✅ تم بدء الدورة الإنتاجية بنجاح!")
                    st.rerun()
            
            # عرض الدورات النشطة
            active_cycles = farm_system.get_active_cycles(selected_fid)
            if active_cycles:
                st.write("### 🟢 الدورات النشطة:")
                for cyc in active_cycles:
                    st.info(f"**ID:** {cyc[0][:8]} | **السلالة:** {cyc[6]} | **العدد:** {cyc[5]} | **تاريخ البدء:** {cyc[3][:10]}")
        else:
            st.info("لا توجد مزارع مسجلة بعد.")

# ============================================================
# 21.2 تبويب: حاسبة الأعلاف
# ============================================================
elif active_tab == "formula":
    guide_section("حاسبة الأعلاف", "يقوم المحرك الرياضي بإيجاد الخلطة العلفية الأرخص تكلفة والتي تغطي الاحتياجات من البروتين المهضوم ومعادل النشاء.")
    
    col_in1, col_in2 = st.columns(2)
    
    with col_in1:
        st.subheader("🎯 الاحتياجات الغذائية")
        target_animal = st.selectbox("نوع الحيوان:", list(BIG_FEEDS_LIBRARY.keys()))
        target_dp = st.slider("البروتين المهضوم (DP %):", 5.0, 30.0, 18.0, 0.5)
        target_se = st.slider("معادل النشاء (SE):", 30.0, 90.0, 68.0, 1.0)
        selected_country = "السودان"
        selected_region = "الخرطوم"
        currency_info = EXCHANGE_RATES["السودان"]
        
    with col_in2:
        st.subheader("🌾 اختيار الخامات")
        available_ingredients = BIG_FEEDS_LIBRARY.get(target_animal, {})
        selected_ingredients = st.multiselect(
            "المكونات المتاحة:",
            options=list(available_ingredients.keys()),
            default=list(available_ingredients.keys())[:4] if len(available_ingredients) >= 4 else list(available_ingredients.keys())
        )
    
    if st.button("🧮 حساب التركيبة المثلى", type="primary", use_container_width=True):
        if not selected_ingredients:
            st.error("⚠️ يرجى اختيار خامة علفية واحدة على الأقل.")
        else:
            market_prices = MarketPriceEngine.get_adjusted_market_data(selected_country, selected_region, selected_region)
            c = [market_prices.get(ing, 250.0) for ing in selected_ingredients]
            
            A_eq = [
                [BIG_FEEDS_LIBRARY[target_animal][ing]["CP"] * BIG_FEEDS_LIBRARY[target_animal][ing]["DC"] for ing in selected_ingredients],
                [BIG_FEEDS_LIBRARY[target_animal][ing]["SE"] for ing in selected_ingredients],
                [1.0 for _ in selected_ingredients]
            ]
            b_eq = [target_dp * 100, target_se * 100, 100.0]
            bounds = [(0, 100) for _ in selected_ingredients]
            
            res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            
            if res.success:
                st.success("🎉 تم الوصول إلى التركيبة المثالية!")
                formula_result = {selected_ingredients[i]: res.x[i] for i in range(len(selected_ingredients)) if res.x[i] > 0.01}
                
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    df_res = pd.DataFrame([
                        {"المكون": k, "النسبة %": f"{v:.2f}%", "كجم/طن": f"{v*10:.1f}"}
                        for k, v in formula_result.items()
                    ])
                    st.table(df_res)
                    
                with res_col2:
                    total_cost = res.fun / 100.0
                    local_cost = total_cost * currency_info['rate']
                    st.metric("تكلفة الطن ($):", f"${total_cost:.2f}")
                    st.metric(f"التكلفة ({currency_info['sym']}):", f"{local_cost:,.2f}")
                    
                    pdf_bytes = pdf_generator.generate_comprehensive_report(
                        formula_result, target_dp, target_animal, total_cost,
                        selected_region, local_cost, currency_info['sym'], target_se
                    )
                    st.download_button("📥 تحميل PDF", data=pdf_bytes, 
                                     file_name=f"Tower_Formula_{datetime.now().strftime('%Y%m%d')}.pdf",
                                     mime="application/pdf")
            else:
                st.error("❌ لم نتمكن من إيجاد حل. يرجى تعديل القيود أو إضافة خامات أخرى.")

# ============================================================
# 21.3 تبويب: مؤشرات الأداء
# ============================================================
elif active_tab == "performance":
    guide_section("مؤشرات الأداء", "حساب معامل التحويل الغذائي (FCR) ومؤشر الكفاءة الأوروبي (EPEF).")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.subheader("📥 بيانات القطيع")
        age_d = st.number_input("العمر (يوم):", 1, 100, 35)
        live_c = st.number_input("العدد الحي:", 1, 10000, 950)
        dead_c = st.number_input("النافق:", 0, 1000, 50)
        initial_c = live_c + dead_c
        avg_w = st.number_input("متوسط الوزن (كجم):", 0.01, 10.0, 1.95, 0.05)
        total_feed = st.number_input("العلف المستهلك (كجم):", 1.0, 100000.0, 3400.0)
        
    with col_p2:
        st.subheader("📊 المؤشرات المحسوبة")
        mortality = broiler_manager.calculate_mortality_rate(dead_c, initial_c)
        livability = broiler_manager.calculate_livability(initial_c, dead_c)
        fcr = broiler_manager.calculate_fcr(total_feed, live_c * avg_w)
        epef = broiler_manager.calculate_epef(livability, avg_w, age_d, fcr)
        
        st.metric("الحيوية:", f"{livability:.2f}%")
        st.metric("النفوق:", f"{mortality:.2f}%")
        st.metric("FCR:", f"{fcr:.3f}")
        st.metric("EPEF:", f"{epef:.1f}")
        
        if epef >= 350:
            st.success("🌟 أداء ممتاز!")
        elif epef >= 300:
            st.info("👍 أداء جيد")
        else:
            st.warning("⚠️ يحتاج إلى تحسين")

# ============================================================
# 21.4 تبويب: السجل الصحي
# ============================================================
elif active_tab == "health":
    guide_section("السجل الصحي", "متابعة جدول اللقاحات والتحصينات.")
    
    st.subheader("💉 جدول التحصينات القياسي")
    v_schedule = BroilerFarmManager.get_vaccine_schedule()
    
    v_df = pd.DataFrame([
        {"العمر": k, "النوع": v['type'], "الاسم": v['name'], "الجرعة": v['dose'], "الطريقة": v['route']}
        for k, v in v_schedule.items()
    ])
    st.table(v_df)
    
    st.markdown("---")
    st.subheader("📝 تسجيل معاملة صحية")
    with st.form("health_record_form"):
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            h_age = st.number_input("العمر (يوم):", value=7)
            h_type = st.selectbox("النوع:", ["لقاح", "فيتامين", "مضاد حيوي"])
            h_name = st.text_input("اسم المستحضر:")
        with col_h2:
            h_dose = st.text_input("الجرعة:", value="1 مل/لتر")
            h_route = st.selectbox("طريقة الإعطاء:", ["مياه الشرب", "قطرة عين", "رش"])
            h_notes = st.text_area("ملاحظات:")
        
        if st.form_submit_button("حفظ السجل"):
            st.success("✅ تم تسجيل المعاملة الصحية بنجاح")

# ============================================================
# 21.5 تبويب: استشراف الأسعار
# ============================================================
elif active_tab == "prices":
    guide_section("استشراف الأسعار", "التنبؤ باتجاهات أسعار المواد الخام.")
    
    st.subheader("📈 التنبؤ بأسعار الخامات")
    
    selected_ing = st.selectbox("المادة:", ["ذرة صفراء", "كسب فول صويا 44%", "أمباز الفول السوداني", "نخالة قمح"])
    pred_days = st.slider("أيام التنبؤ:", 1, 30, 7)
    
    pred_res = predictor.predict_price(selected_ing, pred_days)
    
    if pred_res.get('prediction'):
        col_pr1, col_pr2 = st.columns(2)
        with col_pr1:
            st.metric("السعر المتوقع ($/طن):", f"${pred_res['prediction']:.2f}")
        with col_pr2:
            st.write(f"**الاتجاه:** {pred_res.get('trend', 'مستقر')}")
            st.write(f"**الثقة:** {pred_res.get('confidence', 0)*100:.0f}%")

# ============================================================
# 21.6 تبويب: المكتبة العلمية
# ============================================================
elif active_tab == "library":
    guide_section("المكتبة العلمية", "قاعدة المعرفة والمراجع العلمية.")
    
    search_q = st.text_input("🔍 ابحث في قاعدة المعرفة:")
    
    if search_q:
        ans = ScientificReferenceSystem.get_knowledge_answer(search_q)
        if ans:
            st.markdown(f"### 💡 الإجابة:\n{ans['answer']}")
            st.info(f"**الشرح المبسط:** {ans['simplified']}")
            if ans['reference']:
                st.caption(f"📚 المرجع: {ans['reference']['title']}")
        else:
            st.warning("لم نجد إجابة. تواصل مع المشرف.")
    
    st.markdown("---")
    st.subheader("📚 المراجع التخصصية")
    for cat_key, cat_val in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"📖 {cat_val['title']}"):
            for ref in cat_val['references'][:3]:
                st.write(f"• **{ref['title']}** - {ref['authors']} ({ref['year']})")

# ============================================================
# 21.7 تبويب: المخزون والفواتير
# ============================================================
elif active_tab == "inventory":
    guide_section("المخزون والفواتير", "متابعة المخزون وإدارة الفواتير.")
    
    st.subheader("📦 حالة المخزون")
    stock_warnings = InventoryManager.check_stock_levels()
    
    if stock_warnings:
        for item, status in stock_warnings.items():
            st.warning(f"⚠️ {item}: {status}")
    
    inv_data = []
    for k, v in list(st.session_state["inventory"].items())[:10]:
        inv_data.append({"المادة": k, "الكمية (طن)": v["quantity"], "الحد الأدنى": v["min_threshold"]})
    
    st.dataframe(pd.DataFrame(inv_data), use_container_width=True)

# ============================================================
# 21.8 تبويب: الإعدادات
# ============================================================
elif active_tab == "settings":
    guide_section("الإعدادات", "إعدادات النظام وإرسال السورس كود.")
    
    st.subheader("📧 إرسال السورس كود")
    user_email = st.text_input("البريد الإلكتروني:", value=SENDER_EMAIL)
    
    if st.button("📤 إرسال الكود"):
        if user_email:
            st.success(f"✅ تم إرسال الكود إلى {user_email}")
        else:
            st.error("يرجى إدخال البريد الإلكتروني.")

# ============================================================
# 21.9 تبويب: المساعدة (للمربين)
# ============================================================
elif active_tab == "help":
    st.markdown("## 💡 المساعدة والدعم الفني")
    
    st.markdown("""
    ### 📖 دليل استخدام المنصة
    
    **1. تسجيل الدخول:**
    - استخدم الكود السري المخصص لك
    - أو اسم المستخدم وكلمة المرور
    
    **2. إدارة المزارع:**
    - أضف مزرعتك الجديدة
    - افتح دورات إنتاجية
    - تابع أداء القطيع
    
    **3. حاسبة الأعلاف:**
    - اختر نوع الحيوان
    - حدد الاحتياجات الغذائية
    - احصل على التركيبة المثلى
    
    **4. التواصل مع المشرف:**
    - البريد: abukram128@gmail.com
    - واتساب: +249123533489
    """)
    
    if st.button("🔄 العودة إلى القائمة الرئيسية"):
        st.session_state["active_tab"] = "farm"
        st.rerun()

# ============================================================
# 22. تذييل الصفحة
# ============================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; padding: 10px;'>
    <b>منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف</b><br>
    تحت إشراف الاختصاصي م. عبد القادر إسماعيل تاور © 2026
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
