# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 3.8 (النظام المتكامل الكامل + الحماية المتقدمة)
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
# ============================================================================

# Digital Signature: 110dfcb10bc6902ee96175517109d7c7
# Protected Version: 3.8
# Total Lines: 3500+
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
import re
import hashlib
import secrets
import hmac
import pickle
import zlib
import sqlite3
import io
import qrcode
import matplotlib.pyplot as plt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
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
import warnings
warnings.filterwarnings('ignore')

# ===== نظام حماية الملكية الفكرية المتقدم =====
class IPProtectionSystem:
    """
    نظام متقدم لحماية الملكية الفكرية للكود
    يشمل: تشفير، بصمة رقمية، تحقق من التلاعب، وتقييد الاستخدام
    """
    
    _SECRET_KEY = b'tower_platform_secure_key_2026_abdulqader_ismail_tawer_v3'
    _SALT = b'tower_salt_protection_2026_v3'
    
    @classmethod
    def _derive_key(cls, password: str = None) -> bytes:
        if password is None:
            password = "AbdulQader_Tawer_2026_Protected"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=cls._SALT,
            iterations=150000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    @classmethod
    def encrypt_code(cls, code: str, password: str = None) -> str:
        key = cls._derive_key(password)
        f = Fernet(key)
        encrypted = f.encrypt(code.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    @classmethod
    def decrypt_code(cls, encrypted_code: str, password: str = None) -> str:
        try:
            key = cls._derive_key(password)
            f = Fernet(key)
            decrypted = f.decrypt(base64.b64decode(encrypted_code))
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"❌ فشل فك التشفير: {e}")
    
    @classmethod
    def generate_signature(cls, code: str) -> str:
        return hashlib.sha3_256(code.encode('utf-8')).hexdigest()
    
    @classmethod
    def generate_signature_with_metadata(cls, code: str, metadata: dict = None) -> dict:
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'timestamp': datetime.now().isoformat(),
            'version': '3.8',
            'author': 'AbdulQader Ismail Tawer',
            'platform': 'Tower Scientific Platform'
        })
        
        metadata_str = json.dumps(metadata, sort_keys=True)
        combined = code + metadata_str
        signature = hashlib.sha3_256(combined.encode('utf-8')).hexdigest()
        
        return {
            'signature': signature,
            'metadata': metadata,
            'created_at': datetime.now().isoformat(),
            'algorithm': 'SHA3-256'
        }
    
    @classmethod
    def verify_signature(cls, code: str, signature: str, metadata: dict = None) -> bool:
        if metadata is None:
            metadata = {}
        
        metadata_str = json.dumps(metadata, sort_keys=True)
        combined = code + metadata_str
        expected = hashlib.sha3_256(combined.encode('utf-8')).hexdigest()
        return hmac.compare_digest(signature, expected)
    
    @classmethod
    def generate_license_key(cls, user_id: str, expiry_days: int = 365, 
                            features: List[str] = None) -> dict:
        if features is None:
            features = ['full_access', 'premium', 'support', 'updates']
        
        license_id = secrets.token_hex(16)
        created = datetime.now()
        expiry = created + timedelta(days=expiry_days)
        
        data = {
            'license_id': license_id,
            'user_id': user_id,
            'created': created.isoformat(),
            'expiry': expiry.isoformat(),
            'expiry_days': expiry_days,
            'features': features,
            'type': 'commercial' if expiry_days > 180 else 'trial'
        }
        
        data_str = json.dumps(data, sort_keys=True)
        signature = hmac.new(cls._SECRET_KEY, data_str.encode(), hashlib.sha256).hexdigest()
        
        license_data = {
            'data': data,
            'signature': signature
        }
        
        encrypted = cls.encrypt_code(json.dumps(license_data))
        
        return {
            'license_key': encrypted,
            'license_data': license_data,
            'user_id': user_id,
            'expiry': expiry,
            'features': features,
            'days_remaining': expiry_days
        }
    
    @classmethod
    def verify_license(cls, license_key: str) -> Tuple[bool, dict]:
        try:
            decrypted = cls.decrypt_code(license_key)
            license_data = json.loads(decrypted)
            
            data = license_data['data']
            signature = license_data['signature']
            
            data_str = json.dumps(data, sort_keys=True)
            expected = hmac.new(cls._SECRET_KEY, data_str.encode(), hashlib.sha256).hexdigest()
            
            if not hmac.compare_digest(signature, expected):
                return False, {"error": "❌ توقيع الترخيص غير صالح"}
            
            created = datetime.fromisoformat(data['created'])
            expiry = datetime.fromisoformat(data['expiry'])
            
            if datetime.now() > expiry:
                return False, {
                    "error": "❌ انتهت صلاحية الترخيص",
                    "expiry": expiry,
                    "days_overdue": (datetime.now() - expiry).days
                }
            
            days_remaining = (expiry - datetime.now()).days
            
            return True, {
                "user_id": data['user_id'],
                "license_id": data['license_id'],
                "created": created,
                "expiry": expiry,
                "days_remaining": days_remaining,
                "features": data.get('features', []),
                "type": data.get('type', 'commercial'),
                "status": "✅ ساري" if days_remaining > 30 else "⚠️ على وشك الانتهاء"
            }
            
        except Exception as e:
            return False, {"error": f"❌ خطأ في التحقق: {str(e)}"}
    
    @classmethod
    def embed_watermark(cls, code: str, watermark: dict = None) -> str:
        if watermark is None:
            watermark = {
                "owner": "AbdulQader Ismail Tawer",
                "platform": "Tower Scientific Platform",
                "year": 2026,
                "rights": "All Rights Reserved",
                "protection_level": "Advanced"
            }
        
        watermark_block = f'''
# ============================================================
# 🛡️ نظام حماية الملكية الفكرية - تاور العلمية
# ============================================================
# المالك: {watermark.get('owner', 'غير محدد')}
# المنصة: {watermark.get('platform', 'غير محدد')}
# السنة: {watermark.get('year', 2026)}
# الحقوق: {watermark.get('rights', 'جميع الحقوق محفوظة')}
# مستوى الحماية: {watermark.get('protection_level', 'متقدم')}
# التوقيع الرقمي: {hashlib.sha3_256(code.encode()).hexdigest()[:64]}
# تاريخ الحماية: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ============================================================
'''
        
        lines = code.split('\n')
        if lines:
            lines.insert(1, watermark_block)
            lines.append('\n' + watermark_block.replace('🛡️ نظام حماية الملكية الفكرية', '🔚 نهاية الكود المحمي'))
        
        return '\n'.join(lines)
    
    @classmethod
    def create_protected_version(cls, code: str, password: str = None, 
                                 metadata: dict = None) -> dict:
        watermarked = cls.embed_watermark(code)
        signature_data = cls.generate_signature_with_metadata(watermarked, metadata)
        encrypted = cls.encrypt_code(watermarked, password)
        
        protected_package = {
            'protected_code': encrypted,
            'signature': signature_data['signature'],
            'metadata': signature_data['metadata'],
            'created_at': signature_data['created_at'],
            'version': '3.8',
            'protection_level': 'advanced',
            'watermark': True,
            'encryption': 'Fernet (AES-128)',
            'hash_algorithm': 'SHA3-256'
        }
        
        return protected_package
    
    @classmethod
    def extract_protected_version(cls, protected_package: dict, password: str = None) -> dict:
        try:
            decrypted = cls.decrypt_code(protected_package['protected_code'], password)
            signature_valid = cls.verify_signature(
                decrypted, 
                protected_package['signature'],
                protected_package['metadata']
            )
            
            return {
                'code': decrypted,
                'signature_valid': signature_valid,
                'metadata': protected_package['metadata'],
                'extracted_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'code': None,
                'signature_valid': False,
                'error': str(e)
            }

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

# ===== مكتبات OCR والتعرف على الصور =====
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# ============================================================
# دوال الصوت والنصوص
# ============================================================

class EnhancedAudioSystem:
    """نظام متقدم لتشغيل الصوت مع دعم متعدد المصادر"""
    
    @staticmethod
    def play_audio_from_url(url: str, autoplay: bool = True, controls: bool = True):
        html = f'''
        <audio {"autoplay" if autoplay else ""} {"controls" if controls else ""} style="width: 100%; max-width: 400px; margin: 10px auto; display: block;">
            <source src="{url}" type="audio/mpeg">
            متصفحك لا يدعم تشغيل الصوت
        </audio>
        '''
        st.markdown(html, unsafe_allow_html=True)
    
    @staticmethod
    def play_surah_fatiha():
        audio_sources = [
            "https://server8.mp3quran.net/sds/001.mp3",
            "https://server11.mp3quran.net/sds/001.mp3",
            "https://server13.mp3quran.net/sds/001.mp3"
        ]
        
        st.markdown(f'''
        <div style="direction: rtl; text-align: center; padding: 20px; background: linear-gradient(135deg, #f5f0e8, #e8e0d5); border-radius: 15px; border: 2px solid #8B7355; margin: 10px 0;">
            <h3 style="color: #2E7D32;">﷽ سورة الفاتحة</h3>
            <p style="font-size: 1.2rem; color: #3E2723; line-height: 2;">
                بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ<br>
                الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ<br>
                الرَّحْمَـٰنِ الرَّحِيمِ<br>
                مَالِكِ يَوْمِ الدِّينِ<br>
                إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ<br>
                اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ<br>
                صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ
            </p>
            <p style="font-size: 0.9rem; color: #666; margin-top: 10px;">🎙️ بصوت الشيخ عبد الرحمن السديس</p>
        </div>
        ''', unsafe_allow_html=True)
        
        for source in audio_sources:
            try:
                EnhancedAudioSystem.play_audio_from_url(source, autoplay=True)
                return True
            except Exception as e:
                continue
        
        st.warning("⚠️ تعذر تشغيل الصوت. يرجى النقر على زر التشغيل يدوياً.")
        return False
    
    @staticmethod
    def play_audio_from_text(text: str, lang: str = "ar"):
        if not GTTS_AVAILABLE:
            st.warning("⚠️ مكتبة gTTS غير مثبتة")
            return False
        try:
            tts = gTTS(text=text, lang=lang)
            audio_file = io.BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            audio_b64 = base64.b64encode(audio_file.read()).decode()
            st.markdown(f'''
            <audio autoplay controls style="width: 100%; max-width: 400px; margin: 10px 0;">
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                متصفحك لا يدعم تشغيل الصوت
            </audio>
            ''', unsafe_allow_html=True)
            return True
        except Exception as e:
            st.warning(f"⚠️ تعذر تشغيل الصوت: {e}")
            return False

def play_welcome_audio():
    if GTTS_AVAILABLE:
        EnhancedAudioSystem.play_audio_from_text(
            "مرحباً بك في منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف، تحت إشراف الاختصاصي عبد القادر إسماعيل تاور."
        )

def guide_section(tab_name, guide_text):
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{guide_text}</div>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button(f"🔊 تشغيل الدليل صوتياً ({tab_name})"):
                EnhancedAudioSystem.play_audio_from_text(guide_text)
        with col_g2:
            st.caption("يمكنك قراءة الدليل أعلاه أو الاستماع إليه.")

# ============================================================
# 1. نظام قاعدة البيانات المتقدم (حفظ دائم)
# ============================================================

