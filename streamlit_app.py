# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 3.9 (متوافق مع جميع البيئات)
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

# ===== محاولة استيراد مكتبة التشفير (مع fallback) =====
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    # استخدام بديل بسيط للتشفير
    import base64
    import hashlib
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad

# ===== نظام حماية الملكية الفكرية (متوافق مع جميع البيئات) =====
class IPProtectionSystem:
    """
    نظام متقدم لحماية الملكية الفكرية للكود
    يدعم بيئات بدون cryptography
    """
    
    _SECRET_KEY = b'tower_platform_secure_key_2026_abdulqader_ismail_tawer_v3'
    _SALT = b'tower_salt_protection_2026_v3'
    
    @classmethod
    def _derive_key(cls, password: str = None) -> bytes:
        """اشتقاق مفتاح تشفير من كلمة مرور"""
        if password is None:
            password = "AbdulQader_Tawer_2026_Protected"
        
        if CRYPTO_AVAILABLE:
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=cls._SALT,
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            # طريقة بديلة باستخدام hashlib
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), cls._SALT, 100000, 32)
            return base64.urlsafe_b64encode(key)
    
    @classmethod
    def encrypt_code(cls, code: str, password: str = None) -> str:
        """تشفير الكود لحمايته"""
        key = cls._derive_key(password)
        
        if CRYPTO_AVAILABLE:
            from cryptography.fernet import Fernet
            f = Fernet(key)
            encrypted = f.encrypt(code.encode('utf-8'))
        else:
            # طريقة بديلة باستخدام AES
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            cipher = AES.new(key[:32], AES.MODE_CBC, key[:16])
            encrypted = cipher.encrypt(pad(code.encode('utf-8'), AES.block_size))
        
        return base64.b64encode(encrypted).decode('utf-8')
    
    @classmethod
    def decrypt_code(cls, encrypted_code: str, password: str = None) -> str:
        """فك تشفير الكود"""
        try:
            key = cls._derive_key(password)
            encrypted = base64.b64decode(encrypted_code)
            
            if CRYPTO_AVAILABLE:
                from cryptography.fernet import Fernet
                f = Fernet(key)
                decrypted = f.decrypt(encrypted)
            else:
                # طريقة بديلة باستخدام AES
                from Crypto.Cipher import AES
                from Crypto.Util.Padding import unpad
                cipher = AES.new(key[:32], AES.MODE_CBC, key[:16])
                decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
            
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"❌ فشل فك التشفير: {e}")
    
    @classmethod
    def generate_signature(cls, code: str) -> str:
        """إنشاء بصمة رقمية للكود"""
        return hashlib.sha3_256(code.encode('utf-8')).hexdigest()
    
    @classmethod
    def generate_signature_with_metadata(cls, code: str, metadata: dict = None) -> dict:
        """إنشاء بصمة رقمية مع بيانات وصفية"""
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'timestamp': datetime.now().isoformat(),
            'version': '3.9',
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
        """التحقق من صحة البصمة الرقمية"""
        if metadata is None:
            metadata = {}
        
        metadata_str = json.dumps(metadata, sort_keys=True)
        combined = code + metadata_str
        expected = hashlib.sha3_256(combined.encode('utf-8')).hexdigest()
        return hmac.compare_digest(signature, expected)
    
    @classmethod
    def generate_license_key(cls, user_id: str, expiry_days: int = 365, 
                            features: List[str] = None) -> dict:
        """إنشاء مفتاح ترخيص فريد مع ميزات"""
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
        """التحقق من صحة مفتاح الترخيص"""
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
        """إدراج علامة مائية متقدمة في الكود"""
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
        """إنشاء نسخة محمية كاملة من الكود"""
        watermarked = cls.embed_watermark(code)
        signature_data = cls.generate_signature_with_metadata(watermarked, metadata)
        encrypted = cls.encrypt_code(watermarked, password)
        
        protected_package = {
            'protected_code': encrypted,
            'signature': signature_data['signature'],
            'metadata': signature_data['metadata'],
            'created_at': signature_data['created_at'],
            'version': '3.9',
            'protection_level': 'advanced',
            'watermark': True,
            'encryption': 'Fernet/AES-128' if CRYPTO_AVAILABLE else 'AES-128 (Fallback)',
            'hash_algorithm': 'SHA3-256'
        }
        
        return protected_package
    
    @classmethod
    def extract_protected_version(cls, protected_package: dict, password: str = None) -> dict:
        """استخراج الكود من النسخة المحمية"""
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

