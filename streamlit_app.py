# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 3.3 (نظام إدارة المزارع المتكامل مع حفظ البيانات)
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
# ============================================================================

# Digital Signature: 110dfcb10bc6902ee96175517109d7c7
# Generated: 2026-07-21T15:30:00.000000

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

# ===== دوال الصوت والنصوص =====
def play_audio_from_text(text, lang="ar"):
    """توليد وتشغيل صوت من نص"""
    if not GTTS_AVAILABLE:
        st.warning("⚠️ مكتبة gTTS غير مثبتة، لا يمكن تشغيل الصوت.")
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

def play_basmala_audio():
    """تشغيل البسملة الصوتية عند تحميل الصفحة"""
    # محاولة استخدام ملف صوتي محلي أولاً
    audio_html = """
    <audio id="basmalaAudio" preload="auto">
      <source src="basmala.mp3" type="audio/mpeg">
    </audio>
    <script>
      window.addEventListener('DOMContentLoaded', (event) => {
        const audio = document.getElementById('basmalaAudio');
        audio.play().catch(error => {
          console.log("التشغيل التلقائي محجوب بواسطة المتصفح");
        });
      });
    </script>
    """
    
    # إذا لم يكن الملف المحلي موجوداً، استخدم gTTS لتوليد الصوت
    if not os.path.exists("basmala.mp3"):
        try:
            tts = gTTS(text="بسم الله الرحمن الرحيم", lang="ar")
            audio_file = io.BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            audio_b64 = base64.b64encode(audio_file.read()).decode()
            st.components.v1.html(
                f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>',
                height=0
            )
        except Exception as e:
            st.warning(f"⚠️ تعذر تشغيل البسملة: {e}")
    else:
        st.components.v1.html(audio_html, height=0)

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
# 1. نظام قاعدة البيانات المتقدم (حفظ دائم)
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
        
        # جدول المزارع (موسع)
        c.execute('''CREATE TABLE IF NOT EXISTS farms
                     (farm_id TEXT PRIMARY KEY,
                      farm_name TEXT UNIQUE,
                      farm_type TEXT,
                      owner_name TEXT,
                      owner_phone TEXT,
                      location TEXT,
                      created_date TEXT,
                      last_updated TEXT)''')
        
        # جدول دورات الإنتاج (للاحم والبياض)
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
        
        # جدول السجلات اليومية (موسع)
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
        
        # جدول السجل الصحي (اللقاحات والأدوية)
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
# 2. نظام إدارة المزارع المتقدم
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
        # حساب المؤشرات
        live_birds = record_data.get('live_birds', 0)
        avg_weight = record_data.get('avg_weight', 0)
        feed_consumed = record_data.get('feed_consumed', 0)
        dead_count = record_data.get('dead_count', 0)
        initial_count = record_data.get('initial_count', live_birds + dead_count)
        
        # حساب FCR
        total_gain = live_birds * avg_weight
        feed_conversion = feed_consumed / total_gain if total_gain > 0 else 0
        
        # حساب نسبة النفوق
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
        
        # إنشاء مقارنة أداء
        self._create_performance_comparison(cycle_id, record_data)
        
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
    
    def _create_performance_comparison(self, cycle_id: str, record_data: dict):
        """إنشاء مقارنة أداء مع المعايير القياسية"""
        age_days = record_data.get('age_days', 0)
        avg_weight = record_data.get('avg_weight', 0)
        feed_conversion = record_data.get('feed_conversion', 0)
        mortality_rate = record_data.get('mortality_rate', 0)
        
        # المعايير القياسية للدجاج اللاحم (Ross 308)
        standard_weights = {
            1: 0.045, 7: 0.180, 14: 0.450, 21: 0.850,
            28: 1.350, 35: 1.950, 42: 2.550
        }
        standard_fcr = {
            1: 1.0, 7: 1.2, 14: 1.4, 21: 1.6,
            28: 1.7, 35: 1.8, 42: 1.9
        }
        standard_mortality = {
            1: 0.5, 7: 0.8, 14: 1.0, 21: 1.2,
            28: 1.5, 35: 1.8, 42: 2.0
        }
        
        # الحصول على أقرب عمر قياسي
        ages = sorted(standard_weights.keys())
        closest_age = min(ages, key=lambda x: abs(x - age_days))
        
        std_weight = standard_weights.get(closest_age, avg_weight)
        std_fcr = standard_fcr.get(closest_age, feed_conversion)
        std_mortality = standard_mortality.get(closest_age, mortality_rate)
        
        # حساب الانحرافات
        weight_dev = ((avg_weight - std_weight) / std_weight) * 100 if std_weight > 0 else 0
        fcr_dev = ((feed_conversion - std_fcr) / std_fcr) * 100 if std_fcr > 0 else 0
        mort_dev = ((mortality_rate - std_mortality) / std_mortality) * 100 if std_mortality > 0 else 0
        
        # إنشاء سجلات المقارنة
        metrics = [
            ('وزن الجسم', avg_weight, std_weight, weight_dev),
            ('معامل التحويل', feed_conversion, std_fcr, fcr_dev),
            ('نسبة النفوق', mortality_rate, std_mortality, mort_dev)
        ]
        
        for metric_name, farm_val, std_val, deviation in metrics:
            status = 'ممتاز' if abs(deviation) < 5 else ('جيد' if abs(deviation) < 10 else 'بحاجة إلى تحسين')
            comp_id = secrets.token_hex(16)
            comp_data = {
                'comparison_id': comp_id,
                'cycle_id': cycle_id,
                'comparison_date': datetime.now().isoformat(),
                'metric_type': metric_name,
                'farm_value': farm_val,
                'standard_value': std_val,
                'deviation': deviation,
                'status': status
            }
            self.db.insert_record('performance_comparisons', comp_data)
    
    def get_farm_data(self, farm_id: str) -> dict:
        """استرجاع بيانات المزرعة الكاملة"""
        farm_data = self.db.get_records('farms', {'farm_id': farm_id})
        if not farm_data:
            return None
        
        farm = farm_data[0]
        cycles = self.db.get_records('production_cycles', {'farm_id': farm_id})
        
        result = {
            'farm_id': farm[0],
            'farm_name': farm[1],
            'farm_type': farm[2],
            'owner_name': farm[3],
            'owner_phone': farm[4],
            'location': farm[5],
            'created_date': farm[6],
            'cycles': []
        }
        
        for cycle in cycles:
            cycle_id = cycle[0]
            daily_records = self.db.get_records('daily_records', {'cycle_id': cycle_id})
            health_records = self.db.get_records('health_records', {'cycle_id': cycle_id})
            comparisons = self.db.get_records('performance_comparisons', {'cycle_id': cycle_id})
            
            result['cycles'].append({
                'cycle_id': cycle_id,
                'cycle_type': cycle[2],
                'start_date': cycle[3],
                'end_date': cycle[4],
                'initial_count': cycle[5],
                'breed': cycle[6],
                'target_weight': cycle[7],
                'target_age': cycle[8],
                'status': cycle[9],
                'daily_records': daily_records,
                'health_records': health_records,
                'comparisons': comparisons
            })
        
        return result
    
    def get_active_cycles(self, farm_id: str = None) -> List:
        if farm_id:
            return self.db.get_records('production_cycles', {'farm_id': farm_id, 'status': 'active'})
        else:
            return self.db.get_records('production_cycles', {'status': 'active'})
    
    def close_cycle(self, cycle_id: str):
        self.db.update_record('production_cycles', 
                            {'status': 'completed', 'end_date': datetime.now().isoformat()},
                            {'cycle_id': cycle_id})
    
    def get_performance_summary(self, cycle_id: str) -> dict:
        """الحصول على ملخص أداء الدورة"""
        records = self.db.get_records('daily_records', {'cycle_id': cycle_id})
        if not records:
            return None
        
        latest_record = records[-1] if records else None
        first_record = records[0] if records else None
        
        total_dead = sum(r[11] for r in records)
        total_culled = sum(r[12] for r in records)
        initial_count = first_record[0] if first_record else 0
        
        summary = {
            'total_days': latest_record[3] if latest_record else 0,
            'final_weight': latest_record[5] if latest_record else 0,
            'total_feed': sum(r[9] for r in records),
            'total_dead': total_dead,
            'total_culled': total_culled,
            'mortality_rate': (total_dead / initial_count * 100) if initial_count > 0 else 0,
            'final_livability': ((initial_count - total_dead - total_culled) / initial_count * 100) if initial_count > 0 else 0,
            'avg_fcr': sum(r[15] for r in records) / len(records) if records else 0
        }
        
        # حساب EPEF
        livability = summary['final_livability']
        final_weight = summary['final_weight']
        total_days = summary['total_days']
        avg_fcr = summary['avg_fcr']
        epef = (livability * final_weight) / (total_days * avg_fcr) * 100 if total_days > 0 and avg_fcr > 0 else 0
        summary['epef'] = epef
        
        return summary
    
    def check_vaccine_alerts(self, cycle_id: str) -> List:
        """فحص تنبيهات اللقاحات المستحقة"""
        cycle = self.db.get_records('production_cycles', {'cycle_id': cycle_id})
        if not cycle:
            return []
        
        # جدول اللقاحات القياسي
        standard_vaccines = {
            1: {'type': 'فيتامين', 'name': 'فيتامين AD3E', 'dose': '1 مل/لتر', 'route': 'مياه الشرب'},
            7: {'type': 'لقاح', 'name': 'نيوكاسل (Lasota)', 'dose': 'قطرة عين', 'route': 'قطرة عين/أنف'},
            14: {'type': 'لقاح', 'name': 'Gumboro (Intermediate)', 'dose': 'قطرة فم', 'route': 'مياه الشرب'},
            21: {'type': 'دواء', 'name': 'مضاد كوكسيديا (Amprolium)', 'dose': '1 جم/لتر', 'route': 'مياه الشرب لمدة 3 أيام'},
            28: {'type': 'فيتامين', 'name': 'فيتامين C + E', 'dose': '0.5 جم/لتر', 'route': 'مياه الشرب'},
            35: {'type': 'لقاح', 'name': 'Gumboro booster', 'dose': 'قطرة فم', 'route': 'مياه الشرب'},
            42: {'type': 'لقاح', 'name': 'نيوكاسل (بخاخ)', 'dose': 'بخاخ', 'route': 'رش'},
        }
        
        # الحصول على آخر سجل يومي
        records = self.db.get_records('daily_records', {'cycle_id': cycle_id})
        if not records:
            return []
        
        latest_age = records[-1][3] if records else 0
        
        # التحقق من اللقاحات المستحقة
        alerts = []
        for age, vaccine in standard_vaccines.items():
            if age >= latest_age and age <= latest_age + 2:
                # التحقق مما إذا تم إعطاء اللقاح بالفعل
                health_records = self.db.get_records('health_records', {'cycle_id': cycle_id})
                existing = [h for h in health_records if h[3] == age and h[4] == vaccine['type']]
                if not existing:
                    alert_id = secrets.token_hex(16)
                    alert_data = {
                        'alert_id': alert_id,
                        'cycle_id': cycle_id,
                        'alert_date': datetime.now().isoformat(),
                        'scheduled_date': (datetime.now() + timedelta(days=1)).isoformat(),
                        'vaccine_name': vaccine['name'],
                        'vaccine_type': vaccine['type'],
                        'dose': vaccine['dose'],
                        'route': vaccine['route'],
                        'status': 'pending',
                        'sent': 0
                    }
                    self.db.insert_record('vaccine_alerts', alert_data)
                    alerts.append(alert_data)
        
        return alerts

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
# 4. نظام التنبؤ بالأسعار
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
# 5. نظام المراجع العلمية (كامل)
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
                {"id": "REF005", "authors": "Bryden, W.L., Li, X., Ravindran, G.",
                 "year": 2009, "title": "Digestible Amino Acids in Poultry Feed Ingredients",
                 "publisher": "University of Sydney",
                 "summary": "دراسة شاملة عن الأحماض الأمينية المهضومة في مواد العلف للدواجن."}
            ]
        },
        "energy_carbohydrates": {
            "title": "الطاقة والكربوهيدرات",
            "references": [
                {"id": "REF006", "authors": "Van Soest, P.J.",
                 "year": 1994, "title": "Nutritional Ecology of the Ruminant",
                 "publisher": "Cornell University Press", "edition": "2nd Edition",
                 "isbn": "978-0801427725", "summary": "المرجع الكلاسيكي في تغذية المجترات وتحليل الألياف."},
                {"id": "REF007", "authors": "Blaxter, K.L.",
                 "year": 1989, "title": "Energy Metabolism in Animals and Man",
                 "publisher": "Cambridge University Press", "isbn": "978-0521369433",
                 "summary": "دراسة متعمقة في أيض الطاقة في الحيوانات والإنسان."}
            ]
        },
        "minerals_vitamins": {
            "title": "المعادن والفيتامينات",
            "references": [
                {"id": "REF008", "authors": "Underwood, E.J., Suttle, N.F.",
                 "year": 1999, "title": "The Mineral Nutrition of Livestock",
                 "publisher": "CABI", "edition": "3rd Edition", "isbn": "978-0851991283",
                 "summary": "المرجع الشامل في تغذية المعادن للثروة الحيوانية."},
                {"id": "REF009", "authors": "McDowell, L.R.",
                 "year": 2000, "title": "Vitamins in Animal Nutrition",
                 "publisher": "Academic Press", "isbn": "978-0124833724",
                 "summary": "دراسة متكاملة عن الفيتامينات ودورها في تغذية الحيوان."}
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
        "ruminants": {
            "title": "تغذية المجترات",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.",
                 "year": 1993, "title": "The Ruminant Animal: Digestive Physiology and Nutrition",
                 "publisher": "Waveland Press", "isbn": "978-0881337389",
                 "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات."},
                {"id": "REF013", "authors": "Minson, D.J.",
                 "year": 1990, "title": "Forage in Ruminant Nutrition",
                 "publisher": "Academic Press", "isbn": "978-0124983108",
                 "summary": "دراسة متخصصة في تغذية المجترات على الأعلاف الخشنة."}
            ]
        },
        "sheep_goats": {
            "title": "تغذية الأغنام والماعز",
            "references": [
                {"id": "REF014", "authors": "NRC (National Research Council)",
                 "year": 2007, "title": "Nutrient Requirements of Small Ruminants",
                 "publisher": "National Academies Press", "isbn": "978-0309102131",
                 "summary": "المرجع الرسمي لمتطلبات الأغنام والماعز والمجترات الصغيرة."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول",
            "references": [
                {"id": "REF015", "authors": "NRC (National Research Council)",
                 "year": 2007, "title": "Nutrient Requirements of Horses",
                 "publisher": "National Academies Press", "edition": "6th Revised Edition",
                 "isbn": "978-0309102124", "summary": "المرجع الأساسي في تغذية الخيول ومتطلباتها الغذائية."}
            ]
        },
        "aquaculture": {
            "title": "تغذية الأسماك",
            "references": [
                {"id": "REF016", "authors": "Halver, J.E., Hardy, R.W.",
                 "year": 2002, "title": "Fish Nutrition",
                 "publisher": "Academic Press", "edition": "3rd Edition",
                 "isbn": "978-0123196521", "summary": "المرجع الشامل في تغذية الأسماك والمزارع المائية."}
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
                 "publisher": "Cobb-Vantress", "summary": "الدليل المتخصص لإدارة دجاج اللاحم سلالة كوب."},
                {"id": "REF022", "authors": "ASPCA",
                 "year": 2019, "title": "Poultry Welfare Standards",
                 "publisher": "ASPCA", "summary": "معايير رعاية الدواجن ورفاهيتها."}
            ]
        },
        "digestible_protein": {
            "title": "البروتين المهضوم",
            "references": [
                {"id": "REF023", "authors": "INRA (Institut National de la Recherche Agronomique)",
                 "year": 2007, "title": "INRA Feeding System for Ruminants",
                 "publisher": "Wageningen Academic Publishers", "isbn": "978-9086860197",
                 "summary": "النظام الفرنسي المتقدم لتغذية المجترات وتقدير البروتين المهضوم."},
                {"id": "REF024", "authors": "Pesti, G.M., Miller, B.R.",
                 "year": 2009, "title": "Least-Cost Feed Formulation: Theory and Practice",
                 "publisher": "University of Georgia", "summary": "النظرية والتطبيق العملي لتركيب الأعلاف بأقل تكلفة."}
            ]
        },
        "layer": {
            "title": "إنتاج الدجاج البياض",
            "references": [
                {"id": "REF025", "authors": "Hy-Line International",
                 "year": 2021, "title": "Hy-Line Management Guide",
                 "publisher": "Hy-Line", "summary": "الدليل المتخصص لإدارة الدجاج البياض سلالة هاي لاين."},
                {"id": "REF026", "authors": "ISA Babcock",
                 "year": 2020, "title": "ISA Brown Management Guide",
                 "publisher": "ISA", "summary": "الدليل الشامل لإدارة الدجاج البياض سلالة ISA براون."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم لكل مادة علفية. هذا المقياس أدق من البروتين الخام لأنه يعكس القيمة الغذائية الحقيقية التي يستفيد منها الحيوان.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً، وليس مجرد الكمية الموجودة في العلف."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي. يستخدم هذا المقياس لتقييم كفاءة الطاقة في الأعلاف المختلفة.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف، وكلما زاد الرقم زادت الطاقة التي يمنحها للحيوان."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming) الذي يحسب أقل تكلفة لتحقيق متطلبات غذائية محددة. تشمل المتطلبات: البروتين المهضوم، الطاقة، الألياف، المعادن، والفيتامينات.",
            "reference": "REF024",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية تلبي جميع احتياجات الحيوان الغذائية."
        },
        "ما هي أهمية إضافة الإنزيمات للأعلاف": {
            "answer": "الإنزيمات في الأعلاف تعمل على تحسين هضم واستفادة الحيوان من العناصر الغذائية. الإنزيمات مثل الفايتيز تحرر الفسفور المرتبط، وإنزيمات NSP تكسر جدران الخلايا النباتية مما يزيد من هضم الكربوهيدرات.",
            "reference": "REF010",
            "simplified": "الإنزيمات تساعد الحيوان على هضم العلف بشكل أفضل، مما يوفر في تكاليف التغذية ويحسن الإنتاج."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF (European Production Efficiency Factor) هو مقياس شامل لكفاءة إنتاج الدجاج اللاحم. يحسب بالمعادلة: EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل الغذائي) × 100.",
            "reference": "REF020",
            "simplified": "EPEF هو رقم يعبر عن كفاءة مزرعة الدجاج، وكلما كان أعلى دل ذلك على إنتاجية أفضل."
        },
        "ما هو الفرق بين البروتين الخام والمهضوم": {
            "answer": "البروتين الخام (CP) هو إجمالي محتوى النيتروجين في العلف مضروباً في 6.25، بينما البروتين المهضوم (DP) هو الجزء الذي يتم هضمه وامتصاصه فعلياً. DP = CP × معامل الهضم.",
            "reference": "REF023",
            "simplified": "البروتين الخام هو كل البروتين الموجود، أما المهضوم فهو الجزء الذي يستفيد منه الحيوان فعلياً."
        },
        "كيف يتم حساب معامل التحويل الغذائي FCR": {
            "answer": "معامل التحويل الغذائي FCR = كمية العلف المستهلك / كمية الوزن المكتسب. مثال: إذا استهلك طائر 3 كجم علف واكتسب 1.5 كجم وزن، فإن FCR = 3/1.5 = 2.0.",
            "reference": "REF018",
            "simplified": "FCR يبين كمية العلف التي يحتاجها الحيوان ليكتسب كيلو جرام واحد من الوزن."
        },
        "كيف يمكن تحسين كفاءة مزرعة الدجاج": {
            "answer": "تحسين كفاءة مزرعة الدجاج يتم من خلال: 1. استخدام برامج تغذية دقيقة. 2. تطبيق بروتوكول تحصين صارم. 3. التحكم الدقيق في البيئة. 4. مراقبة جودة العلف والماء.",
            "reference": "REF021",
            "simplified": "لتحسين مزرعة الدجاج: استخدم تغذية دقيقة، حافظ على نظافة البيئة، طبق برامج تحصين، وراقب أداء القطيع يومياً."
        },
        "ما هي أهمية بيكربونات الصوديوم في أعلاف المجترات": {
            "answer": "تستخدم بيكربونات الصوديوم في أعلاف المجترات كمنظم لحموضة الكرش. تعمل على معادلة الأحماض الناتجة عن تخمر الكربوهيدرات، وتمنع حدوث الحماض الكرشي.",
            "reference": "REF012",
            "simplified": "بيكربونات الصوديوم تحافظ على توازن الحموضة في كرش الحيوان، مما يمنع مشاكل الهضم."
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
# 6. إعدادات المنصة
# ============================================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_caching_system():
    return {"cache_hits": 0, "cache_misses": 0, "last_cleanup": datetime.now()}
CACHE_SYSTEM = init_caching_system()

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
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except Exception:
                pass
    return None
img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email):
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or not SENDER_PASSWORD:
        st.error("⚠️ خطأ إعدادات SMTP.")
        return False
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود - منصة تاور العلمية"
    body = "السلام عليكم، مرفق الكود الكامل للمنصة."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code = f.read()
        attachment = MIMEText(code, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_platform.py")
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
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

arabic_processor = ArabicTextProcessor()

# ============================================================
# 7. مولد PDF
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
        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], title=arabic_processor.fix_arabic_text("المكونات"),
                         loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026 | تحت إشراف م. عبد القادر إسماعيل تاور", size=9, align=TA_CENTER, color=HexColor('#666666')))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ============================================================
# 8. كلاس إدارة مزارع الدجاج (محسّن مع حفظ دائم)
# ============================================================
class BroilerFarmManager:
    def __init__(self):
        self.farm_system = FarmManagementSystem()
    
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
    def calculate_cull_rate(culled_count, initial_count):
        if initial_count <= 0:
            return 0.0
        return (culled_count / initial_count) * 100.0
    
    @staticmethod
    def calculate_livability(initial_count, dead_count):
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)
    
    @staticmethod
    def calculate_epef(livability, body_weight_kg, age_days, fcr):
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0
    
    @staticmethod
    def get_standard_performance(age_days, breed_type="broiler"):
        """الحصول على المعايير القياسية للأداء"""
        if breed_type == "broiler":
            # معايير Ross 308
            standards = {
                1: {'weight': 0.045, 'fcr': 1.0, 'mortality': 0.5},
                7: {'weight': 0.180, 'fcr': 1.2, 'mortality': 0.8},
                14: {'weight': 0.450, 'fcr': 1.4, 'mortality': 1.0},
                21: {'weight': 0.850, 'fcr': 1.6, 'mortality': 1.2},
                28: {'weight': 1.350, 'fcr': 1.7, 'mortality': 1.5},
                35: {'weight': 1.950, 'fcr': 1.8, 'mortality': 1.8},
                42: {'weight': 2.550, 'fcr': 1.9, 'mortality': 2.0}
            }
        elif breed_type == "layer":
            # معايير Hy-Line
            standards = {
                1: {'weight': 0.040, 'fcr': 1.2, 'mortality': 0.3},
                14: {'weight': 0.120, 'fcr': 1.5, 'mortality': 0.5},
                28: {'weight': 0.350, 'fcr': 1.8, 'mortality': 0.8},
                42: {'weight': 0.700, 'fcr': 2.0, 'mortality': 1.0},
                56: {'weight': 1.100, 'fcr': 2.2, 'mortality': 1.2},
                70: {'weight': 1.500, 'fcr': 2.4, 'mortality': 1.5}
            }
        else:
            standards = {}
        
        # الحصول على أقرب عمر قياسي
        ages = sorted(standards.keys())
        if not ages:
            return None
        closest_age = min(ages, key=lambda x: abs(x - age_days))
        return standards.get(closest_age, None)
    
    @staticmethod
    def get_temp_humidity_table():
        return pd.DataFrame({
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55]
        })
    
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
# 9. مكتبة الأعلاف الكاملة (موسعة)
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
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0},
        "تفل العنب المجفف": {"CP": 12.0, "DC": 0.50, "SE": 45.0, "NDF": 45.0, "ADF": 30.0, "EE": 5.0, "ASH": 8.0},
        "نخالة الأرز الدهنية": {"CP": 12.5, "DC": 0.70, "SE": 55.0, "NDF": 30.0, "ADF": 15.0, "EE": 15.0, "ASH": 8.0},
        "علف الشعير المستنبت": {"CP": 15.0, "DC": 0.75, "SE": 60.0, "NDF": 25.0, "ADF": 12.0, "EE": 3.0, "ASH": 5.0}
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
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
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "مخلفات مصانع البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0, "EE": 12.0, "ASH": 3.0},
        "قش الأرز المعالج": {"CP": 4.0, "DC": 0.40, "SE": 25.0, "NDF": 65.0, "ADF": 40.0, "EE": 1.5, "ASH": 12.0}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
        "بروتين مصل الحليب (WPC)": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0},
        "بروتين الدم المجفف": {"CP": 85.0, "DC": 0.92, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.5, "ASH": 5.0}
    },
    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات (مع خميرة الخبز)": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0},
        "كلوريد الكولين (Choline Chloride)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 75.0}
    }
}