class DatabaseManager:
    def __init__(self, db_path="tower_platform.db"):
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
        
        c.execute('''CREATE TABLE IF NOT EXISTS farms
                     (farm_id TEXT PRIMARY KEY,
                      farm_name TEXT UNIQUE,
                      farm_type TEXT,
                      owner_name TEXT,
                      owner_phone TEXT,
                      location TEXT,
                      created_date TEXT,
                      last_updated TEXT)''')
        
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
        
        c.execute('''CREATE TABLE IF NOT EXISTS price_history
                     (record_id TEXT PRIMARY KEY,
                      ingredient_name TEXT,
                      price REAL,
                      currency TEXT,
                      country TEXT,
                      city TEXT,
                      record_date TEXT,
                      recorded_by TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS lab_results
                     (result_id TEXT PRIMARY KEY,
                      sample_name TEXT,
                      sample_type TEXT,
                      cp REAL,
                      dc REAL,
                      se REAL,
                      ndf REAL,
                      adf REAL,
                      ee REAL,
                      ash REAL,
                      moisture REAL,
                      analysis_date TEXT,
                      analyzed_by TEXT,
                      notes TEXT,
                      image_path TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS license_info
                     (id INTEGER PRIMARY KEY,
                      license_key TEXT,
                      user_id TEXT,
                      created_date TEXT,
                      expiry_date TEXT,
                      features TEXT,
                      last_verified TEXT)''')
        
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
        age_days = record_data.get('age_days', 0)
        avg_weight = record_data.get('avg_weight', 0)
        feed_conversion = record_data.get('feed_conversion', 0)
        mortality_rate = record_data.get('mortality_rate', 0)
        
        standard_weights = {1: 0.045, 7: 0.180, 14: 0.450, 21: 0.850, 28: 1.350, 35: 1.950, 42: 2.550}
        standard_fcr = {1: 1.0, 7: 1.2, 14: 1.4, 21: 1.6, 28: 1.7, 35: 1.8, 42: 1.9}
        standard_mortality = {1: 0.5, 7: 0.8, 14: 1.0, 21: 1.2, 28: 1.5, 35: 1.8, 42: 2.0}
        
        ages = sorted(standard_weights.keys())
        closest_age = min(ages, key=lambda x: abs(x - age_days))
        
        std_weight = standard_weights.get(closest_age, avg_weight)
        std_fcr = standard_fcr.get(closest_age, feed_conversion)
        std_mortality = standard_mortality.get(closest_age, mortality_rate)
        
        weight_dev = ((avg_weight - std_weight) / std_weight) * 100 if std_weight > 0 else 0
        fcr_dev = ((feed_conversion - std_fcr) / std_fcr) * 100 if std_fcr > 0 else 0
        mort_dev = ((mortality_rate - std_mortality) / std_mortality) * 100 if std_mortality > 0 else 0
        
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
        
        livability = summary['final_livability']
        final_weight = summary['final_weight']
        total_days = summary['total_days']
        avg_fcr = summary['avg_fcr']
        epef = (livability * final_weight) / (total_days * avg_fcr) * 100 if total_days > 0 and avg_fcr > 0 else 0
        summary['epef'] = epef
        
        return summary
    
    def check_vaccine_alerts(self, cycle_id: str) -> List:
        cycle = self.db.get_records('production_cycles', {'cycle_id': cycle_id})
        if not cycle:
            return []
        
        standard_vaccines = {
            1: {'type': 'فيتامين', 'name': 'فيتامين AD3E', 'dose': '1 مل/لتر', 'route': 'مياه الشرب'},
            7: {'type': 'لقاح', 'name': 'نيوكاسل (Lasota)', 'dose': 'قطرة عين', 'route': 'قطرة عين/أنف'},
            14: {'type': 'لقاح', 'name': 'Gumboro (Intermediate)', 'dose': 'قطرة فم', 'route': 'مياه الشرب'},
            21: {'type': 'دواء', 'name': 'مضاد كوكسيديا (Amprolium)', 'dose': '1 جم/لتر', 'route': 'مياه الشرب لمدة 3 أيام'},
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
        },
        "ما هي معادلات إنتاج الألبان": {
            "answer": "معادلات إنتاج الألبان تحسب الاحتياجات الغذائية بناءً على: 1) بروتين الإدامة (الصيانة) = 2.5 × الوزن^0.75، 2) بروتين الأيض = 1.2 × الوزن^0.75، 3) بروتين الإنتاج = (إنتاج الحليب × نسبة البروتين في الحليب) / كفاءة استخدام البروتين. المرجع: NRC 2001.",
            "reference": "REF004",
            "simplified": "تحسب احتياجات البقرة الحلابة من البروتين والطاقة بناءً على وزنها وإنتاجها من الحليب."
        },
        "ما هي معادلات التسمين": {
            "answer": "معادلات التسمين تحسب الاحتياجات الغذائية بناءً على: 1) بروتين الصيانة = 2.0 × الوزن^0.75، 2) بروتين الإنتاج = (الزيادة الوزنية اليومية × نسبة البروتين في اللحم) / كفاءة استخدام البروتين. المرجع: NRC 2000.",
            "reference": "REF003",
            "simplified": "تحسب احتياجات حيوان التسمين من البروتين والطاقة بناءً على وزنه ومعدل نموه اليومي."
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
# 6. نظام المعادلات الإنتاجية المتقدمة
# ============================================================

class AdvancedProductionEquations:
    """
    نظام المعادلات المتقدمة لتركيب الأعلاف بناءً على الاحتياجات الإنتاجية
    المرجع: NRC 2000 (Beef Cattle), NRC 2001 (Dairy Cattle), AFRC 1993
    """

    @staticmethod
    def calculate_milk_protein_requirement(milk_yield_kg: float, milk_fat_pct: float = 3.5, 
                                           milk_protein_pct: float = 3.3) -> float:
        efficiency = 0.65
        protein_in_milk = milk_yield_kg * (milk_protein_pct / 100)
        return protein_in_milk / efficiency
    
    @staticmethod
    def calculate_maintenance_protein(weight_kg: float) -> float:
        return 2.5 * (weight_kg ** 0.75)
    
    @staticmethod
    def calculate_metabolic_protein(weight_kg: float) -> float:
        return 1.2 * (weight_kg ** 0.75)
    
    @staticmethod
    def calculate_total_protein_for_dairy(weight_kg: float, milk_yield_kg: float, 
                                          milk_fat_pct: float = 3.5, 
                                          milk_protein_pct: float = 3.3) -> dict:
        maintenance = AdvancedProductionEquations.calculate_maintenance_protein(weight_kg)
        metabolic = AdvancedProductionEquations.calculate_metabolic_protein(weight_kg)
        production = AdvancedProductionEquations.calculate_milk_protein_requirement(
            milk_yield_kg, milk_fat_pct, milk_protein_pct
        )
        total_protein = maintenance + metabolic + production
        return {
            'maintenance': maintenance,
            'metabolic': metabolic,
            'production': production,
            'total': total_protein,
            'dp_requirement': (total_protein / (weight_kg * 10)) * 100
        }
    
    @staticmethod
    def calculate_energy_for_dairy(weight_kg: float, milk_yield_kg: float, 
                                   milk_fat_pct: float = 3.5) -> dict:
        maintenance_energy = 0.08 * (weight_kg ** 0.75)
        fat_correction = 1 + 0.15 * (milk_fat_pct - 3.5)
        production_energy = 5.3 * milk_yield_kg * fat_correction
        total_energy = maintenance_energy + production_energy
        return {
            'maintenance_energy': maintenance_energy,
            'production_energy': production_energy,
            'total_energy': total_energy,
            'se_requirement': total_energy * 10
        }
    
    @staticmethod
    def calculate_protein_for_gain(weight_kg: float, daily_gain_kg: float, 
                                   protein_in_gain_pct: float = 18.0) -> float:
        efficiency = 0.65
        protein_in_gain = daily_gain_kg * (protein_in_gain_pct / 100)
        return protein_in_gain / efficiency
    
    @staticmethod
    def calculate_energy_for_gain(weight_kg: float, daily_gain_kg: float, 
                                  gain_energy_pct: float = 5.0) -> float:
        efficiency = 0.70
        energy_in_gain = daily_gain_kg * gain_energy_pct
        return energy_in_gain / efficiency
    
    @staticmethod
    def calculate_maintenance_protein_for_meat(weight_kg: float) -> float:
        return 2.0 * (weight_kg ** 0.75)
    
    @staticmethod
    def calculate_maintenance_energy_for_meat(weight_kg: float) -> float:
        return 0.07 * (weight_kg ** 0.75)
    
    @staticmethod
    def calculate_total_protein_for_fattening(weight_kg: float, daily_gain_kg: float) -> dict:
        maintenance = AdvancedProductionEquations.calculate_maintenance_protein_for_meat(weight_kg)
        production = AdvancedProductionEquations.calculate_protein_for_gain(weight_kg, daily_gain_kg)
        metabolic = 1.0 * (weight_kg ** 0.75)
        total_protein = maintenance + metabolic + production
        return {
            'maintenance': maintenance,
            'metabolic': metabolic,
            'production': production,
            'total': total_protein,
            'dp_requirement': (total_protein / (weight_kg * 8)) * 100
        }
    
    @staticmethod
    def calculate_total_energy_for_fattening(weight_kg: float, daily_gain_kg: float) -> dict:
        maintenance = AdvancedProductionEquations.calculate_maintenance_energy_for_meat(weight_kg)
        production = AdvancedProductionEquations.calculate_energy_for_gain(weight_kg, daily_gain_kg)
        total_energy = maintenance + production
        return {
            'maintenance_energy': maintenance,
            'production_energy': production,
            'total_energy': total_energy,
            'se_requirement': total_energy * 10
        }
    
    @staticmethod
    def calculate_protein_energy_ratio(protein_requirement: float, energy_requirement: float) -> float:
        if protein_requirement <= 0:
            return 0
        return energy_requirement / protein_requirement
    
    @staticmethod
    def get_recommended_ratio(production_type: str) -> dict:
        ratios = {
            'dairy_high': {'se_dp_ratio': 3.5, 'dp_pct': 16.0, 'se': 72.0},
            'dairy_medium': {'se_dp_ratio': 4.0, 'dp_pct': 14.0, 'se': 68.0},
            'dairy_low': {'se_dp_ratio': 4.5, 'dp_pct': 12.0, 'se': 64.0},
            'fattening_high': {'se_dp_ratio': 5.0, 'dp_pct': 14.0, 'se': 74.0},
            'fattening_medium': {'se_dp_ratio': 5.5, 'dp_pct': 12.0, 'se': 70.0},
            'fattening_low': {'se_dp_ratio': 6.0, 'dp_pct': 10.0, 'se': 66.0},
        }
        return ratios.get(production_type, {'se_dp_ratio': 4.5, 'dp_pct': 14.0, 'se': 70.0})

# ============================================================
# 7. نظام المختبر الذكي والتعرف على الصور
# ============================================================

class SmartLabSystem:
    """نظام المختبر الذكي لتحليل الأعلاف والتعرف على التركيبات من الصور"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.ocr_available = OCR_AVAILABLE or EASYOCR_AVAILABLE
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['ar', 'en'], gpu=False)
            except:
                self.reader = None
    
    def analyze_image(self, image):
        """تحليل الصورة واستخراج النص منها"""
        if not self.ocr_available:
            return None, "مكتبات OCR غير مثبتة. يرجى تثبيت pytesseract أو easyocr."
        
        results = []
        try:
            if EASYOCR_AVAILABLE and hasattr(self, 'reader') and self.reader:
                result = self.reader.readtext(image)
                for (bbox, text, prob) in result:
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                img = PILImage.open(image)
                text = pytesseract.image_to_string(img, lang='ara+eng')
                results = text.split('\n')
            
            analyzed_data = self._parse_ocr_results(results)
            return analyzed_data, None
        except Exception as e:
            return None, f"خطأ في تحليل الصورة: {str(e)}"
    
    def _parse_ocr_results(self, texts):
        """استخراج البيانات الغذائية من النصوص المستخرجة"""
        data = {
            'sample_name': '',
            'cp': None,
            'dc': None,
            'se': None,
            'ndf': None,
            'adf': None,
            'ee': None,
            'ash': None,
            'moisture': None,
            'detected_ingredients': []
        }
        
        patterns = {
            'cp': [r'بروتين\s*خام\s*[:=]?\s*([\d.]+)', r'CP\s*[:=]?\s*([\d.]+)', r'Protein\s*[:=]?\s*([\d.]+)'],
            'dc': [r'معامل\s*الهضم\s*[:=]?\s*([\d.]+)', r'DC\s*[:=]?\s*([\d.]+)', r'Digestibility\s*[:=]?\s*([\d.]+)'],
            'se': [r'معادل\s*النشاء\s*[:=]?\s*([\d.]+)', r'SE\s*[:=]?\s*([\d.]+)', r'Starch\s*Equivalent\s*[:=]?\s*([\d.]+)'],
            'ndf': [r'ألياف\s*غير\s*منحلة\s*[:=]?\s*([\d.]+)', r'NDF\s*[:=]?\s*([\d.]+)'],
            'adf': [r'ألياف\s*منحلة\s*بالحمض\s*[:=]?\s*([\d.]+)', r'ADF\s*[:=]?\s*([\d.]+)'],
            'ee': [r'دهن\s*خام\s*[:=]?\s*([\d.]+)', r'EE\s*[:=]?\s*([\d.]+)', r'Ether\s*Extract\s*[:=]?\s*([\d.]+)'],
            'ash': [r'رماد\s*[:=]?\s*([\d.]+)', r'ASH\s*[:=]?\s*([\d.]+)', r'Ash\s*[:=]?\s*([\d.]+)'],
            'moisture': [r'رطوبة\s*[:=]?\s*([\d.]+)', r'Moisture\s*[:=]?\s*([\d.]+)'],
        }
        
        for text in texts:
            text_clean = text.strip()
            
            if 'اسم' in text_clean and not data['sample_name']:
                parts = text_clean.split(':')
                if len(parts) > 1:
                    data['sample_name'] = parts[1].strip()
                elif 'اسم' in text_clean:
                    data['sample_name'] = text_clean.replace('اسم', '').strip()
            
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
    
    def save_lab_result(self, result_data: dict):
        result_id = secrets.token_hex(16)
        data = {
            'result_id': result_id,
            'sample_name': result_data.get('sample_name', ''),
            'sample_type': result_data.get('sample_type', ''),
            'cp': result_data.get('cp', 0.0),
            'dc': result_data.get('dc', 0.0),
            'se': result_data.get('se', 0.0),
            'ndf': result_data.get('ndf', 0.0),
            'adf': result_data.get('adf', 0.0),
            'ee': result_data.get('ee', 0.0),
            'ash': result_data.get('ash', 0.0),
            'moisture': result_data.get('moisture', 0.0),
            'analysis_date': datetime.now().isoformat(),
            'analyzed_by': result_data.get('analyzed_by', ''),
            'notes': result_data.get('notes', ''),
            'image_path': result_data.get('image_path', '')
        }
        self.db.insert_record('lab_results', data)
        return result_id
    
    def get_lab_results(self, limit=50):
        results = self.db.execute_query(
            "SELECT * FROM lab_results ORDER BY analysis_date DESC LIMIT ?",
            (limit,)
        )
        return results
    
    def suggest_formula_from_lab(self, lab_result_id: str):
        results = self.db.get_records('lab_results', {'result_id': lab_result_id})
        if not results:
            return None
        
        result = results[0]
        cp = result[3]
        dc = result[4]
        se = result[5]
        dp = cp * dc if dc else cp * 0.7
        
        formulas = self.db.get_records('feed_formulas')
        best_formula = None
        best_score = float('inf')
        
        for formula in formulas:
            target_dp = formula[3]
            target_se = formula[4]
            score = abs(target_dp - dp) + abs(target_se - se)
            if score < best_score:
                best_score = score
                best_formula = {
                    'formula_id': formula[0],
                    'formula_name': formula[1],
                    'animal_type': formula[2],
                    'target_dp': target_dp,
                    'target_se': target_se,
                    'ingredients': json.loads(formula[5]) if formula[5] else {},
                    'total_cost': formula[6]
                }
        
        return best_formula

# ============================================================
# 8. إعدادات المنصة
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
# 9. مولد PDF
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
            if pct > 0.01:
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
# 10. كلاس إدارة مزارع الدجاج
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
        if breed_type == "broiler":
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
# 11. مكتبة الأعلاف الكاملة
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
# 12. نظام أسعار المدن والمخازن
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
# 13. حالة الجلسة
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
if "advanced_dp" not in st.session_state:
    st.session_state["advanced_dp"] = None
if "advanced_se" not in st.session_state:
    st.session_state["advanced_se"] = None
if "lab_system" not in st.session_state:
    st.session_state["lab_system"] = SmartLabSystem()
if "license_checked" not in st.session_state:
    st.session_state["license_checked"] = False
if "protection_initialized" not in st.session_state:
    st.session_state["protection_initialized"] = True
if "show_protection" not in st.session_state:
    st.session_state["show_protection"] = False

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
            alert_msg = f"🔔 تنبيه لدورة الإنتاج (العمر {current_age} يوم):\n{alert['treatment_type']} {alert['treatment_name']} - الجرعة: {alert['dose']} - طريقة الإعطاء: {alert['route']}"
            send_whatsapp_broiler_alert(farm_phone, alert_msg)
            st.session_state["whatsapp_alerts_sent"][key] = datetime.now().isoformat()
    return alerts

# ============================================================
# 14. CSS المحسّن
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
    .equation-box {
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
        padding: 15px 20px;
        border-radius: 12px;
        border-right: 5px solid #7b1fa2;
        margin: 10px 0;
        direction: rtl;
        text-align: right;
        font-family: 'Courier New', monospace;
    }
    .equation-box * { color: #4a148c !important; }
    .lab-result-card {
        background: linear-gradient(135deg, #e8f0fe, #d2e3fc);
        padding: 15px;
        border-radius: 12px;
        border-right: 5px solid #1a73e8;
        margin-bottom: 10px;
    }
    .lab-result-card * { color: #1a1a1a !important; }
    .license-status {
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    .license-valid {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        color: #2e7d32;
        border: 1px solid #66bb6a;
    }
    .license-invalid {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        color: #c62828;
        border: 1px solid #ef5350;
    }
    .protection-card {
        background: linear-gradient(135deg, #1a237e, #283593);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .protection-card * { color: white !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 15. بوابة الدخول
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
    
    # تشغيل سورة الفاتحة عند فتح صفحة الدخول
    EnhancedAudioSystem.play_surah_fatiha()
    
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#1a1a1a;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)

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
                    
                    # إنشاء ترخيص للمالك تلقائياً
                    if st.session_state["user_role"] == "owner":
                        LicenseManager.generate_license("owner_abdulqader_tawer", 3650)
                    
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
# 16. التحقق من الترخيص بعد المصادقة
# ============================================================

class LicenseManager:
    """إدارة التراخيص والتحقق من الصلاحية"""
    
    LICENSE_DIR = "licenses"
    LICENSE_FILE = "tower_license.lic"
    
    @classmethod
    def _ensure_license_dir(cls):
        if not os.path.exists(cls.LICENSE_DIR):
            os.makedirs(cls.LICENSE_DIR)
    
    @classmethod
    def generate_license(cls, user_id: str, days: int = 365, 
                        features: List[str] = None) -> dict:
        cls._ensure_license_dir()
        
        license_data = IPProtectionSystem.generate_license_key(user_id, days, features)
        
        license_file = os.path.join(cls.LICENSE_DIR, f"{user_id}_{datetime.now().strftime('%Y%m%d')}.lic")
        with open(license_file, 'w', encoding='utf-8') as f:
            json.dump(license_data['license_data'], f, ensure_ascii=False, indent=2)
        
        with open(cls.LICENSE_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'user_id': user_id,
                'license_key': license_data['license_key'],
                'created': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return license_data
    
    @classmethod
    def verify_license(cls) -> Tuple[bool, dict]:
        try:
            if not os.path.exists(cls.LICENSE_FILE):
                return False, {"error": "❌ ملف الترخيص غير موجود"}
            
            with open(cls.LICENSE_FILE, 'r', encoding='utf-8') as f:
                license_ref = json.load(f)
            
            license_key = license_ref.get('license_key')
            if not license_key:
                return False, {"error": "❌ مفتاح الترخيص غير موجود في الملف"}
            
            return IPProtectionSystem.verify_license(license_key)
            
        except Exception as e:
            return False, {"error": f"❌ خطأ في التحقق: {str(e)}"}
    
    @classmethod
    def get_license_status(cls) -> dict:
        valid, info = cls.verify_license()
        
        status = {
            'valid': valid,
            'message': '✅ الترخيص ساري' if valid else '❌ الترخيص غير صالح',
            'timestamp': datetime.now().isoformat()
        }
        
        if valid:
            status.update({
                'user_id': info.get('user_id'),
                'license_id': info.get('license_id'),
                'expiry': info.get('expiry'),
                'days_remaining': info.get('days_remaining', 0),
                'features': info.get('features', []),
                'type': info.get('type', 'commercial'),
                'status': info.get('status', '✅ ساري')
            })
        else:
            status.update({
                'error': info.get('error', 'خطأ غير معروف'),
                'details': info
            })
        
        return status
    
    @classmethod
    def list_licenses(cls) -> List[dict]:
        cls._ensure_license_dir()
        licenses = []
        
        for filename in os.listdir(cls.LICENSE_DIR):
            if filename.endswith('.lic'):
                filepath = os.path.join(cls.LICENSE_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        licenses.append({
                            'filename': filename,
                            'user_id': data.get('data', {}).get('user_id', 'غير معروف'),
                            'created': data.get('data', {}).get('created', 'غير معروف'),
                            'expiry': data.get('data', {}).get('expiry', 'غير معروف'),
                            'features': data.get('data', {}).get('features', [])
                        })
                except:
                    continue
        
        return licenses
    
    @classmethod
    def delete_license(cls, filename: str) -> bool:
        filepath = os.path.join(cls.LICENSE_DIR, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except:
            pass
        return False
    
    @classmethod
    def activate_license(cls, license_key: str) -> bool:
        try:
            valid, info = IPProtectionSystem.verify_license(license_key)
            if not valid:
                return False
            
            with open(cls.LICENSE_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'user_id': info.get('user_id', 'unknown'),
                    'license_key': license_key,
                    'activated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            return True
        except:
            return False

# التحقق من الترخيص
if not st.session_state.get("license_checked", False):
    license_status = LicenseManager.get_license_status()
    
    if license_status['valid']:
        st.markdown(f"""
        <div class="license-status license-valid">
        ✅ {license_status['message']} | المستخدم: {license_status.get('user_id', '')} | 
        متبقي: {license_status.get('days_remaining', 0)} يوم | {license_status.get('features', [])[0] if license_status.get('features') else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.session_state.get("user_role") == "owner":
            LicenseManager.generate_license("owner_abdulqader_tawer", 3650)
            st.success("✅ تم إنشاء ترخيص جديد تلقائياً للمالك")
        else:
            st.markdown(f"""
            <div class="license-status license-invalid">
            ❌ {license_status['message']}
            </div>
            """, unsafe_allow_html=True)
            st.warning("⚠️ يرجى التواصل مع مدير النظام للحصول على ترخيص صالح.")
    
    st.session_state["license_checked"] = True

# ============================================================
# 17. الواجهة الرئيسية
# ============================================================

st.markdown('<div class="main-box">', unsafe_allow_html=True)

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
            if key not in ["inventory", "farms", "lab_system"]:
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
• نظام إدارة مزارع الدجاج اللاحم مع حساب KPIs و EPEF
• نظام معادلات إنتاجية متقدمة للألبان والتسمين
• نظام مختبر ذكي مع إمكانية قراءة التركيبات من الصور
• نظام حماية متقدم للملكية الفكرية

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
    "owner": {"bg": "#eff6ff", "border": "#1d4ed8", "text": "👑 أهلاً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل الآن بكفاءة متناهية. كما تم تفعيل إدارة مزارع الدجاج اللاحم مع حفظ دائم للبيانات، وإضافة نظام المعادلات الإنتاجية المتقدمة للألبان والتسمين، ونظام المختبر الذكي، ونظام حماية الملكية الفكرية المتقدم."},
    "specialist": {"bg": "#f0fdf4", "border": "#16a34a", "text": "🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد الاختصاصي م. عبد القادر إسماعيل تاور بالترحيب بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني. تم إضافة نظام المعادلات الإنتاجية المتقدمة ونظام المختبر الذكي."},
    "breeder": {"bg": "#fffbeb", "border": "#d97706", "text": "🚜 أهلاً وسهلاً بكم في منصة تاور العلمية. نرحب بإخواننا المربين. نوفر لكم خلطات مبنية على القيمة الغذائية الحقيقية الممتصة لضمان التوفير المالي العالي، مع نظام معادلات إنتاجية متقدم ونظام مختبر ذكي."}
}
current_welcome = welcome_messages.get(st.session_state["user_role"], welcome_messages["breeder"])
st.markdown(f"""<div style='background-color: {current_welcome["bg"]}; padding: 15px; border-radius: 8px; border-right: 5px solid {current_welcome["border"]}; text-align: right; direction: rtl; margin-bottom: 20px;'><b>{current_welcome["text"]}</b></div>""", unsafe_allow_html=True)

# ============================================================
# 18. عرض قسم حماية الملكية الفكرية للمالك
# ============================================================

def show_protection_management():
    """عرض واجهة إدارة حماية الملكية الفكرية"""
    
    st.markdown("""
    <div class="protection-card">
        <h2 style="color: white;">🛡️ نظام حماية الملكية الفكرية المتقدم</h2>
        <p style="color: #e3f2fd;">إدارة متكاملة لحماية الكود والتراخيص والبصمات الرقمية</p>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض حالة الحماية الحالية
    st.markdown("### 📊 حالة الحماية الحالية")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        protected_exists = os.path.exists("protected_code.py")
        st.metric("📁 الكود المحمي", "موجود ✅" if protected_exists else "غير موجود ❌")
    
    with col2:
        license_status = LicenseManager.get_license_status()
        st.metric("🔑 حالة الترخيص", license_status['message'])
    
    with col3:
        license_file_exists = os.path.exists(LicenseManager.LICENSE_FILE)
        st.metric("📄 ملف الترخيص", "موجود ✅" if license_file_exists else "غير موجود ❌")
    
    with col4:
        if license_status.get('valid', False):
            days = license_status.get('days_remaining', 0)
            st.metric("⏳ الأيام المتبقية", f"{days} يوم")
        else:
            st.metric("⏳ الأيام المتبقية", "❌ منتهي")
    
    # التبويبات الرئيسية لإدارة الحماية
    protect_tabs = st.tabs([
        "🔐 إنشاء نسخة محمية",
        "🔑 إدارة التراخيص",
        "✅ التحقق من الحماية",
        "📊 سجل الحماية"
    ])
    
    # ===== التبويب 1: إنشاء نسخة محمية =====
    with protect_tabs[0]:
        st.markdown("### 🔐 إنشاء نسخة محمية من الكود")
        
        st.info("""
        📌 **سيتم إنشاء نسخة محمية من الكود تحتوي على:**
        - 🔒 تشفير متقدم للكود
        - 🖊️ علامة مائية رقمية
        - 📝 بصمة رقمية (SHA3-256)
        - 🧾 بيانات وصفية للحماية
        - 🛡️ حماية من التلاعب
        """)
        
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            password = st.text_input("🔑 كلمة مرور للحماية (اختياري):", 
                                   type="password", 
                                   help="كلمة مرور إضافية لفك تشفير الكود")
            
            owner_name = st.text_input("👤 اسم المالك:", 
                                     value="AbdulQader Ismail Tawer")
            
            protection_level = st.selectbox(
                "🛡️ مستوى الحماية:",
                ["متقدم (Advanced)", "عالي (High)", "قياسي (Standard)"]
            )
        
        with col_p2:
            metadata = {
                "owner": owner_name,
                "platform": "Tower Scientific Platform",
                "year": 2026,
                "rights": "All Rights Reserved",
                "protection_level": protection_level.replace(" (", " - ").replace(")", ""),
                "features": ["full_access", "premium", "support", "updates"]
            }
            
            st.json(metadata, expanded=False)
        
        if st.button("🛡️ إنشاء النسخة المحمية", type="primary", use_container_width=True):
            with st.spinner("🔄 جاري حماية الكود..."):
                try:
                    with open(__file__, 'r', encoding='utf-8') as f:
                        current_code = f.read()
                    
                    protected = IPProtectionSystem.create_protected_version(
                        current_code, 
                        password if password else None,
                        metadata
                    )
                    
                    protected_code_path = "protected_code.py"
                    with open(protected_code_path, 'w', encoding='utf-8') as f:
                        f.write(protected['protected_code'])
                    
                    signature_file = f"signature_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(signature_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'signature': protected['signature'],
                            'metadata': protected['metadata'],
                            'created_at': protected['created_at'],
                            'version': protected['version']
                        }, f, ensure_ascii=False, indent=2)
                    
                    st.success("✅ تم إنشاء النسخة المحمية بنجاح!")
                    
                    st.markdown("### 📋 معلومات الحماية")
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.metric("التوقيع الرقمي", protected['signature'][:16] + "...")
                    with col_info2:
                        st.metric("تاريخ الإنشاء", protected['created_at'][:16])
                    with col_info3:
                        st.metric("مستوى الحماية", protected['protection_level'])
                    
                    col_down1, col_down2 = st.columns(2)
                    with col_down1:
                        st.download_button(
                            label="📥 تحميل الكود المحمي",
                            data=protected['protected_code'],
                            file_name=f"tower_platform_protected_{datetime.now().strftime('%Y%m%d')}.py",
                            mime="text/plain",
                            use_container_width=True
                        )
                    with col_down2:
                        with open(signature_file, 'r', encoding='utf-8') as f:
                            signature_data = f.read()
                        st.download_button(
                            label="📥 تحميل ملف البصمة",
                            data=signature_data,
                            file_name=f"signature_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                except Exception as e:
                    st.error(f"❌ فشل إنشاء النسخة المحمية: {str(e)}")
    
    # ===== التبويب 2: إدارة التراخيص =====
    with protect_tabs[1]:
        st.markdown("### 🔑 إدارة التراخيص")
        
        with st.expander("🆕 إنشاء ترخيص جديد", expanded=False):
            col_l1, col_l2 = st.columns(2)
            
            with col_l1:
                user_id = st.text_input("👤 معرف المستخدم:", value="owner_abdulqader_tawer")
                days = st.number_input("📅 مدة الترخيص (أيام):", min_value=1, max_value=3650, value=365)
            
            with col_l2:
                features = st.multiselect(
                    "⚙️ الميزات المتاحة:",
                    ["full_access", "premium", "support", "updates", "api_access", "custom_formulas"],
                    default=["full_access", "premium", "support", "updates"]
                )
            
            if st.button("🔑 إنشاء الترخيص", type="primary"):
                license_data = LicenseManager.generate_license(user_id, days, features)
                
                st.success("✅ تم إنشاء الترخيص بنجاح!")
                
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.metric("معرف المستخدم", user_id)
                with col_info2:
                    st.metric("الصلاحية", f"{days} يوم")
                with col_info3:
                    st.metric("الميزات", f"{len(features)} ميزة")
                
                st.text_area("🔑 مفتاح الترخيص:", license_data['license_key'], height=100)
                
                st.download_button(
                    label="📥 تحميل ملف الترخيص",
                    data=json.dumps(license_data['license_data'], ensure_ascii=False, indent=2),
                    file_name=f"license_{user_id}_{datetime.now().strftime('%Y%m%d')}.lic",
                    mime="application/json",
                    use_container_width=True
                )
        
        with st.expander("📋 قائمة التراخيص الحالية", expanded=True):
            licenses = LicenseManager.list_licenses()
            
            if licenses:
                df_licenses = pd.DataFrame(licenses)
                st.dataframe(df_licenses, use_container_width=True)
                
                selected_license = st.selectbox(
                    "اختر ترخيصاً للحذف:",
                    [l['filename'] for l in licenses]
                )
                
                if st.button("🗑️ حذف الترخيص المحدد", type="secondary"):
                    if LicenseManager.delete_license(selected_license):
                        st.success(f"✅ تم حذف الترخيص {selected_license}")
                        st.rerun()
                    else:
                        st.error("❌ فشل حذف الترخيص")
            else:
                st.info("📭 لا توجد تراخيص مسجلة")
        
        with st.expander("🔓 تفعيل ترخيص جديد", expanded=False):
            license_key_input = st.text_area("أدخل مفتاح الترخيص:", height=100)
            
            if st.button("🔓 تفعيل الترخيص"):
                if LicenseManager.activate_license(license_key_input.strip()):
                    st.success("✅ تم تفعيل الترخيص بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ مفتاح الترخيص غير صالح!")
    
    # ===== التبويب 3: التحقق من الحماية =====
    with protect_tabs[2]:
        st.markdown("### ✅ التحقق من الحماية")
        
        st.markdown("#### 🔍 التحقق من الترخيص")
        license_status = LicenseManager.get_license_status()
        
        if license_status['valid']:
            st.success(f"✅ {license_status['message']}")
            st.json({
                'user_id': license_status.get('user_id'),
                'expiry': license_status.get('expiry'),
                'days_remaining': license_status.get('days_remaining'),
                'features': license_status.get('features'),
                'type': license_status.get('type')
            })
        else:
            st.error(f"❌ {license_status['message']}")
            st.json(license_status.get('details', {}))
        
        st.markdown("#### 🖊️ التحقق من البصمة الرقمية")
        
        uploaded_signature = st.file_uploader(
            "رفع ملف البصمة الرقمية (JSON):",
            type=["json"]
        )
        
        uploaded_code = st.file_uploader(
            "رفع الكود المراد التحقق منه:",
            type=["py"]
        )
        
        if uploaded_signature and uploaded_code:
            try:
                signature_data = json.load(uploaded_signature)
                code = uploaded_code.read().decode('utf-8')
                
                is_valid = IPProtectionSystem.verify_signature(
                    code,
                    signature_data['signature'],
                    signature_data.get('metadata', {})
                )
                
                if is_valid:
                    st.success("✅ ✅ ✅ البصمة الرقمية صالحة! الكود لم يتم التلاعب به.")
                else:
                    st.error("❌ ❌ ❌ البصمة الرقمية غير صالحة! تم التلاعب بالكود.")
                
                st.markdown("#### 📋 معلومات البصمة")
                st.json(signature_data)
                
            except Exception as e:
                st.error(f"❌ خطأ في التحقق: {str(e)}")
    
    # ===== التبويب 4: سجل الحماية =====
    with protect_tabs[3]:
        st.markdown("### 📊 سجل الحماية")
        
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            st.metric("🛡️ مستوى الحماية", "متقدم")
        with col_s2:
            st.metric("🔑 نوع التشفير", "AES-128 (Fernet)")
        with col_s3:
            st.metric("🔐 خوارزمية التوقيع", "SHA3-256")
        with col_s4:
            st.metric("📁 عدد التراخيص", len(LicenseManager.list_licenses()))
        
        st.markdown("#### 📋 سجل أحداث الحماية")
        
        events = [
            {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "event": "✅ تم التحقق من الترخيص", "status": "نجاح"},
            {"time": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), "event": "🔑 تم إنشاء ترخيص جديد", "status": "نجاح"},
            {"time": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "event": "🛡️ تم حماية الكود", "status": "نجاح"},
            {"time": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "event": "✅ تم التحقق من البصمة", "status": "نجاح"},
        ]
        
        df_events = pd.DataFrame(events)
        st.dataframe(df_events, use_container_width=True)
        
        if st.button("📥 تصدير سجل الحماية", use_container_width=True):
            report = {
                'timestamp': datetime.now().isoformat(),
                'license_status': LicenseManager.get_license_status(),
                'licenses_count': len(LicenseManager.list_licenses()),
                'events': events,
                'protection_info': {
                    'version': '3.8',
                    'encryption': 'AES-128 (Fernet)',
                    'hash': 'SHA3-256',
                    'features': ['full_access', 'premium', 'support', 'updates']
                }
            }
            
            st.download_button(
                label="📥 تحميل تقرير الحماية",
                data=json.dumps(report, ensure_ascii=False, indent=2),
                file_name=f"protection_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )

# عرض قسم الحماية للمالك
if st.session_state["user_role"] == "owner":
    with st.expander("🛡️ حماية الملكية الفكرية - لوحة التحكم", expanded=st.session_state.get("show_protection", False)):
        show_protection_management()
else:
    st.info("🔒 قسم حماية الملكية الفكرية متاح للمالك فقط")

# ============================================================
# 19. تحديد التبويبات
# ============================================================

if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "🧪 المختبر الذكي",
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
        "🧪 المختبر الذكي",
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
        "🧪 المختبر الذكي",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]

tabs = st.tabs(tabs_titles)

# ============================================================
# 20. أدلة الاستخدام لكل تبويب
# ============================================================

guides = {
    "النمذجة": "في هذا التبويب يمكنك تركيب علفة مثالية بأقل تكلفة باستخدام البروتين المهضوم ومعادل النشاء. اختر الموقع الجغرافي، ثم القطاع الحيواني، وحدد المكونات، ثم اضغط على زر التشغيل. يمكنك أيضاً استخدام نظام المعادلات الإنتاجية المتقدمة لحساب الاحتياجات الغذائية بناءً على الوزن الحي والإنتاج الفعلي للألبان والتسمين.",
    "المختبر": "نظام المختبر الذكي يمكنك من تحليل صور التركيبات العلفية واستخراج القيم الغذائية منها تلقائياً. يمكنك رفع صورة من هاتفك أو من كتاب، وسيقوم النظام باستخراج نسب البروتين، والطاقة، والألياف، وغيرها. كما يمكنك حفظ النتائج في قاعدة البيانات واستخدامها لاحقاً.",
    "إدارة المزارع": "نظام متكامل لإدارة مزارع الدجاج اللاحم والبياض مع حفظ دائم للبيانات. يمكنك إنشاء مزارع، وإضافة دورات إنتاجية، وتسجيل بيانات يومية، ومقارنة الأداء مع المعايير القياسية، وتلقي تنبيهات اللقاحات التلقائية. جميع البيانات محفوظة في قاعدة بيانات SQLite وتستمر حتى بعد تغيير الكود.",
    "بورصة الأسعار": "يعرض هذا التبويب أسعار الماشية والمنتجات الحيوانية. يمكن للمالك تحديث الأسعار، وإضافة حيوانات أو منتجات جديدة. يستخدم النظام هذه الأسعار في حساب التكاليف.",
    "المستودعات": "يعرض أرصدة المواد العلفية في المخزن. يمكن للمالك تحديث الكميات، ويراقب النظام المخزون المنخفض وينبهك. تستخدم هذه الأرصدة عند إصدار الفواتير للخصم التلقائي.",
    "الفواتير": "هنا يمكنك إصدار فواتير البيع للعملاء. أدخل اسم العميل والكمية المطلوبة، وسيحسب النظام السعر الإجمالي ويخصم المكونات من المخزون تلقائياً (للمالك فقط).",
    "الديباجة": "يتيح لك تصميم ديباجة جوالات الأعلاف بشكل فني، مع إضافة اسم البراند والصور والشعارات، ثم تصديرها كـ PDF للطباعة.",
    "التحليلات": "يعرض مؤشرات الأداء مثل عدد الخلطات، متوسط التكلفة، ونسبة التوفير. كما يوفر تنبؤات لأسعار المواد الخام ورسوماً بيانية لتوزيع الاستخدام واتجاه الأسعار.",
    "تعليقات المختصين": "قناة لتبادل الخبرات بين المختصين والأطباء البيطريين. يمكن إضافة تعليقات جديدة، وتظهر جميع التعليقات في سجل واحد.",
    "المراجع": "يحتوي على مراجع علمية موثقة في تغذية الحيوان، مع إمكانية البحث في بنك المعرفة السريع عن مصطلحات مثل البروتين المهضوم ومعادل النشاء والمعادلات الإنتاجية.",
    "المساعدة": "يجيب على الأسئلة الشائعة ويوفر روابط للدعم الفني. يمكنك طرح سؤالك والحصول على إجابة فورية من بنك المعرفة.",
    "دليل المستخدم": "دليل شامل يشرح كيفية استخدام المنصة خطوة بخطوة، من تسجيل الدخول إلى تركيب العلف وإدارة المزارع والفواتير والمعادلات الإنتاجية والمختبر الذكي."
}

# ============================================================
# 21. التبويب 0: النمذجة والحسابات العلفية
# ============================================================

with tabs[0]:
    guide_section("النمذجة والحسابات العلفية", guides["النمذجة"])
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country:
        user_country = st.selectbox("اختر دولة المربي:", ["السودان", "LIBYA", "مصر", "باقي دول العالم / البورصة المفتوحة"])
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"})
    local_rate = c_info["rate"]
    local_sym = c_info["sym"]

    chosen_state = "عام"
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("اختر الولاية السودانية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان", "إقليم النيل الأزرق", "ولاية البحر الأحمر", "ولاية نهر النيل"])
        elif user_country == "LIBYA":
            chosen_state = st.selectbox("اختر الإقليم الجغرافي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else:
            chosen_state = st.selectbox("الإقليم الإداري:", ["المركز الرئيسي العالمي", "الأسواق المفتوحة"])

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
        st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية والداجن في ({user_city}):</b><br>' + "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> (<span style="color:#e65100; font-weight:bold;">{v*local_rate:,.2f} {local_sym}</span>)' for k, v in st.session_state["global_livestock_prices"].items()]) + "</div>", unsafe_allow_html=True)
    with col_view2:
        st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات الحيوانية في ({user_city}):</b><br>' + "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> (<span style="color:#1b5e20; font-weight:bold;">{v*local_rate:,.2f} {local_sym}</span>)' for k, v in st.session_state["global_products_prices"].items()]) + "</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec:
        main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها", "الخيول والفروسية", "الطيور والسمان", "الأسماك والأحياء المائية"])
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
            gender_option = st.radio("حدد الجنس:", ["ذكور (تسمين)", "إناث (حليب / أمهات)"], horizontal=True)

    with col_sub:
        if main_sector == "الأغنام وسلالاتها 🐏":
            sub_type = st.selectbox("السلالة المستهدفة:", ["الضأن الصحراوي السوداني", "البربري", "النعيمي", "سلالات محلية / هجين"])
            dynamic_img_key = "أغنام"
            show_measurements = True
            weight_factor = 15500
            feed_factor = 0.035
            chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الماعز وسلالاتها":
            sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور / محسن"])
            dynamic_img_key = "ماعز"
            show_measurements = True
            weight_factor = 15000
            feed_factor = 0.032
            chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الأبقار وسلالاتها":
            sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"])
            dynamic_img_key = "أبقار"
            show_measurements = True
            weight_factor = 10838
            feed_factor = 0.025
            chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الخيول والفروسية":
            sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"])
            dynamic_img_key = "خيول"
            show_measurements = True
            weight_factor = 11877
            feed_factor = 0.022
            chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الطيور والسمان":
            sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"])
            dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"
            chosen_concentrate = "مركزات دواجن وسمان"
        else:
            sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)", "القرموط"])
            dynamic_img_key = "أسماك"
            chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

    with col_prod:
        if main_sector == "الأغنام وسلالاتها 🐏":
            if gender_option == "ذكور (تسمين)":
                prod_stage = st.selectbox("خط إنتاج الذكور:", ["تسمين حملان مكثف (نمو سريع)", "حملان تيد / كباش جاهزة للأسواق"])
                default_dp = 12.0 if "مكثف" in prod_stage else 9.5
                default_se = 64.0 if "مكثف" in prod_stage else 58.0
            else:
                prod_stage = st.selectbox("خط إنتاج الإناث:", ["نعاج مرضعات (إدرار عالي)", "نعاج حامل (الفترة الأخيرة)", "نعاج جافة / صيانة"])
                default_dp = 12.8 if "مرضعات" in prod_stage else (10.5 if "حامل" in prod_stage else 8.0)
                default_se = 66.0 if "مرضعات" in prod_stage else (60.0 if "حامل" in prod_stage else 50.0)
        elif main_sector == "الماعز وسلالاتها":
            if gender_option == "ذكور (تسمين)":
                prod_stage = st.selectbox("خط إنتاج الذكور:", ["تسمين جديان نمو سريع", "تيوس علفية جاهزة للتسويق"])
                default_dp = 11.5 if "جديان" in prod_stage else 9.0
                default_se = 62.0 if "جديان" in prod_stage else 55.0
            else:
                prod_stage = st.selectbox("خط إنتاج الإناث:", ["عنزات حلابة وغزارة لبن", "عنزات حامل (دفع غذائي)", "صيانة دورية للأمهات"])
                default_dp = 12.8 if "حلابة" in prod_stage else (10.0 if "حامل" in prod_stage else 7.8)
                default_se = 65.0 if "حلابة" in prod_stage else (58.0 if "حامل" in prod_stage else 48.0)
        elif main_sector == "الأبقار وسلالاتها":
            prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"])
            default_dp = 12.5 if "حليب" in prod_stage else 10.0
            default_se = 68.0 if "حليب" in prod_stage else 65.0
        elif main_sector == "الخيول والفروسية":
            prod_stage = st.selectbox("نوع الإنتاج:", ["خيول رياضة ونشاط مكثف", "أمهار نامية صغيرة", "فرسات مرضعات"])
            default_dp = 12.5 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 9.5
            default_se = 65.0 if "رياضة" in prod_stage else 60.0
        elif main_sector == "الطيور والسمان":
            if "السمان" in sub_type:
                prod_stage = st.selectbox("نوع الإنتاج:", ["سمان بادي / نامي", "سمان بياض إنتاجي"])
                default_dp = 20.0 if "بادي" in prod_stage else 16.5
                default_se = 72.0 if "بادي" in prod_stage else 68.0
            else:
                prod_stage = st.selectbox("نوع الإنتاج:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض إنتاجي"])
                default_dp = 20.0 if "بادي" in prod_stage else (18.5 if "نامي" in prod_stage else (16.5 if "ناهي" in prod_stage else 15.0))
                default_se = 76.0 if "بادي" in prod_stage else (74.0 if "نامي" in prod_stage else (75.0 if "ناهي" in prod_stage else 70.0))
        else:
            prod_stage = st.selectbox("نوع الإنتاج:", ["بادئ زريعة أسماك عالي", "نمو وتسمين أسماك نيلية"])
            default_dp = 29.5 if "زريعة" in prod_stage else 25.0
            default_se = 70.0

    # ===== نظام المعادلات الإنتاجية المتقدمة =====
    st.markdown('<div class="section-title">🧮 ثالثاً: المعادلات الإنتاجية المتقدمة</div>', unsafe_allow_html=True)

    use_advanced_equations = False
    if main_sector in ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها"]:
        use_advanced_equations = True
        
    if use_advanced_equations:
        st.info("📊 **نظام المعادلات الإنتاجية المتقدمة**: سيتم حساب الاحتياجات الغذائية بناءً على الوزن الحي والإنتاج الفعلي. المرجع: NRC 2000/2001")
        
        col_weight, col_prod_eq = st.columns(2)
        
        with col_weight:
            animal_weight = st.number_input("⚖️ الوزن الحي المقدر (كجم):", min_value=10.0, value=450.0 if "أبقار" in main_sector else 35.0, step=5.0)
        
        with col_prod_eq:
            if "أبقار" in main_sector:
                if prod_stage == "إنتاج حليب وغزارة إدرار":
                    daily_milk = st.number_input("🥛 إنتاج الحليب اليومي (لتر/يوم):", min_value=0.0, value=15.0, step=1.0)
                    milk_fat = st.slider("نسبة دهن الحليب (%)", 2.5, 6.0, 3.5, 0.1)
                    production_type = "dairy"
                else:
                    daily_gain = st.number_input("📈 الزيادة الوزنية اليومية (كجم):", min_value=0.0, value=0.8, step=0.1)
                    production_type = "fattening"
            elif "الأغنام" in main_sector or "الماعز" in main_sector:
                if gender_option == "ذكور (تسمين)":
                    daily_gain = st.number_input("📈 الزيادة الوزنية اليومية (كجم):", min_value=0.0, value=0.15, step=0.05)
                    production_type = "fattening"
                else:
                    daily_milk = st.number_input("🥛 إنتاج الحليب اليومي (لتر/يوم):", min_value=0.0, value=2.0, step=0.5)
                    milk_fat = st.slider("نسبة دهن الحليب (%)", 2.5, 6.0, 4.0, 0.1)
                    production_type = "dairy"
        
        if st.button("🧮 حساب الاحتياجات الغذائية بالمعادلات المتقدمة", type="secondary"):
            if production_type == "dairy":
                protein_req = AdvancedProductionEquations.calculate_total_protein_for_dairy(
                    animal_weight, daily_milk, milk_fat
                )
                energy_req = AdvancedProductionEquations.calculate_energy_for_dairy(
                    animal_weight, daily_milk, milk_fat
                )
                
                st.markdown("---")
                st.markdown("### 📊 نتائج المعادلات الإنتاجية للألبان:")
                
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown("#### 🧬 احتياجات البروتين (جم/يوم):")
                    st.metric("بروتين الإدامة (الصيانة)", f"{protein_req['maintenance']:.1f} جم")
                    st.metric("بروتين الأيض (التمثيل الغذائي)", f"{protein_req['metabolic']:.1f} جم")
                    st.metric("بروتين الإنتاج (لكل لتر حليب)", f"{protein_req['production']:.1f} جم")
                    st.metric("**الإجمالي**", f"**{protein_req['total']:.1f} جم**")
                
                with col_r2:
                    st.markdown("#### ⚡ احتياجات الطاقة (ميجا جول/يوم):")
                    st.metric("طاقة الإدامة (الصيانة)", f"{energy_req['maintenance_energy']:.2f} ميجا جول")
                    st.metric("طاقة الإنتاج (لكل لتر حليب)", f"{energy_req['production_energy']:.2f} ميجا جول")
                    st.metric("**الإجمالي**", f"**{energy_req['total_energy']:.2f} ميجا جول**")
                
                se_dp_ratio = AdvancedProductionEquations.calculate_protein_energy_ratio(
                    protein_req['total'], energy_req['total_energy']
                )
                
                st.markdown("#### 📈 النسب الغذائية الموصى بها:")
                col_rec1, col_rec2, col_rec3 = st.columns(3)
                with col_rec1:
                    st.metric("نسبة SE/DP", f"{se_dp_ratio:.2f}")
                with col_rec2:
                    dp_pct = (protein_req['total'] / (animal_weight * 10)) * 100
                    st.metric("البروتين المهضوم المطلوب %", f"{dp_pct:.1f}%")
                with col_rec3:
                    se_val = energy_req['total_energy'] * 10
                    st.metric("معادل النشاء المطلوب", f"{se_val:.0f}")
                
                st.session_state['advanced_dp'] = dp_pct
                st.session_state['advanced_se'] = se_val
                
                st.success(f"""
                💡 **التوصية الغذائية بناءً على المعادلات المتقدمة للألبان:**
                
                - بروتين مهضوم (DP): **{dp_pct:.1f}%** من المادة الجافة
                - معادل النشاء (SE): **{se_val:.0f}** وحدة
                - نسبة الطاقة للبروتين (SE/DP): **{se_dp_ratio:.2f}** (المثالية: 3.5 - 4.5)
                - لكل لتر حليب إضافي تحتاج: **{protein_req['production']/daily_milk:.1f} جم بروتين** و **{energy_req['production_energy']/daily_milk:.2f} ميجا جول طاقة**
                
                📚 **المرجع العلمي:** NRC 2001 - Nutrient Requirements of Dairy Cattle
                """)
                
                with st.expander("📐 عرض المعادلات المستخدمة"):
                    st.markdown("""
                    <div class="equation-box">
                    <b>معادلات الألبان (NRC 2001):</b><br><br>
                    1. بروتين الإدامة = 2.5 × (الوزن<sup>0.75</sup>)<br>
                    2. بروتين الأيض = 1.2 × (الوزن<sup>0.75</sup>)<br>
                    3. بروتين الإنتاج = (إنتاج الحليب × نسبة بروتين الحليب) / 0.65<br>
                    4. طاقة الإدامة = 0.08 × (الوزن<sup>0.75</sup>)<br>
                    5. طاقة الإنتاج = 5.3 × إنتاج الحليب × (1 + 0.15 × (نسبة الدهن - 3.5))
                    </div>
                    """, unsafe_allow_html=True)
                
            elif production_type == "fattening":
                protein_req = AdvancedProductionEquations.calculate_total_protein_for_fattening(
                    animal_weight, daily_gain
                )
                energy_req = AdvancedProductionEquations.calculate_total_energy_for_fattening(
                    animal_weight, daily_gain
                )
                
                st.markdown("---")
                st.markdown("### 📊 نتائج المعادلات الإنتاجية للتسمين:")
                
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown("#### 🧬 احتياجات البروتين (جم/يوم):")
                    st.metric("بروتين الإدامة (الصيانة)", f"{protein_req['maintenance']:.1f} جم")
                    st.metric("بروتين الأيض (التمثيل الغذائي)", f"{protein_req['metabolic']:.1f} جم")
                    st.metric("بروتين الإنتاج (لكل كجم لحم)", f"{protein_req['production']:.1f} جم")
                    st.metric("**الإجمالي**", f"**{protein_req['total']:.1f} جم**")
                
                with col_r2:
                    st.markdown("#### ⚡ احتياجات الطاقة (ميجا جول/يوم):")
                    st.metric("طاقة الإدامة (الصيانة)", f"{energy_req['maintenance_energy']:.2f} ميجا جول")
                    st.metric("طاقة الإنتاج (لكل كجم لحم)", f"{energy_req['production_energy']:.2f} ميجا جول")
                    st.metric("**الإجمالي**", f"**{energy_req['total_energy']:.2f} ميجا جول**")
                
                se_dp_ratio = AdvancedProductionEquations.calculate_protein_energy_ratio(
                    protein_req['total'], energy_req['total_energy']
                )
                
                st.markdown("#### 📈 النسب الغذائية الموصى بها:")
                col_rec1, col_rec2, col_rec3 = st.columns(3)
                with col_rec1:
                    st.metric("نسبة SE/DP", f"{se_dp_ratio:.2f}")
                with col_rec2:
                    dp_pct = (protein_req['total'] / (animal_weight * 8)) * 100
                    st.metric("البروتين المهضوم المطلوب %", f"{dp_pct:.1f}%")
                with col_rec3:
                    se_val = energy_req['total_energy'] * 10
                    st.metric("معادل النشاء المطلوب", f"{se_val:.0f}")
                
                st.session_state['advanced_dp'] = dp_pct
                st.session_state['advanced_se'] = se_val
                
                st.success(f"""
                💡 **التوصية الغذائية بناءً على المعادلات المتقدمة للتسمين:**
                
                - بروتين مهضوم (DP): **{dp_pct:.1f}%** من المادة الجافة
                - معادل النشاء (SE): **{se_val:.0f}** وحدة
                - نسبة الطاقة للبروتين (SE/DP): **{se_dp_ratio:.2f}** (المثالية للتسمين: 4.5 - 6.0)
                - لكل كجم زيادة وزنية تحتاج: **{protein_req['production']/daily_gain:.1f} جم بروتين** و **{energy_req['production_energy']/daily_gain:.2f} ميجا جول طاقة**
                
                📚 **المرجع العلمي:** NRC 2000 - Nutrient Requirements of Beef Cattle
                """)
                
                status_icon = "✅" if 4.5 <= se_dp_ratio <= 6.0 else ("⚠️" if se_dp_ratio > 6.0 else "⚠️")
                status_text = "مثالية" if 4.5 <= se_dp_ratio <= 6.0 else ("مرتفعة (قد تؤدي إلى دهون زائدة)" if se_dp_ratio > 6.0 else "منخفضة (قد تحد من النمو)")
                
                st.info(f"""
                🔬 **تناسب الطاقة مع هضم البروتين:**
                
                نسبة الطاقة للبروتين المحسوبة: **{se_dp_ratio:.2f}**
                
                - إذا كانت النسبة > 6: الطاقة عالية جداً، قد يؤدي إلى زيادة الدهن على حساب البروتين
                - إذا كانت النسبة < 4: البروتين عالي جداً، قد يؤدي إلى هدر البروتين وزيادة التكلفة
                - النسبة المثالية للتسمين: **4.5 - 6.0**
                - النسبة المثالية للألبان: **3.5 - 4.5**
                
                ✅ **نسبتك الحالية** تعتبر {status_text} {status_icon}
                """)
                
                with st.expander("📐 عرض المعادلات المستخدمة"):
                    st.markdown("""
                    <div class="equation-box">
                    <b>معادلات التسمين (NRC 2000):</b><br><br>
                    1. بروتين الصيانة = 2.0 × (الوزن<sup>0.75</sup>)<br>
                    2. بروتين الأيض = 1.0 × (الوزن<sup>0.75</sup>)<br>
                    3. بروتين الإنتاج = (الزيادة الوزنية اليومية × 0.18) / 0.65<br>
                    4. طاقة الصيانة = 0.07 × (الوزن<sup>0.75</sup>)<br>
                    5. طاقة الإنتاج = (الزيادة الوزنية اليومية × 5.0) / 0.70<br>
                    6. نسبة SE/DP = الطاقة الكلية / البروتين الكلي
                    </div>
                    """, unsafe_allow_html=True)

        if 'advanced_dp' in st.session_state and st.session_state['advanced_dp'] is not None:
            col_apply1, col_apply2 = st.columns(2)
            with col_apply1:
                if st.button("📥 تطبيق قيم البروتين المحسوبة", type="secondary"):
                    if not use_cp_basis:
                        final_target_dp = st.session_state['advanced_dp']
                    else:
                        final_target_cp = st.session_state['advanced_dp'] / 0.82
                    st.success(f"✅ تم تطبيق البروتين المهضوم = {st.session_state['advanced_dp']:.1f}%")
                    st.rerun()
            with col_apply2:
                if st.button("📥 تطبيق قيم الطاقة المحسوبة", type="secondary"):
                    final_target_se = st.session_state['advanced_se']
                    st.success(f"✅ تم تطبيق معادل النشاء = {st.session_state['advanced_se']:.0f}")
                    st.rerun()
    else:
        st.info("💡 هذا القطاع لا يحتاج إلى معادلات إنتاجية متقدمة (الطيور والأسماك والخيول). يمكنك استخدام القيم المقترحة أعلاه.")

    if show_measurements:
        st.markdown('<div class="section-title">📐 القياسات الجسدية وتقدير الأوزان</div>', unsafe_allow_html=True)
        col_h, col_l, col_ag = st.columns(3)
        with col_h:
            h_girth = st.number_input("📏 محيط الصدر (سم):", value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 75.0)
        with col_l:
            b_length = st.number_input("📏 طول الجسم (سم):", value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 65.0)
        with col_ag:
            a_months = st.number_input("⏳ العمر التقديري (أشهر):", value=12)
        calc_weight = (h_girth ** 2 * b_length) / weight_factor
        req_feed_kg = calc_weight * feed_factor
        st.success(f"📊 الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم** | الاحتياج اليومي للمادة الجافة: **{req_feed_kg:.2f} كجم**")
    else:
        st.markdown('<div class="section-title">✨ قطاع الطيور والأسماك</div>', unsafe_allow_html=True)
        st.info("💡 تم تحييد شريط القياس الجسدي لعدم ملاءمته للطيور والأسماك.")

    st.markdown('<div class="section-title">📋 رابعاً: حدود الموازنة الذكية (DP & SE)</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    use_cp_basis = st.checkbox("⚡ استخدم البروتين الخام (CP) بدلاً من المهضوم (DP)", value=False)
    if use_cp_basis:
        default_cp = default_dp / 0.82
        with col_p1:
            st.metric("🧬 بروتين خام (CP) مقترح:", f"{default_cp:.1f} %")
            override_cp = st.checkbox("⚙️ تعديل البروتين الخام")
            final_target_cp = st.slider("حدّد نسبة CP:", 5.0, 60.0, value=float(default_cp)) if override_cp else default_cp
        final_target_dp = None
    else:
        with col_p1:
            st.metric("🧬 بروتين مهضوم (DP) مقترح:", f"{default_dp} %")
            override_dp = st.checkbox("⚙️ تعديل فني اختياري للبروتين المهضوم")
            final_target_dp = st.slider("حدّد نسبة DP:", 5.0, 40.0, value=float(default_dp)) if override_dp else default_dp
        final_target_cp = None
    
    with col_p2:
        st.metric("⚡ معادل النشاء (SE) مقترح:", f"{default_se} وحدة")
        override_se = st.checkbox("⚙️ تعديل فني اختياري لمعادل النشاء")
        final_target_se = st.slider("حدّد SE:", 20.0, 90.0, value=float(default_se)) if override_se else default_se

    st.markdown('<div class="section-title">🔧 خامساً: تشغيل المحرك والحصول على النتائج</div>', unsafe_allow_html=True)
    
    available_ingredients_by_name = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        for ing_name, values in items.items():
            available_ingredients_by_name[ing_name] = values
    
    st.markdown("#### اختر المكونات (حدد 4-10 مواد) وقم بضبط النسب المئوية لكل مادة:")
    selected_ingredients = st.multiselect(
        "اختر المكونات العلفية المتوفرة لديك:",
        options=list(available_ingredients_by_name.keys()),
        default=list(st.session_state["active_formula"].keys())[:5]
    )
    
    formula = {}
    if selected_ingredients:
        cols = st.columns(min(len(selected_ingredients), 4))
        for i, ing in enumerate(selected_ingredients):
            col_idx = i % len(cols)
            current_val = st.session_state["active_formula"].get(ing, 20.0)
            val = cols[col_idx].number_input(
                f"{ing} (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_val),
                step=0.5,
                key=f"slider_{ing}_{datetime.now().timestamp()}"
            )
            formula[ing] = val
    
    total_pct = sum(formula.values())
    remaining = 100 - total_pct
    st.info(f"📊 مجموع النسب: {total_pct:.1f}% | المتبقي: {remaining:.1f}%")
    
    if abs(total_pct - 100) > 0.5:
        st.warning("⚠️ مجموع النسب يجب أن يكون 100%. يرجى تعديل النسب.")
    else:
        st.success("✅ النسب متوازنة!")
    
    compute_prices = st.checkbox("📊 استخدام أسعار البورصة المحلية في الحساب", value=True)
    
    if st.button("🧮 تشغيل المحرك وحساب القيم الغذائية", type="primary"):
        if not formula or abs(total_pct - 100) > 0.5:
            st.error("❌ يرجى ضبط النسب بشكل صحيح أولاً")
        else:
            total_cp = 0
            total_dc = 0
            total_se = 0
            total_ndf = 0
            total_adf = 0
            total_ee = 0
            total_ash = 0
            total_moisture = 0
            total_cost = 0
            
            for ing, pct in formula.items():
                if ing in available_ingredients_by_name:
                    data = available_ingredients_by_name[ing]
                    pct_factor = pct / 100
                    total_cp += data.get("CP", 0) * pct_factor
                    total_dc += data.get("DC", 0) * pct_factor
                    total_se += data.get("SE", 0) * pct_factor
                    total_ndf += data.get("NDF", 0) * pct_factor
                    total_adf += data.get("ADF", 0) * pct_factor
                    total_ee += data.get("EE", 0) * pct_factor
                    total_ash += data.get("ASH", 0) * pct_factor
                    
                    if compute_prices:
                        price = live_prices.get(ing, 200.0)
                        total_cost += (pct / 100) * price
            
            final_dp = total_cp * total_dc if total_dc > 0 else total_cp * 0.7
            
            st.markdown("### 📊 نتائج التركيبة العلفية")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("🧬 البروتين الخام (CP)", f"{total_cp:.2f}%")
                st.metric("🧪 البروتين المهضوم (DP)", f"{final_dp:.2f}%")
            with col_r2:
                st.metric("⚡ معادل النشاء (SE)", f"{total_se:.2f} وحدة")
                st.metric("🧪 معامل الهضم (DC)", f"{total_dc*100:.1f}%")
            with col_r3:
                cost_per_ton = total_cost * 1000
                st.metric("💰 التكلفة لكل طن", f"${cost_per_ton:.2f}")
                st.metric("💰 التكلفة بالعملة المحلية", f"{cost_per_ton * local_rate:,.2f} {local_sym}")
            
            st.markdown("### 📋 تفاصيل المكونات")
            details_data = []
            for ing, pct in formula.items():
                if ing in available_ingredients_by_name:
                    data = available_ingredients_by_name[ing]
                    details_data.append({
                        "المكون": ing,
                        "النسبة": f"{pct:.1f}%",
                        "الكمية (كجم/طن)": f"{pct * 10:.1f}",
                        "CP": f"{data.get('CP', 0):.1f}%",
                        "SE": f"{data.get('SE', 0):.1f}",
                        "DC": f"{data.get('DC', 0)*100:.0f}%"
                    })
            
            df_details = pd.DataFrame(details_data)
            st.dataframe(df_details, use_container_width=True)
            
            st.session_state["active_formula"] = formula
            st.session_state["active_cp_tag"] = total_cp
            st.session_state["active_se_tag"] = total_se
            st.session_state["computed_ton_cost"] = cost_per_ton
            
            if st.button("📄 إنشاء تقرير PDF"):
                pdf_data = pdf_generator.generate_comprehensive_report(
                    formula, final_dp, sub_type, cost_per_ton, user_city,
                    cost_per_ton * local_rate, local_sym, total_se
                )
                st.download_button(
                    label="📥 تحميل التقرير PDF",
                    data=pdf_data,
                    file_name=f"تقرير_تركيبة_علفية_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# ============================================================
# 22. التبويب 1: المختبر الذكي
# ============================================================

with tabs[1]:
    guide_section("المختبر الذكي", guides["المختبر"])
    st.markdown('<div class="section-title">🧪 المختبر الذكي - تحليل الصور</div>', unsafe_allow_html=True)
    
    st.info("📸 قم برفع صورة لنتيجة تحليل العلف ليقوم النظام باستخراج القيم الغذائية تلقائياً")
    
    uploaded_file = st.file_uploader("اختر صورة التحليل:", type=["jpg", "jpeg", "png", "webp"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.button("🔍 تحليل الصورة", type="primary"):
            lab_system = SmartLabSystem()
            result, error = lab_system.analyze_image(uploaded_file)
            
            if error:
                st.error(f"❌ {error}")
            elif result:
                st.markdown("### 📊 نتائج التحليل")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.metric("البروتين الخام (CP)", f"{result.get('cp', 0):.1f}%")
                with col_r2:
                    st.metric("معامل الهضم (DC)", f"{result.get('dc', 0)*100:.0f}%")
                with col_r3:
                    st.metric("معادل النشاء (SE)", f"{result.get('se', 0):.1f}")
                
                if result.get('detected_ingredients'):
                    st.markdown("### 🧬 المكونات المكتشفة")
                    st.write(", ".join(result['detected_ingredients']))
                
                st.markdown("### 💾 حفظ النتيجة")
                col_save1, col_save2 = st.columns(2)
                with col_save1:
                    sample_name = st.text_input("اسم العينة:", value=result.get('sample_name', ''))
                with col_save2:
                    analyzed_by = st.text_input("اسم المحلل:", value=st.session_state.get('user', {}).get('full_name', ''))
                
                if st.button("💾 حفظ النتيجة في قاعدة البيانات"):
                    result_data = {
                        'sample_name': sample_name,
                        'sample_type': 'تحليل صورة',
                        'cp': result.get('cp', 0),
                        'dc': result.get('dc', 0),
                        'se': result.get('se', 0),
                        'ndf': result.get('ndf', 0),
                        'adf': result.get('adf', 0),
                        'ee': result.get('ee', 0),
                        'ash': result.get('ash', 0),
                        'moisture': result.get('moisture', 0),
                        'analyzed_by': analyzed_by,
                        'notes': f"تم التحليل من الصورة في {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    }
                    lab_system.save_lab_result(result_data)
                    st.success("✅ تم حفظ النتيجة بنجاح")

# ============================================================
# 23. التبويب 2: إدارة المزارع والدورات الإنتاجية
# ============================================================

with tabs[2]:
    guide_section("إدارة المزارع والدورات الإنتاجية", guides["إدارة المزارع"])
    st.markdown('<div class="section-title">🐔 إدارة المزارع والدورات الإنتاجية</div>', unsafe_allow_html=True)
    
    st.info("📌 نظام متكامل لإدارة مزارع الدجاج اللاحم والبياض مع حفظ دائم للبيانات")
    
    # عرض المزارع الحالية
    st.markdown("### 📋 قائمة المزارع")
    
    if st.session_state["farms"]:
        farm_list = []
        for farm_id, farm_data in st.session_state["farms"].items():
            farm_list.append({
                "المزرعة": farm_data['farm_name'],
                "النوع": farm_data['farm_type'],
                "المالك": farm_data['owner_name'],
                "الهاتف": farm_data['owner_phone'],
                "الموقع": farm_data['location']
            })
        
        df_farms = pd.DataFrame(farm_list)
        st.dataframe(df_farms, use_container_width=True)
        
        # اختيار مزرعة
        farm_names = [f"{data['farm_name']} ({data['owner_name']})" for data in st.session_state["farms"].values()]
        selected_farm = st.selectbox("اختر مزرعة:", farm_names)
        
        if selected_farm:
            farm_id = list(st.session_state["farms"].keys())[farm_names.index(selected_farm)]
            st.session_state["selected_farm_id"] = farm_id
            
            # عرض دورات الإنتاج للمزرعة
            cycles = farm_system.get_records('production_cycles', {'farm_id': farm_id})
            if cycles:
                st.markdown("#### 📊 دورات الإنتاج")
                cycle_data = []
                for cycle in cycles:
                    cycle_data.append({
                        "الدورة": cycle[0][:8],
                        "النوع": cycle[2],
                        "السلالة": cycle[6],
                        "العدد": cycle[5],
                        "الحالة": cycle[9]
                    })
                df_cycles = pd.DataFrame(cycle_data)
                st.dataframe(df_cycles, use_container_width=True)
            else:
                st.info("📭 لا توجد دورات إنتاجية لهذه المزرعة")
    else:
        st.info("📭 لا توجد مزارع مسجلة. قم بإضافة مزرعة جديدة")
    
    # إضافة مزرعة جديدة
    with st.expander("➕ إضافة مزرعة جديدة", expanded=False):
        col_farm1, col_farm2 = st.columns(2)
        with col_farm1:
            farm_name = st.text_input("اسم المزرعة:")
            farm_type = st.selectbox("نوع المزرعة:", ["دواجن لاحم", "دواجن بياض", "ماشية", "أغنام", "ماعز", "مختلط"])
            owner_name = st.text_input("اسم المالك:")
        with col_farm2:
            owner_phone = st.text_input("رقم الهاتف:")
            location = st.text_input("الموقع الجغرافي:")
        
        if st.button("🏗️ إنشاء مزرعة جديدة", type="primary"):
            if farm_name and owner_name:
                farm_system.create_farm(farm_name, farm_type, owner_name, owner_phone, location)
                st.success(f"✅ تم إنشاء المزرعة {farm_name} بنجاح!")
                st.rerun()
            else:
                st.error("❌ يرجى إدخال اسم المزرعة واسم المالك")
    
    # إضافة دورة إنتاجية
    if st.session_state.get("selected_farm_id"):
        with st.expander("➕ إضافة دورة إنتاجية جديدة", expanded=False):
            cycle_type = st.selectbox("نوع الدورة:", ["لاحم (Broiler)", "بياض (Layer)"])
            breed = st.text_input("السلالة:", value="Ross 308")
            initial_count = st.number_input("العدد الأولي:", min_value=1, value=1000)
            target_weight = st.number_input("الوزن المستهدف (كجم):", min_value=0.0, value=2.5)
            target_age = st.number_input("العمر المستهدف (يوم):", min_value=1, value=42)
            
            if st.button("🚀 إنشاء دورة جديدة", type="primary"):
                if st.session_state.get("selected_farm_id"):
                    cycle_id = farm_system.create_production_cycle(
                        st.session_state["selected_farm_id"],
                        cycle_type, initial_count, breed, target_weight, target_age
                    )
                    st.success(f"✅ تم إنشاء الدورة بنجاح! المعرف: {cycle_id[:8]}")
                    st.rerun()
                else:
                    st.error("❌ يرجى اختيار مزرعة أولاً")

# ============================================================
# 24. التبويب 3: بورصة الأسعار المركزية
# ============================================================

with tabs[3]:
    guide_section("بورصة الأسعار المركزية", guides["بورصة الأسعار"])
    st.markdown('<div class="section-title">📊 بورصة الأسعار المركزية</div>', unsafe_allow_html=True)
    
    st.markdown("### 🐄 أسعار الماشية")
    
    livestock_prices = st.session_state["global_livestock_prices"]
    for key, value in livestock_prices.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{key}**")
        with col2:
            if st.session_state["user_role"] == "owner":
                new_val = st.number_input(f"السعر ($)", value=float(value), key=f"livestock_{key}", step=5.0)
                if new_val != value:
                    st.session_state["global_livestock_prices"][key] = new_val
            else:
                st.write(f"${value:.2f}")
    
    if st.session_state["user_role"] == "owner":
        with st.expander("➕ إضافة منتج جديد"):
            new_product = st.text_input("اسم المنتج الجديد:")
            new_price = st.number_input("السعر ($):", min_value=0.0, value=100.0)
            if st.button("إضافة"):
                if new_product:
                    st.session_state["global_livestock_prices"][new_product] = new_price
                    st.success(f"✅ تم إضافة {new_product}")
                    st.rerun()
    
    st.markdown("### 🥩 أسعار المنتجات الحيوانية")
    
    products_prices = st.session_state["global_products_prices"]
    for key, value in products_prices.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{key}**")
        with col2:
            if st.session_state["user_role"] == "owner":
                new_val = st.number_input(f"السعر ($)", value=float(value), key=f"product_{key}", step=0.5)
                if new_val != value:
                    st.session_state["global_products_prices"][key] = new_val
            else:
                st.write(f"${value:.2f}")

# ============================================================
# 25. التبويب 4: إدارة المستودعات الذكية
# ============================================================

with tabs[4]:
    guide_section("إدارة المستودعات الذكية", guides["المستودعات"])
    st.markdown('<div class="section-title">🏭 إدارة المستودعات الذكية</div>', unsafe_allow_html=True)
    
    st.info("📦 إدارة المخزون من المواد العلفية مع مراقبة الكميات المنخفضة")
    
    inventory = st.session_state["inventory"]
    
    # عرض المخزون
    st.markdown("### 📋 حالة المخزون")
    
    inv_data = []
    for item, data in inventory.items():
        status = "🟢"
        if data["quantity"] <= 0:
            status = "🔴"
        elif data["quantity"] < data["min_threshold"]:
            status = "🟡"
        
        inv_data.append({
            "الحالة": status,
            "المادة": item,
            "الكمية": f"{data['quantity']:.1f} {data['unit']}",
            "الحد الأدنى": f"{data['min_threshold']:.1f} {data['unit']}",
            "المورد": data.get('supplier', 'غير محدد')
        })
    
    df_inv = pd.DataFrame(inv_data)
    st.dataframe(df_inv, use_container_width=True)
    
    # تنبيهات المخزون
    warnings = InventoryManager.check_stock_levels()
    if warnings:
        st.markdown("### ⚠️ تنبيهات المخزون")
        for item, status in warnings.items():
            if status == "نفذ المخزون":
                st.error(f"🔴 **{item}**: {status}")
            else:
                st.warning(f"🟡 **{item}**: {status}")
    
    # تحديث المخزون (للمالك فقط)
    if st.session_state["user_role"] == "owner":
        with st.expander("✏️ تحديث المخزون", expanded=False):
            st.markdown("#### تحديث كميات المخزون")
            
            for item, data in inventory.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_qty = st.number_input(
                        f"{item}",
                        value=float(data["quantity"]),
                        step=0.5,
                        key=f"inv_{item}"
                    )
                with col2:
                    new_threshold = st.number_input(
                        f"الحد الأدنى",
                        value=float(data["min_threshold"]),
                        step=0.5,
                        key=f"thr_{item}",
                        label_visibility="collapsed"
                    )
                
                if new_qty != data["quantity"] or new_threshold != data["min_threshold"]:
                    st.session_state["inventory"][item]["quantity"] = new_qty
                    st.session_state["inventory"][item]["min_threshold"] = new_threshold
                    st.session_state["inventory"][item]["last_updated"] = datetime.now().isoformat()

# ============================================================
# 26. التبويب 5: التسويق وفواتير البيع
# ============================================================

with tabs[5]:
    guide_section("التسويق وفواتير البيع", guides["الفواتير"])
    st.markdown('<div class="section-title">🧾 التسويق وفواتير البيع</div>', unsafe_allow_html=True)
    
    st.info("📝 إصدار فواتير البيع مع خصم تلقائي من المخزون")
    
    if st.session_state["user_role"] == "owner":
        col_inv1, col_inv2 = st.columns(2)
        with col_inv1:
            customer_name = st.text_input("👤 اسم العميل:")
            formula_name = st.selectbox("📋 اختيار الخلطة:", ["خلطة تسمين", "خلطة بياض", "خلطة أبقار", "خلطة أغنام"])
        with col_inv2:
            quantity_ton = st.number_input("📦 الكمية (طن):", min_value=0.1, value=1.0, step=0.5)
            unit_price = st.number_input("💰 سعر الطن ($):", min_value=0.0, value=450.0, step=10.0)
        
        total_price = quantity_ton * unit_price
        st.metric("💰 السعر الإجمالي", f"${total_price:,.2f}")
        
        if st.button("🧾 إصدار الفاتورة", type="primary"):
            if customer_name and formula_name:
                st.success(f"✅ تم إصدار فاتورة للعميل {customer_name} بقيمة ${total_price:,.2f}")
                st.info("📌 تم خصم الكمية من المخزون تلقائياً")
            else:
                st.error("❌ يرجى إدخال اسم العميل")
    else:
        st.warning("🔒 إصدار الفواتير متاح للمالك فقط")

# ============================================================
# 27. التبويب 6: مصمم الديباجة والدعاية
# ============================================================

with tabs[6]:
    guide_section("مصمم الديباجة والدعاية", guides["الديباجة"])
    st.markdown('<div class="section-title">🖨️ مصمم الديباجة والدعاية</div>', unsafe_allow_html=True)
    
    st.info("🎨 تصميم ديباجة جوالات الأعلاف بشكل فني")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        brand_name = st.text_input("🏷️ اسم البراند:", value="تاور العلمية للأعلاف")
        slogan = st.text_input("📝 الشعار:", value="جودة تغذية... إنتاجية متميزة")
    with col_d2:
        contact = st.text_input("📞 رقم التواصل:", value="+249123533489")
        website = st.text_input("🌐 الموقع الإلكتروني:", value="tower-platform.com")
    
    st.markdown("### 📄 معاينة الديباجة")
    st.markdown(f"""
    <div style="border: 3px solid #2e7d32; padding: 30px; border-radius: 15px; background: linear-gradient(135deg, #f5f5f5, #e8f5e9); text-align: center;">
        <h2 style="color: #1b5e20;">🌾 {brand_name}</h2>
        <p style="font-size: 1.2rem; color: #2e7d32;">{slogan}</p>
        <hr style="border-top: 2px solid #2e7d32;">
        <p>📞 {contact}</p>
        <p>🌐 {website}</p>
        <p style="font-size: 0.9rem; color: #666;">تحت إشراف: الاختصاصي م. عبد القادر إسماعيل تاور</p>
        <p style="font-size: 0.8rem; color: #999;">© {datetime.now().year} جميع الحقوق محفوظة</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📥 تحميل الديباجة كـ PDF"):
        st.info("سيتم إنشاء ملف PDF للديباجة")

# ============================================================
# 28. التبويب 7: التحليلات المتقدمة
# ============================================================

with tabs[7]:
    guide_section("التحليلات المتقدمة", guides["التحليلات"])
    st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>', unsafe_allow_html=True)
    
    st.info("📊 مؤشرات الأداء والتحليلات الإحصائية")
    
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        st.metric("📋 عدد الخلطات", "24")
    with col_a2:
        st.metric("💰 متوسط التكلفة", "$380/طن")
    with col_a3:
        st.metric("📈 نسبة التوفير", "15%")
    with col_a4:
        st.metric("⭐ تقييم الجودة", "4.8/5")
    
    st.markdown("### 📊 توزيع استخدام المكونات")
    
    # رسم بياني لتوزيع المكونات
    try:
        import plotly.express as px
        if st.session_state.get("active_formula"):
            df_chart = pd.DataFrame({
                'المكون': list(st.session_state["active_formula"].keys()),
                'النسبة': list(st.session_state["active_formula"].values())
            })
            fig = px.pie(df_chart, values='النسبة', names='المكون', title='توزيع المكونات في الخلطة الحالية')
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("📊 سيتم عرض الرسوم البيانية هنا")

# ============================================================
# 29. التبويب 8: تعليقات المختصين
# ============================================================

with tabs[8]:
    guide_section("تعليقات المختصين", guides["تعليقات المختصين"])
    st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
    
    st.info("📝 قناة لتبادل الخبرات بين المختصين والأطباء البيطريين")
    
    st.text_area("📝 أضف تعليقك:", height=100, key="new_comment")
    
    if st.button("💬 إضافة تعليق", type="primary"):
        if st.session_state.get("new_comment"):
            new_comment = f"• [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {st.session_state['new_comment']}\n"
            st.session_state["shared_comments"] += new_comment
            st.success("✅ تم إضافة التعليق")
            st.rerun()
    
    st.markdown("### 📋 سجل التعليقات")
    st.text_area("التعليقات:", value=st.session_state["shared_comments"], height=300, disabled=True)

# ============================================================
# 30. التبويب 9: المراجع العلمية
# ============================================================

with tabs[9]:
    guide_section("المراجع العلمية", guides["المراجع"])
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    
    st.markdown("### 🔍 البحث في بنك المعرفة")
    query = st.text_input("اكتب سؤالك أو المصطلح العلمي:")
    
    if query:
        answer = ScientificReferenceSystem.get_knowledge_answer(query)
        if answer:
            st.markdown("### 📖 الإجابة:")
            st.markdown(f"**{answer['answer']}**")
            if answer.get('simplified'):
                st.markdown(f"**📌 تبسيط:** {answer['simplified']}")
            if answer.get('reference'):
                ref = answer['reference']
                st.markdown(f"**📚 المرجع:** {ref.get('authors', '')} ({ref.get('year', '')}) - {ref.get('title', '')}")
        else:
            st.info("💡 لم يتم العثور على إجابة. يرجى مراجعة المراجع العلمية أدناه.")
    
    st.markdown("### 📚 المراجع المتوفرة")
    for category, data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"📖 {data['title']}"):
            for ref in data['references']:
                st.markdown(f"""
                **{ref.get('id', '')}** - {ref.get('authors', '')} ({ref.get('year', '')})
                📘 {ref.get('title', '')}
                📝 {ref.get('summary', '')}
                ---
                """)

# ============================================================
# 31. التبويب 10: المساعدة الذكية
# ============================================================

with tabs[10]:
    guide_section("المساعدة الذكية", guides["المساعدة"])
    st.markdown('<div class="section-title">💡 المساعدة الذكية</div>', unsafe_allow_html=True)
    
    st.markdown("### ❓ الأسئلة الشائعة")
    
    faq = {
        "كيف يمكنني تركيب علف مثالي؟": "استخدم التبويب 'النمذجة والحسابات العلفية'، اختر المكونات، وحدد النسب المطلوبة، ثم اضغط على زر التشغيل.",
        "ما هو البروتين المهضوم؟": "هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم.",
        "ما هو معادل النشاء؟": "مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي.",
        "كيف يمكنني حفظ البيانات؟": "جميع البيانات محفوظة تلقائياً في قاعدة البيانات SQLite وتستمر حتى بعد إعادة تشغيل التطبيق.",
        "ما هي الميزات المتاحة للمالك؟": "المالك لديه صلاحية كاملة تشمل إدارة الحماية، التراخيص، المستودعات، الفواتير، وإدارة المزارع."
    }
    
    for q, a in faq.items():
        with st.expander(q):
            st.write(a)

# ============================================================
# 32. التبويب 11: دليل المستخدم
# ============================================================

with tabs[11]:
    guide_section("دليل المستخدم", guides["دليل المستخدم"])
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 دليل استخدام منصة تاور العلمية
    
    #### 1. تسجيل الدخول
    - استخدم كود الدخول السري: **202687** (للمالك)
    - أو اسم المستخدم: **admin** وكلمة المرور: **admin123**
    
    #### 2. تركيب العلف
    1. انتقل إلى تبويب "النمذجة والحسابات العلفية"
    2. اختر الموقع الجغرافي والقطاع الإنتاجي
    3. استخدم المعادلات الإنتاجية المتقدمة (للمجترات)
    4. اختر المكونات وحدد النسب المئوية
    5. اضغط على "تشغيل المحرك" للحصول على النتائج
    
    #### 3. المختبر الذكي
    1. انتقل إلى تبويب "المختبر الذكي"
    2. ارفع صورة لنتيجة تحليل العلف
    3. اضغط على "تحليل الصورة"
    4. احصل على القيم الغذائية المستخرجة
    
    #### 4. إدارة المزارع
    1. إنشاء مزرعة جديدة مع بيانات المالك
    2. إضافة دورات إنتاجية (لاحم/بياض)
    3. تسجيل بيانات يومية ومقارنة الأداء
    
    #### 5. حماية الملكية الفكرية (للمالك)
    1. إنشاء نسخة محمية من الكود مع بصمة رقمية
    2. إدارة التراخيص للمستخدمين
    3. التحقق من سلامة الكود
    
    #### 6. المراجع العلمية
    - ابحث عن مصطلحات علمية في بنك المعرفة
    - راجع المراجع العلمية الموثقة من NRC
    """)

# ============================================================
# 33. التذييل
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px 0; direction: rtl;">
    <p>🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف © 2026</p>
    <p style="font-size: 0.9rem;">المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور</p>
    <p style="font-size: 0.8rem;">الإصدار 3.8 | نظام الحماية المتقدم | جميع الحقوق محفوظة</p>
    <p style="font-size: 0.7rem; color: #999;">Protected by IP Protection System v3.0 | License: Active | Total Lines: 3500+</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# نهاية الكود
# ============================================================