# ===== نظام إدارة التراخيص =====
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

# ===== مكتبة الصوت (gTTS) =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ===== مكتبات PDF واللغة العربية =====
try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import inch, mm
    from reportlab.lib.colors import HexColor, black, white, grey
    from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_AVAILABLE = True
except ImportError:
    ARABIC_AVAILABLE = False

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
        autoplay_attr = "autoplay" if autoplay else ""
        controls_attr = "controls" if controls else ""
        html = f'''
        <audio {autoplay_attr} {controls_attr} style="width: 100%; max-width: 400px; margin: 10px auto; display: block;">
            <source src="{url}" type="audio/mpeg">
            متصفحك لا يدعم تشغيل الصوت
        </audio>
        '''
        st.markdown(html, unsafe_allow_html=True)
    
    @staticmethod
    def play_surah_fatiha():
        """تشغيل سورة الفاتحة بصوت الشيخ السديس"""
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
            except:
                continue
        
        st.warning("⚠️ تعذر تشغيل الصوت تلقائياً. يرجى الضغط على زر التشغيل.")
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
    """عرض دليل استخدام للتبويب مع خيار صوتي ونصي"""
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{guide_text}</div>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button(f"🔊 تشغيل الدليل صوتياً ({tab_name})"):
                EnhancedAudioSystem.play_audio_from_text(guide_text)
        with col_g2:
            st.caption("يمكنك قراءة الدليل أعلاه أو الاستماع إليه.")

# ============================================================
# نظام قاعدة البيانات المتقدم
# ============================================================

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
        
        # جدول نتائج المختبر
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
# نظام إدارة المزارع
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

# ============================================================
# نظام المصادقة
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
# نظام المراجع العلمية
# ============================================================

class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education",
                 "edition": "7th Edition", "isbn": "978-1408204238",
                 "summary": "المرجع الأساسي في تغذية الحيوان، يغطي جميع جوانب التغذية من الهضم إلى متطلبات العناصر الغذائية."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.",
                 "year": 2009, "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press", "edition": "3rd Edition",
                 "isbn": "978-1904761578", "summary": "المرجع العملي في تغذية الدواجن التجارية."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.",
                 "year": 1993, "title": "The Ruminant Animal: Digestive Physiology and Nutrition",
                 "publisher": "Waveland Press", "isbn": "978-0881337389",
                 "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف.",
            "reference": "REF001",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان.",
            "reference": "REF001",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
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
# نظام المعادلات الإنتاجية المتقدمة
# ============================================================

class AdvancedProductionEquations:
    @staticmethod
    def calculate_maintenance_protein(weight_kg: float) -> float:
        return 2.5 * (weight_kg ** 0.75)
    
    @staticmethod
    def calculate_milk_protein_requirement(milk_yield_kg: float) -> float:
        efficiency = 0.65
        protein_in_milk = milk_yield_kg * 0.033
        return protein_in_milk / efficiency
    
    @staticmethod
    def calculate_total_protein_for_dairy(weight_kg: float, milk_yield_kg: float) -> dict:
        maintenance = AdvancedProductionEquations.calculate_maintenance_protein(weight_kg)
        production = AdvancedProductionEquations.calculate_milk_protein_requirement(milk_yield_kg)
        total = maintenance + production
        return {
            'maintenance': maintenance,
            'production': production,
            'total': total
        }