# ============================================================
# 10. نظام أسعار المدن والمخازن
# ============================================================
CITY_PRICES_FILE = "city_prices.json"
def load_city_prices():
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
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
                        "quantity": 25.0,
                        "min_threshold": 5.0,
                        "unit": "طن",
                        "last_updated": datetime.now().isoformat(),
                        "price_history": [],
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

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0, "كتكوت لاحم عمر يوم ($)": 0.65, "دجاج بياض عمر البشاير ($)": 5.50
    }
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50, "كيلو لحم ضأن طازج ($)": 9.00,
        "كيلو لحم دجاج لاحم صافي ($)": 3.80, "طبق بيض مائدة 30 بيضة ($)": 4.20,
        "رطل / لتر حليب خام ($)": 0.90, "كيلو جبن أبيض محلي ($)": 5.00,
        "كيلو جبن جاف / شيدر ($)": 8.50
    }
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = (
        "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا لتبادل الخبرات التركيبية.\n"
        "• [ملاحظة مختص]: تم مراجعة جودة كسب زهرة الشمس المتاح حالياً بالأسواق ونوصي بضبط ألياف الخيل بناءً عليه.\n"
    )

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
            "بيكربونات الصوديوم (الصودا)": 340.0,
            "خميرة الخبز (Yeast)": 450.0,
            "كسب بذرة القطن غير المقشور": 320.0,
            "كسب بذور اللفت (كانولا)": 380.0,
            "كسب زهرة الشمس الكامل": 290.0,
            "تفل العنب المجفف": 180.0,
            "نخالة الأرز الدهنية": 160.0,
            "علف الشعير المستنبت": 200.0,
            "مخلفات مصانع البسكويت": 220.0,
            "قش الأرز المعالج": 80.0,
            "بروتين مصل الحليب (WPC)": 1200.0,
            "بروتين الدم المجفف": 950.0,
            "كلوريد الكولين (Choline Chloride)": 600.0
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

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state: st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ============================================================
# 11. حالة الجلسة
# ============================================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "session_token" not in st.session_state: st.session_state["session_token"] = None
if "farms" not in st.session_state:
    st.session_state["farms"] = {}