# ============================================================
# نظام المختبر الذكي
# ============================================================

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
            return None, "مكتبات OCR غير مثبتة"
        
        results = []
        try:
            if EASYOCR_AVAILABLE and hasattr(self, 'reader') and self.reader:
                result = self.reader.readtext(image)
                for (bbox, text, prob) in result:
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                img = Image.open(image)
                text = pytesseract.image_to_string(img, lang='ara+eng')
                results = text.split('\n')
            
            analyzed_data = self._parse_ocr_results(results)
            return analyzed_data, None
        except Exception as e:
            return None, f"خطأ في تحليل الصورة: {str(e)}"
    
    def _parse_ocr_results(self, texts):
        data = {
            'sample_name': '',
            'cp': None,
            'dc': None,
            'se': None,
            'detected_ingredients': []
        }
        
        patterns = {
            'cp': [r'بروتين\s*خام\s*[:=]?\s*([\d.]+)', r'CP\s*[:=]?\s*([\d.]+)'],
            'dc': [r'معامل\s*الهضم\s*[:=]?\s*([\d.]+)', r'DC\s*[:=]?\s*([\d.]+)'],
            'se': [r'معادل\s*النشاء\s*[:=]?\s*([\d.]+)', r'SE\s*[:=]?\s*([\d.]+)']
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

# ============================================================
# مكتبة الأعلاف الكاملة
# ============================================================

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0}
    },
    "🌱 مصادر البروتين": {
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0}
    }
}

# ============================================================
# إعدادات المنصة
# ============================================================

st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
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
            "أمباز الفول السوداني": 460.0, "كسب فول صويا 44%": 440.0,
            "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0,
            "كسب بذور القطن": 290.0, "نخالة قمح (ردة)": 150.0,
            "البرسيم الجاف": 170.0, "مولاس قصب السكر": 120.0,
            "مسحوق أسماك 60%": 850.0, "مركزات دواجن": 650.0,
            "مركزات خيول ومجترات": 600.0,
            "الحجر الجيري": 40.0, "فوسفات ثنائي الكالسيوم": 280.0,
            "ملح الطعام": 30.0, "بيكربونات الصوديوم": 340.0
        }
        feed_prices.update(base_prices)
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
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

# ============================================================
# حالة الجلسة
# ============================================================

if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "session_token" not in st.session_state: st.session_state["session_token"] = None
if "farms" not in st.session_state: st.session_state["farms"] = {}
if "selected_farm_id" not in st.session_state: st.session_state["selected_farm_id"] = None
if "selected_cycle_id" not in st.session_state: st.session_state["selected_cycle_id"] = None
if "audio_played" not in st.session_state: st.session_state["audio_played"] = False
if "license_checked" not in st.session_state: st.session_state["license_checked"] = False
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        for ing in items:
            st.session_state["inventory"][ing] = {
                "quantity": 25.0,
                "min_threshold": 5.0,
                "unit": "طن",
                "last_updated": datetime.now().isoformat()
            }
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين": 1350.0,
        "أبقار كنانة محلية": 900.0,
        "ضأن محلي": 180.0,
        "ماعز نوبي": 130.0,
        "خيول عربية أصيلة": 4500.0,
        "كتكوت لاحم": 0.65,
        "دجاج بياض": 5.50
    }
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري": 7.50,
        "كيلو لحم ضأن": 9.00,
        "كيلو لحم دجاج": 3.80,
        "طبق بيض 30": 4.20,
        "لتر حليب خام": 0.90,
        "كيلو جبن أبيض": 5.00
    }
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = "• [توجيه الاختصاصي]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا.\n"
if "active_formula" not in st.session_state:
    st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "lab_system" not in st.session_state:
    st.session_state["lab_system"] = SmartLabSystem()

# ============================================================
# CSS المحسّن
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
* { font-family: 'Cairo', sans-serif; }
.main-box {
    background: rgba(255,255,255,0.98);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.18);
    margin-bottom: 50px;
    backdrop-filter: blur(5px);
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
}
.profile-img-style {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    display: block;
    margin: 0 auto;
}
.license-status {
    padding: 10px 15px;
    border-radius: 8px;
    margin: 10px 0;
    text-align: center;
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
.stButton > button {
    color: #1a1a1a !important;
    background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important;
    font-weight: bold !important;
}
.stButton > button:hover {
    background-color: #c8e6c9 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# بوابة الدخول
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
    
    EnhancedAudioSystem.play_surah_fatiha()
    
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)
    
    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")
        if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
            input_code_stripped = input_code.strip()
            if input_code_stripped in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = CODES_DB[input_code_stripped]["role"]
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                
                if st.session_state["user_role"] == "owner":
                    LicenseManager.generate_license("owner_abdulqader_tawer", 3650)
                
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
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

# ============================================================
# تشغيل الصوت الترحيبي
# ============================================================

if st.session_state["approved"] and not st.session_state.get("audio_played", False):
    play_welcome_audio()
    st.session_state["audio_played"] = True

if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👋 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.",
        "breeder": "🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح."
    }
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"))
    st.session_state["login_welcome_shown"] = True

# ============================================================
# التحقق من الترخيص
# ============================================================