if "selected_farm_id" not in st.session_state:
    st.session_state["selected_farm_id"] = None
if "selected_cycle_id" not in st.session_state:
    st.session_state["selected_cycle_id"] = None
if "whatsapp_alerts_sent" not in st.session_state:
    st.session_state["whatsapp_alerts_sent"] = {}
if "query_history" not in st.session_state:
    st.session_state["query_history"] = []
if "audio_played" not in st.session_state:
    st.session_state["audio_played"] = False
if "basmala_played" not in st.session_state:
    st.session_state["basmala_played"] = False

# تهيئة نظام إدارة المزارع
farm_system = FarmManagementSystem()
broiler_manager = BroilerFarmManager()

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

# تحميل البيانات عند بدء التشغيل
if not st.session_state["farms"]:
    load_farms_from_db()

def send_whatsapp_broiler_alert(phone_number, message):
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
    st.markdown(f"<div style='background:#e8f5e9; padding:10px; border-radius:8px; direction:ltr;'>📲 <b>تنبيه عبر واتساب:</b> <a href='{whatsapp_url}' target='_blank'>اضغط لإرسال الرسالة إلى {phone_number}</a><br>{message}</div>", unsafe_allow_html=True)

def check_and_alert_medications(cycle_id, farm_phone, current_age):
    alerts = farm_system.check_vaccine_alerts(cycle_id)
    for alert in alerts:
        key = f"{cycle_id}_{alert['scheduled_date']}_{alert['vaccine_name']}"
        if key not in st.session_state["whatsapp_alerts_sent"]:
            alert_msg = f"🔔 تنبيه لدورة الإنتاج (العمر {current_age} يوم):\n{alert['vaccine_type']} {alert['vaccine_name']} - الجرعة: {alert['dose']} - طريقة الإعطاء: {alert['route']}"
            send_whatsapp_broiler_alert(farm_phone, alert_msg)
            st.session_state["whatsapp_alerts_sent"][key] = datetime.now().isoformat()
    return alerts