if not st.session_state.get("license_checked", False):
    license_status = LicenseManager.get_license_status()
    
    if license_status['valid']:
        st.markdown(f"""
        <div class="license-status license-valid">
        ✅ {license_status['message']} | المستخدم: {license_status.get('user_id', '')} | 
        متبقي: {license_status.get('days_remaining', 0)} يوم
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
# الواجهة الرئيسية
# ============================================================

st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    st.markdown("""
    <div style="text-align: center;">
        <div style="width: 150px; height: 150px; border-radius: 50%; background: linear-gradient(135deg, #1b5e20, #2e7d32); 
                    display: flex; align-items: center; justify-content: center; margin: 0 auto; border: 4px solid #d4af37;">
            <span style="font-size: 4rem;">🌾</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem;'>محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم (DP) ومعادل النشاء (SE)</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

# ============================================================
# زر تسجيل الخروج
# ============================================================

col_logout, col_status = st.columns([0.7, 0.3])
with col_logout:
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory", "farms", "lab_system"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

with col_status:
    role_info = {"owner": "المالك 👑", "specialist": "المختص 👨‍🔬", "breeder": "المربي 🌾"}
    st.markdown(f"""<div style='text-align: left; font-size:0.9rem; background: #f5f5f5; padding: 10px; border-radius: 10px;'>الحساب: <b>{role_info.get(st.session_state["user_role"], "مستخدم")}</b></div>""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# عرض وظيفة حماية الملكية الفكرية للمالك
# ============================================================

def show_protection_management():
    st.markdown("### 🛡️ نظام حماية الملكية الفكرية")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔐 التشفير", "AES-128" if CRYPTO_AVAILABLE else "AES-128 (Fallback)")
    with col2:
        st.metric("🖊️ خوارزمية التوقيع", "SHA3-256")
    with col3:
        license_status = LicenseManager.get_license_status()
        st.metric("🔑 حالة الترخيص", "✅ ساري" if license_status['valid'] else "❌ منتهي")
    
    st.markdown("#### 🔐 إنشاء نسخة محمية من الكود")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        password = st.text_input("🔑 كلمة مرور للحماية (اختياري):", type="password")
        owner_name = st.text_input("👤 اسم المالك:", value="AbdulQader Ismail Tawer")
    
    with col_p2:
        metadata = {
            "owner": owner_name,
            "platform": "Tower Scientific Platform",
            "year": 2026,
            "rights": "All Rights Reserved"
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
                
                st.success("✅ تم إنشاء النسخة المحمية بنجاح!")
                
                st.download_button(
                    label="📥 تحميل الكود المحمي",
                    data=protected['protected_code'],
                    file_name=f"tower_platform_protected_{datetime.now().strftime('%Y%m%d')}.py",
                    mime="text/plain",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ فشل إنشاء النسخة المحمية: {str(e)}")

if st.session_state["user_role"] == "owner":
    with st.expander("🛡️ حماية الملكية الفكرية - لوحة التحكم", expanded=False):
        show_protection_management()

# ============================================================
# التبويبات
# ============================================================

tabs_titles = [
    "🔬 النمذجة والحسابات العلفية",
    "🧪 المختبر الذكي",
    "🐔 إدارة المزارع",
    "📊 بورصة الأسعار",
    "🏭 المستودعات",
    "🧾 الفواتير",
    "📚 المراجع العلمية",
    "💡 المساعدة الذكية",
    "📖 دليل المستخدم"
]

tabs = st.tabs(tabs_titles)

# ============================================================
# التبويب 0: النمذجة والحسابات العلفية
# ============================================================

with tabs[0]:
    st.markdown('<div class="section-title">🌍 تحديد الموقع الجغرافي</div>', unsafe_allow_html=True)
    
    col_country, col_state, col_city = st.columns(3)
    with col_country:
        user_country = st.selectbox("اختر الدولة:", ["السودان", "LIBYA", "مصر", "باقي دول العالم"])
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]
    local_sym = c_info["sym"]
    
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("الولاية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف"])
        else:
            chosen_state = st.selectbox("الإقليم:", ["عام"])
    
    with col_city:
        user_city = st.text_input("المدينة:", "الخرطوم")
    
    live_prices = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)
    
    st.markdown('<div class="section-title">⚖️ اختيار القطاع والإنتاجية</div>', unsafe_allow_html=True)
    
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec:
        main_sector = st.selectbox("القطاع:", ["الأغنام", "الماعز", "الأبقار", "الدواجن"])
    
    default_dp = 11.0
    default_se = 60.0
    
    with col_sub:
        if main_sector == "الأبقار":
            sub_type = st.selectbox("النوع:", ["كنانة", "هولشتاين"])
            default_dp = 12.5
            default_se = 68.0
        elif main_sector == "الدواجن":
            sub_type = st.selectbox("النوع:", ["لاحم", "بياض"])
            default_dp = 20.0 if sub_type == "لاحم" else 15.0
            default_se = 76.0 if sub_type == "لاحم" else 70.0
        else:
            sub_type = st.selectbox("النوع:", ["محلي", "محسن"])
            default_dp = 11.5
            default_se = 62.0
    
    with col_prod:
        if main_sector == "الأبقار":
            prod_stage = st.selectbox("نوع الإنتاج:", ["حليب", "تسمين"])
        else:
            prod_stage = st.selectbox("نوع الإنتاج:", ["نمو", "إنتاج"])
    
    st.markdown('<div class="section-title">📋 حدود الموازنة</div>', unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        target_dp = st.slider("البروتين المهضوم (DP) %:", 5.0, 40.0, value=float(default_dp))
    with col_p2:
        target_se = st.slider("معادل النشاء (SE):", 20.0, 90.0, value=float(default_se))
    
    st.markdown('<div class="section-title">🔧 اختيار المكونات</div>', unsafe_allow_html=True)
    
    available_ingredients = []
    for category in BIG_FEEDS_LIBRARY.values():
        available_ingredients.extend(category.keys())
    
    selected_ingredients = st.multiselect(
        "اختر المكونات:",
        available_ingredients,
        default=["ذرة صفراء", "كسب فول صويا 44%"]
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
                key=f"slider_{ing}"
            )
            formula[ing] = val
    
    total_pct = sum(formula.values())
    remaining = 100 - total_pct
    st.info(f"📊 مجموع النسب: {total_pct:.1f}% | المتبقي: {remaining:.1f}%")
    
    if abs(total_pct - 100) > 0.5:
        st.warning("⚠️ مجموع النسب يجب أن يكون 100%")
    else:
        st.success("✅ النسب متوازنة!")
    
    if st.button("🧮 حساب القيم الغذائية", type="primary"):
        if not formula or abs(total_pct - 100) > 0.5:
            st.error("❌ يرجى ضبط النسب أولاً")
        else:
            total_cp = 0
            total_dc = 0
            total_se = 0
            total_cost = 0
            
            for ing, pct in formula.items():
                pct_factor = pct / 100
                for cat in BIG_FEEDS_LIBRARY.values():
                    if ing in cat:
                        data = cat[ing]
                        total_cp += data.get("CP", 0) * pct_factor
                        total_dc += data.get("DC", 0) * pct_factor
                        total_se += data.get("SE", 0) * pct_factor
                        price = live_prices.get(ing, 200.0)
                        total_cost += (pct / 100) * price
                        break
            
            final_dp = total_cp * total_dc if total_dc > 0 else total_cp * 0.7
            
            st.markdown("### 📊 النتائج")
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("البروتين الخام (CP)", f"{total_cp:.2f}%")
                st.metric("البروتين المهضوم (DP)", f"{final_dp:.2f}%")
            with col_r2:
                st.metric("معادل النشاء (SE)", f"{total_se:.2f} وحدة")
                st.metric("معامل الهضم (DC)", f"{total_dc*100:.1f}%")
            with col_r3:
                cost_per_ton = total_cost * 1000
                st.metric("التكلفة للطن", f"${cost_per_ton:.2f}")
                st.metric("بالعملة المحلية", f"{cost_per_ton * local_rate:,.2f} {local_sym}")

# ============================================================
# التبويب 1: المختبر الذكي
# ============================================================

with tabs[1]:
    st.markdown('<div class="section-title">🧪 المختبر الذكي</div>', unsafe_allow_html=True)
    st.info("📸 ارفع صورة لنتيجة تحليل العلف")
    
    uploaded_file = st.file_uploader("اختر صورة:", type=["jpg", "jpeg", "png"])
    
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

# ============================================================
# التبويب 2: إدارة المزارع
# ============================================================

with tabs[2]:
    st.markdown('<div class="section-title">🐔 إدارة المزارع</div>', unsafe_allow_html=True)
    
    if st.session_state["farms"]:
        farm_list = []
        for farm_id, farm_data in st.session_state["farms"].items():
            farm_list.append({
                "المزرعة": farm_data['farm_name'],
                "النوع": farm_data['farm_type'],
                "المالك": farm_data['owner_name'],
                "الهاتف": farm_data['owner_phone']
            })
        df_farms = pd.DataFrame(farm_list)
        st.dataframe(df_farms, use_container_width=True)
    else:
        st.info("📭 لا توجد مزارع مسجلة")
    
    with st.expander("➕ إضافة مزرعة جديدة", expanded=False):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            farm_name = st.text_input("اسم المزرعة:")
            farm_type = st.selectbox("النوع:", ["دواجن لاحم", "دواجن بياض", "ماشية"])
        with col_f2:
            owner_name = st.text_input("اسم المالك:")
            owner_phone = st.text_input("رقم الهاتف:")
        
        if st.button("🏗️ إنشاء مزرعة", type="primary"):
            if farm_name and owner_name:
                farm_system = FarmManagementSystem()
                farm_system.create_farm(farm_name, farm_type, owner_name, owner_phone)
                st.success(f"✅ تم إنشاء المزرعة {farm_name}")
                st.rerun()

# ============================================================
# التبويب 3: بورصة الأسعار
# ============================================================

with tabs[3]:
    st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
    
    st.markdown("### 🐄 أسعار الماشية")
    for key, value in st.session_state["global_livestock_prices"].items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{key}**")
        with col2:
            st.write(f"${value:.2f}")
    
    st.markdown("### 🥩 أسعار المنتجات")
    for key, value in st.session_state["global_products_prices"].items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{key}**")
        with col2:
            st.write(f"${value:.2f}")

# ============================================================
# التبويب 4: المستودعات
# ============================================================

with tabs[4]:
    st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
    
    inv_data = []
    for item, data in st.session_state["inventory"].items():
        inv_data.append({
            "المادة": item,
            "الكمية": f"{data['quantity']:.1f} {data['unit']}",
            "الحد الأدنى": f"{data['min_threshold']:.1f} {data['unit']}"
        })
    
    df_inv = pd.DataFrame(inv_data)
    st.dataframe(df_inv, use_container_width=True)

# ============================================================
# التبويب 5: الفواتير
# ============================================================

with tabs[5]:
    st.markdown('<div class="section-title">🧾 الفواتير</div>', unsafe_allow_html=True)
    
    if st.session_state["user_role"] == "owner":
        col_inv1, col_inv2 = st.columns(2)
        with col_inv1:
            customer_name = st.text_input("اسم العميل:")
            formula_name = st.selectbox("الخلطة:", ["خلطة تسمين", "خلطة بياض"])
        with col_inv2:
            quantity_ton = st.number_input("الكمية (طن):", min_value=0.1, value=1.0, step=0.5)
            unit_price = st.number_input("سعر الطن ($):", min_value=0.0, value=450.0, step=10.0)
        
        total_price = quantity_ton * unit_price
        st.metric("السعر الإجمالي", f"${total_price:,.2f}")
        
        if st.button("🧾 إصدار الفاتورة", type="primary"):
            if customer_name:
                st.success(f"✅ تم إصدار فاتورة للعميل {customer_name} بقيمة ${total_price:,.2f}")
    else:
        st.warning("🔒 إصدار الفواتير متاح للمالك فقط")

# ============================================================
# التبويب 6: المراجع العلمية
# ============================================================

with tabs[6]:
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    
    query = st.text_input("🔍 ابحث في بنك المعرفة:")
    
    if query:
        answer = ScientificReferenceSystem.get_knowledge_answer(query)
        if answer:
            st.markdown("### 📖 الإجابة:")
            st.markdown(f"**{answer['answer']}**")
            if answer.get('simplified'):
                st.markdown(f"📌 {answer['simplified']}")
    
    st.markdown("### 📚 المراجع المتوفرة")
    for category, data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"📖 {data['title']}"):
            for ref in data['references']:
                st.markdown(f"""
                **{ref.get('id', '')}** - {ref.get('authors', '')} ({ref.get('year', '')})
                📘 {ref.get('title', '')}
                📝 {ref.get('summary', '')}
                """)

# ============================================================
# التبويب 7: المساعدة الذكية
# ============================================================

with tabs[7]:
    st.markdown('<div class="section-title">💡 المساعدة الذكية</div>', unsafe_allow_html=True)
    
    faq = {
        "كيف يمكنني تركيب علف مثالي؟": "استخدم التبويب 'النمذجة والحسابات العلفية'، اختر المكونات وحدد النسب.",
        "ما هو البروتين المهضوم؟": "هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً.",
        "ما هو معادل النشاء؟": "مقياس لكمية الطاقة التي يوفرها العلف للحيوان."
    }
    
    for q, a in faq.items():
        with st.expander(q):
            st.write(a)

# ============================================================
# التبويب 8: دليل المستخدم
# ============================================================

with tabs[8]:
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 دليل استخدام المنصة
    
    #### 1. تسجيل الدخول
    - كود المالك: **202687**
    - المستخدم الافتراضي: admin / admin123
    
    #### 2. تركيب العلف
    1. حدد الموقع الجغرافي
    2. اختر القطاع الإنتاجي
    3. حدد المكونات والنسب
    4. اضغط على حساب القيم
    
    #### 3. المختبر الذكي
    1. ارفع صورة التحليل
    2. اضغط على تحليل الصورة
    3. احصل على النتائج
    
    #### 4. إدارة المزارع
    1. أضف مزرعة جديدة
    2. أضف دورات إنتاجية
    3. تابع الأداء
    """)

# ============================================================
# التذييل
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px 0; direction: rtl;">
    <p>🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف © 2026</p>
    <p style="font-size: 0.9rem;">المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور</p>
    <p style="font-size: 0.8rem;">الإصدار 3.9 | نظام الحماية المتقدم | جميع الحقوق محفوظة</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# نهاية الكود
# ============================================================