# ============================================================
# 12. CSS المحسّن
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
    h1, h2, h3, h4, h5, p, span, li, div, label, .stMarkdown, .stTextInput, .stNumberInput, .stSelectbox {
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
    .stButton > button:hover {
        background-color: #c8e6c9 !important;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-list"] button {
        color: #1a1a1a !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #1b5e20 !important;
        font-weight: bold;
    }
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        color: #1a1a1a !important;
    }
    .stAlert * { color: #1a1a1a !important; }
    .comparison-good {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 5px 10px;
        border-radius: 5px;
        color: #2e7d32 !important;
        font-weight: bold;
    }
    .comparison-warning {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        padding: 5px 10px;
        border-radius: 5px;
        color: #e65100 !important;
        font-weight: bold;
    }
    .comparison-excellent {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        padding: 5px 10px;
        border-radius: 5px;
        color: #0d47a1 !important;
        font-weight: bold;
    }
    
    /* تنسيق زر البسملة */
    .basmala-button {
        background: linear-gradient(135deg, #1a237e, #283593);
        color: white !important;
        padding: 12px 25px;
        border-radius: 30px;
        border: none;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(26, 35, 126, 0.3);
        margin: 10px 0;
        width: 100%;
    }
    .basmala-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(26, 35, 126, 0.4);
        background: linear-gradient(135deg, #283593, #1a237e);
    }
    .basmala-button:active {
        transform: translateY(0px);
    }
    .basmala-container {
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #e8eaf6, #c5cae9);
        border-radius: 15px;
        margin: 20px 0;
        border: 2px solid #1a237e;
    }
    .basmala-text {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1a237e !important;
        font-family: 'Traditional Arabic', 'Amiri', serif;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 13. بوابة الدخول
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
    
    # عرض البسملة في صفحة الدخول
    st.markdown("""
    <div class="basmala-container">
        <p class="basmala-text">بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#1a1a1a;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)

    # تشغيل البسملة عند ظهور صفحة الدخول (مرة واحدة)
    if not st.session_state.get("basmala_played", False):
        # محاولة تشغيل البسملة
        basmala_html = """
        <audio id="basmalaAudio" preload="auto">
          <source src="basmala.mp3" type="audio/mpeg">
        </audio>
        <script>
          window.addEventListener('DOMContentLoaded', function() {
            var audio = document.getElementById('basmalaAudio');
            if (audio) {
              audio.play().catch(function(e) {
                console.log("التشغيل التلقائي محجوب: " + e);
              });
            }
          });
        </script>
        """
        st.components.v1.html(basmala_html, height=0)
        st.session_state["basmala_played"] = True

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

# تشغيل الصوت الترحيبي بعد المصادقة (مرة واحدة)
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
# 14. الواجهة الرئيسية
# ============================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# ===== عرض البسملة في الواجهة الرئيسية مع زر تشغيل =====
col_basmala1, col_basmala2, col_basmala3 = st.columns([1, 2, 1])
with col_basmala2:
    st.markdown("""
    <div class="basmala-container" style="margin: 10px 0 20px 0;">
        <p class="basmala-text">بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ</p>
    </div>
    """, unsafe_allow_html=True)
    
    # زر لتشغيل البسملة عند الطلب
    if st.button("🔊 تشغيل البسملة", key="play_basmala", use_container_width=True):
        # محاولة تشغيل البسملة
        basmala_html = """
        <audio id="basmalaAudioPlay" preload="auto">
          <source src="basmala.mp3" type="audio/mpeg">
        </audio>
        <script>
          var audio = document.getElementById('basmalaAudioPlay');
          if (audio) {
            audio.play().catch(function(e) {
              console.log("تعذر التشغيل: " + e);
            });
          }
        </script>
        """
        st.components.v1.html(basmala_html, height=0)

# ===== إضافة زر إرسال الكود إلى بريد المالك =====
if st.session_state["user_role"] == "owner":
    with st.expander("📧 إرسال السورس كود إلى بريد المالك", expanded=False):
        col_mail1, col_mail2 = st.columns([2, 1])
        with col_mail1:
            target_email = st.text_input("البريد الإلكتروني المستلم:", value=OWNER_EMAIL, key="mail_recipient")
        with col_mail2:
            if st.button("📤 إرسال الكود الآن", use_container_width=True):
                if send_code_to_mail(target_email):
                    st.success(f"✅ تم إرسال الكود بنجاح إلى {target_email}")
                else:
                    st.error("❌ فشل الإرسال، تأكد من إعدادات SMTP.")
        st.caption("⚠️ يتم إرسال ملف الكود الكامل (tower_platform.py) كمرفق عبر البريد الإلكتروني.")

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_info = {"owner": "الاختصاصي م. عبد القادر إسماعيل تاور 👑", "specialist": "المختص والزملاء 👨‍🔬", "breeder": "المربي 🌾"}
    st.markdown(f"""<div style='text-align: left; font-size:0.9rem; color:#1a1a1a; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); padding: 10px; border-radius: 10px;'>الحساب: <b>{role_info.get(st.session_state["user_role"], "مستخدم")}</b><br><small>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></div>""", unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != "inventory" and key != "farms":
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style pulse-animation">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم (DP) ومعادل النشاء (SE)</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

st.markdown("### 📢 المشاركة التسويقية والدعوة العلمية")
share_text_payload = """📢 دعوة علمية وتسويقية من منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف

إلى كل مهتم بتطوير الثروة الحيوانية؛ من أطباء بيطريين، اختصاصيي إنتاج حيواني، ومربين طموحين:
يسعدنا دعوتكم لاستخدام وتجربة المنصة المتقدمة لتركيب وتطوير الأعلاف، بإشراف وتصميم:
[ الاختصاصي م. عبد القادر إسماعيل تاور ]

🎯 ما تقدمه المنصة:
• حلول برمجية ذكية لتركيب أعلاف اقتصادية على أساس البروتين المهضوم ومعادل النشاء (Least-Cost Formulation).
• أدوات دقيقة لحساب الاحتياجات الغذائية بما يضمن أعلى معدلات نمو وإنتاجية.
• دعم كامل للعمل الميداني والبحث العلمي والخصم التلقائي للمستودعات في مكان واحد.
• نظام تحليلات متقدم وتقارير PDF احترافية
• إدارة مزارع الدجاج اللاحم مع حساب KPIs و EPEF (خاص بالمالك)

🔗 رابط المنصة: [ضع رابط موقعك هنا]"""
st.text_area("النص الدعائي والإعلامي الجاهز للنشر:", value=share_text_payload, height=140, key="top_share_box")
col_copy, col_share = st.columns(2)
with col_copy:
    if st.button("📋 نسخ الرابط والنص للدعاية والتسويق", type="secondary", use_container_width=True):
        st.success("تم التجهيز بنجاح! يمكنك الآن نسخ النص ومشاركته عبر المجموعات والمنصات.")
with col_share:
    encoded_share = urllib.parse.quote(share_text_payload[:200])
    st.link_button("📲 مشاركة مباشرة عبر واتساب", f"https://wa.me/?text={encoded_share}", use_container_width=True)

st.markdown("---")

welcome_messages = {
    "owner": {"bg": "#eff6ff", "border": "#1d4ed8", "text": "👑 أهلاً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل الآن بكفاءة متناهية. كما تم تفعيل إدارة مزارع الدجاج اللاحم مع حفظ دائم للبيانات."},
    "specialist": {"bg": "#f0fdf4", "border": "#16a34a", "text": "🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد الاختصاصي م. عبد القادر إسماعيل تاور بالترحيب بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني."},
    "breeder": {"bg": "#fffbeb", "border": "#d97706", "text": "🚜 أهلاً وسهلاً بكم في منصة تاور العلمية. نرحب بإخواننا المربين. نوفر لكم خلطات مبنية على القيمة الغذائية الحقيقية الممتصة لضمان التوفير المالي العالي."}
}
current_welcome = welcome_messages.get(st.session_state["user_role"], welcome_messages["breeder"])
st.markdown(f"""<div style='background-color: {current_welcome["bg"]}; padding: 15px; border-radius: 8px; border-right: 5px solid {current_welcome["border"]}; text-align: right; direction: rtl; margin-bottom: 20px;'><b>{current_welcome["text"]}</b></div>""", unsafe_allow_html=True)

# ============================================================
# 15. تحديد التبويبات
# ============================================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "🐔 إدارة المزارع والدورات الإنتاجية",
        "📊 بورصة الأسعار المركزية",
        "🏭 إدارة المستودعات الذكية",
        "🧾 التسويق وفواتير البيع",
        "🖨️ مصمم الديباجة والدعاية",
        "📈 التحليلات المتقدمة",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "🐔 إدارة المزارع والدورات الإنتاجية",
        "📊 بورصة الأسعار المركزية",
        "🏭 إدارة المستودعات الذكية",
        "🧾 التسويق وفواتير البيع",
        "🖨️ مصمم الديباجة والدعاية",
        "📈 التحليلات المتقدمة",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]
else:
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]

tabs = st.tabs(tabs_titles)

# ============================================================
# 16. أدلة الاستخدام لكل تبويب (مع خيار صوتي)
# ============================================================
guides = {
    "النمذجة": "في هذا التبويب يمكنك تركيب علفة مثالية بأقل تكلفة باستخدام البروتين المهضوم ومعادل النشاء. اختر الموقع الجغرافي، ثم القطاع الحيواني، وحدد المكونات، ثم اضغط على زر التشغيل. يمكنك أيضاً تحليل خلطة جاهزة في مختبر التحليل.",
    "إدارة المزارع": "نظام متكامل لإدارة مزارع الدجاج اللاحم والبياض مع حفظ دائم للبيانات. يمكنك إنشاء مزارع، وإضافة دورات إنتاجية، وتسجيل بيانات يومية، ومقارنة الأداء مع المعايير القياسية، وتلقي تنبيهات اللقاحات التلقائية. جميع البيانات محفوظة في قاعدة بيانات SQLite وتستمر حتى بعد تغيير الكود.",
    "بورصة الأسعار": "يعرض هذا التبويب أسعار الماشية والمنتجات الحيوانية. يمكن للمالك تحديث الأسعار، وإضافة حيوانات أو منتجات جديدة. يستخدم النظام هذه الأسعار في حساب التكاليف.",
    "المستودعات": "يعرض أرصدة المواد العلفية في المخزن. يمكن للمالك تحديث الكميات، ويراقب النظام المخزون المنخفض وينبهك. تستخدم هذه الأرصدة عند إصدار الفواتير للخصم التلقائي.",
    "الفواتير": "هنا يمكنك إصدار فواتير البيع للعملاء. أدخل اسم العميل والكمية المطلوبة، وسيحسب النظام السعر الإجمالي ويخصم المكونات من المخزون تلقائياً (للمالك فقط).",
    "الديباجة": "يتيح لك تصميم ديباجة جوالات الأعلاف بشكل فني، مع إضافة اسم البراند والصور والشعارات، ثم تصديرها كـ PDF للطباعة.",
    "التحليلات": "يعرض مؤشرات الأداء مثل عدد الخلطات، متوسط التكلفة، ونسبة التوفير. كما يوفر تنبؤات لأسعار المواد الخام ورسوماً بيانية لتوزيع الاستخدام واتجاه الأسعار.",
    "تعليقات المختصين": "قناة لتبادل الخبرات بين المختصين والأطباء البيطريين. يمكن إضافة تعليقات جديدة، وتظهر جميع التعليقات في سجل واحد.",
    "المراجع": "يحتوي على مراجع علمية موثقة في تغذية الحيوان، مع إمكانية البحث في بنك المعرفة السريع عن مصطلحات مثل البروتين المهضوم ومعادل النشاء.",
    "المساعدة": "يجيب على الأسئلة الشائعة ويوفر روابط للدعم الفني. يمكنك طرح سؤالك والحصول على إجابة فورية من بنك المعرفة.",
    "دليل المستخدم": "دليل شامل يشرح كيفية استخدام المنصة خطوة بخطوة، من تسجيل الدخول إلى تركيب العلف وإدارة المزارع والفواتير."
}

# ============================================================
# 17. محتوى كل تبويب (ملخص)
# ============================================================

# ----- التبويب 0: النمذجة والحسابات العلفية -----
with tabs[0]:
    guide_section("النمذجة والحسابات العلفية", guides["النمذجة"])
    st.info("🔬 هذا التبويب يحتوي على محرك الاستمثال الخطي الكامل لتركيب الأعلاف، ومختبر التحليل. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 1: إدارة المزارع والدورات الإنتاجية -----
with tabs[1]:
    guide_section("إدارة المزارع والدورات الإنتاجية", guides["إدارة المزارع"])
    st.info("🐔 هذا التبويب يحتوي على نظام إدارة المزارع المتكامل مع حفظ دائم للبيانات. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 2: بورصة الأسعار المركزية -----
if len(tabs) > 2:
    with tabs[2]:
        guide_section("بورصة الأسعار المركزية", guides["بورصة الأسعار"])
        st.info("📊 هذا التبويب يعرض أسعار الماشية والمنتجات الحيوانية مع إمكانية التحديث. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 3: إدارة المستودعات الذكية -----
if len(tabs) > 3:
    with tabs[3]:
        guide_section("إدارة المستودعات الذكية", guides["المستودعات"])
        st.info("🏭 هذا التبويب يعرض أرصدة المواد العلفية ويتتبع المخزون المنخفض. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 4: التسويق وفواتير البيع -----
if len(tabs) > 4:
    with tabs[4]:
        guide_section("التسويق وفواتير البيع", guides["الفواتير"])
        st.info("🧾 هذا التبويب لإصدار فواتير البيع مع خصم تلقائي من المخزون. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 5: مصمم الديباجة والدعاية -----
if len(tabs) > 5:
    with tabs[5]:
        guide_section("مصمم الديباجة والدعاية", guides["الديباجة"])
        st.info("🖨️ هذا التبويب لتصميم ديباجة جوالات الأعلاف وتصديرها كـ PDF. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 6: التحليلات المتقدمة -----
if len(tabs) > 6:
    with tabs[6]:
        guide_section("التحليلات المتقدمة", guides["التحليلات"])
        st.info("📈 هذا التبويب يعرض مؤشرات الأداء والرسوم البيانية. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 7: تعليقات المختصين -----
if len(tabs) > 7:
    with tabs[7]:
        guide_section("تعليقات المختصين", guides["تعليقات المختصين"])
        st.info("💬 هذا التبويب لتبادل الخبرات بين المختصين. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 8: المراجع العلمية -----
if len(tabs) > 8:
    with tabs[8]:
        guide_section("المراجع العلمية", guides["المراجع"])
        st.info("📚 هذا التبويب يحتوي على مراجع علمية موثقة في تغذية الحيوان. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 9: المساعدة الذكية -----
if len(tabs) > 9:
    with tabs[9]:
        guide_section("المساعدة الذكية", guides["المساعدة"])
        st.info("💡 هذا التبويب يجيب على الأسئلة الشائعة ويوفر روابط للدعم الفني. (الكود الكامل موجود في الملف الأصلي)")

# ----- التبويب 10: دليل المستخدم -----
if len(tabs) > 10:
    with tabs[10]:
        guide_section("دليل المستخدم", guides["دليل المستخدم"])
        st.info("📖 هذا التبويب يحتوي على دليل شامل لاستخدام المنصة. (الكود الكامل موجود في الملف الأصلي)")

# ============================================================
# 18. التذييل والتوقيع
# ============================================================
st.markdown("""
<div class="mini-left-signature">
    🌾 منصة تاور العلمية | الاختصاصي م. عبد القادر إسماعيل تاور
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
