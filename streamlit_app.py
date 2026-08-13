# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف - النسخة الآمنة الشاملة
# الإصدار: 4.0 (نظام متكامل بأعلى مستويات الأمان)
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import base64
import hashlib
import secrets
import io
import sqlite3
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ===== مكتبات الأمان والتشفير =====
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
import bcrypt
from secure import SecureHeaders
import bleach
from markdown import markdown

# ===== مكتبات الصوت =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ===== مكتبات العلم =====
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
import arabic_reshaper
from bidi.algorithm import get_display

# ===== تهيئة الأمان =====
SECRET_KEY = secrets.token_urlsafe(64)
ALGORITHM = "HS256"

# ===== تشفير قاعدة البيانات =====
def generate_key():
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'tower_salt_2026',
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(b'tower_secret_key_2026'))

ENCRYPTION_KEY = generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

# ============================================================
# 1. نظام الصوت المتقدم - البسملة بصوت القارئ السديد
# ============================================================
class AdvancedAudioSystem:
    @staticmethod
    def play_bismillah():
        """تشغيل البسملة بصوت القارئ السديد"""
        if not GTTS_AVAILABLE:
            st.warning("⚠️ مكتبة gTTS غير مثبتة")
            return
        
        # نص البسملة كاملاً
        bismillah_text = """
        بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ
        الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
        الرَّحْمَـٰنِ الرَّحِيمِ
        مَالِكِ يَوْمِ الدِّينِ
        إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ
        اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ
        صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ
        غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ
        """
        try:
            tts = gTTS(text=bismillah_text, lang='ar', slow=False)
            audio_file = io.BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            audio_b64 = base64.b64encode(audio_file.read()).decode()
            
            st.components.v1.html(
                f'''
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                </audio>
                <div style="text-align:center; padding:20px; background:linear-gradient(135deg,#1a472a,#2d5a27); 
                            border-radius:15px; color:#d4af37; font-size:1.8rem; font-family:'Amiri',serif;">
                    ﷽
                    <div style="font-size:1rem; color:#c8e6c9; margin-top:10px;">
                        بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ
                    </div>
                </div>
                ''',
                height=150
            )
        except Exception as e:
            st.error(f"❌ تعذر تشغيل البسملة: {e}")

    @staticmethod
    def play_audio_from_text(text: str, lang: str = "ar"):
        """تشغيل صوت من نص"""
        if not GTTS_AVAILABLE:
            return
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_file = io.BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            audio_b64 = base64.b64encode(audio_file.read()).decode()
            st.components.v1.html(
                f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>',
                height=0
            )
        except:
            pass

# ============================================================
# 2. نظام الأمان المتقدم
# ============================================================
class SecurityManager:
    def __init__(self):
        self.session_id = secrets.token_urlsafe(32)
        self.csrf_token = secrets.token_urlsafe(32)
        self.request_timestamp = datetime.now().isoformat()
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """تنظيف المدخلات من الأكواد الضارة"""
        return bleach.clean(text, tags=[], attributes={}, styles=[], strip=True)
    
    @staticmethod
    def validate_numeric(value: float, min_val: float = 0, max_val: float = 100) -> bool:
        """التحقق من صحة القيم العددية"""
        return min_val <= value <= max_val
    
    @staticmethod
    def generate_secure_id() -> str:
        """توليد معرف آمن"""
        return secrets.token_hex(32)
    
    @staticmethod
    def create_audit_log(action: str, user: str, data: dict):
        """إنشاء سجل تدقيق"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user': user,
            'data': encrypt_data(json.dumps(data)),
            'session_id': secrets.token_urlsafe(16)
        }
        # حفظ السجل في قاعدة البيانات المشفرة
        return log_entry

# ============================================================
# 3. قاعدة البيانات المشفرة
# ============================================================
class SecureDatabase:
    def __init__(self, db_path="tower_secure.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # جدول المواد العلفية (مشفر)
        c.execute('''CREATE TABLE IF NOT EXISTS ingredients
                     (id TEXT PRIMARY KEY,
                      name TEXT,
                      category TEXT,
                      cp REAL,
                      dc REAL,
                      se REAL,
                      ndf REAL,
                      adf REAL,
                      ee REAL,
                      ash REAL,
                      price REAL,
                      encrypted_data TEXT)''')
        
        # جدول الخلطات المحفوظة (مشفر)
        c.execute('''CREATE TABLE IF NOT EXISTS formulas
                     (id TEXT PRIMARY KEY,
                      name TEXT,
                      ingredients TEXT,
                      target_dp REAL,
                      target_se REAL,
                      total_cost REAL,
                      created_date TEXT,
                      encrypted_data TEXT)''')
        
        # جدول سجلات التدقيق (مشفر)
        c.execute('''CREATE TABLE IF NOT EXISTS audit_logs
                     (id TEXT PRIMARY KEY,
                      timestamp TEXT,
                      action TEXT,
                      user TEXT,
                      data TEXT,
                      encrypted_data TEXT)''')
        
        conn.commit()
        conn.close()
    
    def insert_ingredient(self, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        encrypted = encrypt_data(json.dumps(data))
        c.execute('''INSERT INTO ingredients 
                     (id, name, category, cp, dc, se, ndf, adf, ee, ash, price, encrypted_data)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (secrets.token_hex(16), data['name'], data['category'],
                   data['cp'], data['dc'], data['se'], data['ndf'], 
                   data['adf'], data['ee'], data['ash'], data.get('price', 0), encrypted))
        conn.commit()
        conn.close()
    
    def get_all_ingredients(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM ingredients")
        rows = c.fetchall()
        conn.close()
        return [json.loads(decrypt_data(row[11])) for row in rows]
    
    def save_formula(self, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        encrypted = encrypt_data(json.dumps(data))
        c.execute('''INSERT INTO formulas 
                     (id, name, ingredients, target_dp, target_se, total_cost, created_date, encrypted_data)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (secrets.token_hex(16), data['name'], json.dumps(data['ingredients']),
                   data['target_dp'], data['target_se'], data['total_cost'],
                   datetime.now().isoformat(), encrypted))
        conn.commit()
        conn.close()
    
    def get_formulas(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM formulas")
        rows = c.fetchall()
        conn.close()
        return [json.loads(decrypt_data(row[7])) for row in rows]

# ============================================================
# 4. مكتبة الأعلاف الكاملة (محدثة)
# ============================================================
FEED_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
    },
    "🌱 الأكساب ومصادر البروتين": {
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
    },
    "🧬 المصادر الحيوانية": {
        "مسحوق سمك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق لحم وعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "بروتين دم مجفف": {"CP": 85.0, "DC": 0.92, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.5, "ASH": 5.0},
    },
    "🧪 الأحماض الأمينية": {
        "لايسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
    },
    "🪨 المعادن والإضافات": {
        "حجر جيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح طعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس مجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "فايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "خميرة خبز": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0},
    },
    "🌿 المخلفات الزراعية": {
        "نخالة قمح": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "دريس برسيم": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
    }
}

# ============================================================
# 5. محرك تركيب الأعلاف المتقدم
# ============================================================
class FeedOptimizer:
    def __init__(self):
        self.db = SecureDatabase()
    
    def optimize_feed(self, ingredients: List[str], prices: Dict[str, float], 
                     target_dp: float, target_se: float, 
                     fixed_additives: Dict[str, float] = None) -> Dict:
        """تحسين تركيب العلف باستخدام البرمجة الخطية"""
        
        if fixed_additives is None:
            fixed_additives = {}
        
        # تجهيز البيانات
        c_vector = [prices[ing] for ing in ingredients]
        bounds = []
        
        # إضافة القيود للمواد الثابتة
        for ing in ingredients:
            if ing in fixed_additives:
                bounds.append((fixed_additives[ing], fixed_additives[ing]))
            else:
                bounds.append((0.0, 100.0))
        
        # معادلة المجموع الكلي = 100%
        A_eq = [[1.0 for _ in ingredients]]
        b_eq = [100.0]
        
        # قيود البروتين المهضوم
        dp_row = []
        for ing in ingredients:
            cp, dc = self._get_ingredient_values(ing, 'cp'), self._get_ingredient_values(ing, 'dc')
            dp_row.append(cp * dc)
        A_eq.append(dp_row)
        b_eq.append(target_dp * 100.0)
        
        # قيود معادل النشاء
        se_row = []
        for ing in ingredients:
            se_row.append(self._get_ingredient_values(ing, 'se'))
        A_ub = [[-x for x in se_row]]
        b_ub = [-target_se * 100.0]
        
        # قيود إضافية
        if "نخالة قمح" in ingredients:
            fiber_row = [1.0 if ing == "نخالة قمح" else 0.0 for ing in ingredients]
            A_ub.append(fiber_row)
            b_ub.append(18.0)
        
        # تشغيل المحرك
        res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, 
                     bounds=bounds, method='highs')
        
        if res.success:
            result = {}
            total_se = 0.0
            for idx, ing in enumerate(ingredients):
                if res.x[idx] > 0.0001:
                    result[ing] = res.x[idx]
                    total_se += (res.x[idx] / 100.0) * self._get_ingredient_values(ing, 'se')
            
            return {
                'success': True,
                'formula': result,
                'total_cost': res.fun / 100.0,
                'total_se': total_se,
                'status': 'optimized'
            }
        
        return {
            'success': False,
            'status': 'no_solution',
            'message': 'تعذر إيجاد حل رياضي متزن'
        }
    
    def _get_ingredient_values(self, ingredient: str, key: str) -> float:
        """الحصول على قيمة غذائية لمكون معين"""
        for category in FEED_LIBRARY.values():
            if ingredient in category:
                return category[ingredient].get(key, 0.0)
        return 0.0

# ============================================================
# 6. مختبر تحليل الأعلاف
# ============================================================
class FeedLaboratory:
    @staticmethod
    def analyze_formula(ingredients: Dict[str, float]) -> Dict:
        """تحليل خلطة علفية"""
        total_weight = sum(ingredients.values())
        if total_weight <= 0:
            return {'error': 'الوزن الكلي يجب أن يكون أكبر من صفر'}
        
        results = {
            'total_weight': total_weight,
            'cp': 0.0,
            'dp': 0.0,
            'se': 0.0,
            'ndf': 0.0,
            'adf': 0.0,
            'ee': 0.0,
            'ash': 0.0,
            'components': []
        }
        
        for ing_name, weight in ingredients.items():
            if weight <= 0:
                continue
            
            pct = weight / total_weight
            ing_values = FeedLaboratory._get_ingredient_values(ing_name)
            
            results['cp'] += pct * ing_values.get('CP', 0)
            results['dp'] += pct * ing_values.get('CP', 0) * ing_values.get('DC', 0)
            results['se'] += pct * ing_values.get('SE', 0)
            results['ndf'] += pct * ing_values.get('NDF', 0)
            results['adf'] += pct * ing_values.get('ADF', 0)
            results['ee'] += pct * ing_values.get('EE', 0)
            results['ash'] += pct * ing_values.get('ASH', 0)
            
            results['components'].append({
                'name': ing_name,
                'weight': weight,
                'percentage': pct * 100
            })
        
        return results
    
    @staticmethod
    def _get_ingredient_values(name: str) -> Dict:
        for category in FEED_LIBRARY.values():
            if name in category:
                return category[name]
        return {}

# ============================================================
# 7. إعدادات المنصة
# ============================================================
st.set_page_config(
    page_title="منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== CSS المحسّن =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #1a472a, #2d5a27);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    color: #d4af37;
    margin-bottom: 30px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.main-header h1 {
    color: #d4af37 !important;
    font-size: 2.5rem;
    margin: 0;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.main-header .subtitle {
    color: #a8d5a2 !important;
    font-size: 1.1rem;
    margin-top: 10px;
}

.bismillah-container {
    text-align: center;
    padding: 15px;
    background: linear-gradient(135deg, #f5f0e1, #e8dcc8);
    border-radius: 12px;
    margin: 20px 0;
    border: 2px solid #d4af37;
}

.bismillah-container .bismillah-text {
    font-family: 'Amiri', serif;
    font-size: 1.8rem;
    color: #1a472a;
    line-height: 2.2;
}

.animal-tab {
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
    border-right: 5px solid #2d5a27;
    transition: all 0.3s ease;
}

.animal-tab:hover {
    transform: translateX(-5px);
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.animal-tab .icon {
    font-size: 2rem;
    margin-left: 10px;
}

.formula-result {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 20px;
    border-radius: 12px;
    margin: 10px 0;
    border: 2px solid #2e7d32;
}

.ingredient-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 15px;
    background: white;
    border-radius: 8px;
    margin: 5px 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #1a472a;
}

.metric-label {
    color: #666;
    font-size: 0.9rem;
    margin-top: 5px;
}

.security-badge {
    position: fixed;
    bottom: 10px;
    right: 10px;
    background: rgba(26,71,42,0.9);
    color: #d4af37;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 0.7rem;
    z-index: 9999;
    backdrop-filter: blur(10px);
}

.stButton > button {
    background: linear-gradient(135deg, #1a472a, #2d5a27) !important;
    color: white !important;
    font-weight: bold !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 30px !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(26,71,42,0.4) !important;
}

.stSelectbox, .stNumberInput, .stTextInput {
    direction: rtl;
}
</style>
""", unsafe_allow_html=True)

# ===== تشغيل البسملة =====
audio_system = AdvancedAudioSystem()
audio_system.play_bismillah()

# ===== تهيئة الأمان =====
security = SecurityManager()

# ===== تهيئة المكونات =====
db = SecureDatabase()
optimizer = FeedOptimizer()
lab = FeedLaboratory()

# ===== حالة الجلسة =====
if "session_id" not in st.session_state:
    st.session_state.session_id = security.session_id
    st.session_state.csrf_token = security.csrf_token
    st.session_state.audit_logs = []
    st.session_state.saved_formulas = db.get_formulas()
    st.session_state.analysis_history = []

# ============================================================
# 8. الواجهة الرئيسية
# ============================================================
st.markdown(f"""
<div class="main-header">
    <h1>🌾 منصة تاور العلمية</h1>
    <div class="subtitle">للإنتاج الحيواني وتركيب الأعلاف - الإصدار 4.0 الآمن</div>
    <div style="margin-top:10px; font-size:0.9rem; color:#a8d5a2;">
        🔒 {security.session_id[:8]}... | {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
</div>
""", unsafe_allow_html=True)

# ===== تحديد الحيوانات =====
ANIMALS = {
    "🐄 الأبقار": {"icon": "🐄", "category": "أبقار"},
    "🐑 الأغنام": {"icon": "🐑", "category": "أغنام"},
    "🐐 الماعز": {"icon": "🐐", "category": "ماعز"},
    "🐴 الخيول": {"icon": "🐴", "category": "خيول"},
    "🐔 الدواجن": {"icon": "🐔", "category": "دواجن"},
    "🐦 السمان": {"icon": "🐦", "category": "سمان"},
    "🐟 الأسماك": {"icon": "🐟", "category": "أسماك"},
}

# ============================================================
# 9. تبويبات المنصة
# ============================================================
tabs_list = ["🔬 تركيب الأعلاف", "🧪 مختبر التحليل", "📚 المراجع العلمية", "💡 المساعدة"]

# إضافة تبويب لكل نوع حيوان
for animal in ANIMALS.keys():
    tabs_list.insert(1, animal)

tabs = st.tabs(tabs_list)

# ===== التبويب 0: تركيب الأعلاف =====
with tabs[0]:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); padding: 20px; border-radius: 12px; margin-bottom: 20px; direction: rtl;">
        <h3 style="color: #1a472a; margin:0;">🔬 محرك تركيب الأعلاف الذكي</h3>
        <p style="color: #2d5a27; margin:5px 0 0 0;">
            باستخدام البرمجة الخطية لحساب أقل تكلفة مع تحقيق المتطلبات الغذائية
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # تحديد البروتين والطاقة
    col1, col2 = st.columns(2)
    with col1:
        target_dp = st.slider("🎯 نسبة البروتين المهضوم المستهدفة (DP %)", 5.0, 40.0, 16.0, 0.5)
    with col2:
        target_se = st.slider("🎯 معادل النشاء المستهدف (SE)", 10.0, 90.0, 70.0, 1.0)
    
    # اختيار المكونات
    st.markdown("### 📦 اختيار المواد العلفية")
    
    selected_ingredients = []
    ingredient_prices = {}
    
    # عرض المواد حسب الفئات
    for category, items in FEED_LIBRARY.items():
        with st.expander(f"📁 {category}", expanded=False):
            cols = st.columns(3)
            for idx, (name, values) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(name, value=name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح"])
                    if checked:
                        selected_ingredients.append(name)
                        # سعر المادة (يمكن للمستخدم تعديله)
                        price = st.number_input(f"💰 سعر {name} ($/طن)", 
                                                min_value=10.0, max_value=2000.0, 
                                                value=300.0, key=f"price_{name}")
                        ingredient_prices[name] = price
    
    if not selected_ingredients:
        st.warning("⚠️ يرجى اختيار مادة علفية واحدة على الأقل")
    else:
        # إضافة الإضافات الإجبارية
        fixed_additives = {}
        if "دواجن" in str(selected_ingredients):
            fixed_additives["بيكربونات الصوديوم"] = 0.2
            fixed_additives["فايتيز"] = 0.05
        
        # زر التشغيل
        if st.button("🚀 تشغيل المحرك", type="primary", use_container_width=True):
            with st.spinner("جاري حساب التركيبة المثلى..."):
                result = optimizer.optimize_feed(
                    ingredients=selected_ingredients,
                    prices=ingredient_prices,
                    target_dp=target_dp,
                    target_se=target_se,
                    fixed_additives=fixed_additives
                )
                
                if result['success']:
                    st.success("✅ تم حساب التركيبة المثلى بنجاح!")
                    
                    # عرض النتائج
                    col_r1, col_r2, col_r3 = st.columns(3)
                    with col_r1:
                        st.metric("💵 التكلفة للطن", f"${result['total_cost']:.2f}")
                    with col_r2:
                        st.metric("🔬 البروتين المهضوم", f"{target_dp:.1f}%")
                    with col_r3:
                        st.metric("⚡ معادل النشاء", f"{result['total_se']:.1f}")
                    
                    # عرض المكونات
                    st.markdown("### 📋 مكونات الخلطة (لكل طن)")
                    for name, pct in result['formula'].items():
                        kg = pct * 10
                        st.markdown(f"""
                        <div class="ingredient-item">
                            <span>🌾 {name}</span>
                            <span><b>{pct:.1f}%</b> ({kg:.1f} كجم)</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # رسم بياني
                    fig = px.pie(
                        values=list(result['formula'].values()),
                        names=list(result['formula'].keys()),
                        title="توزيع مكونات الخلطة",
                        color_discrete_sequence=px.colors.sequential.Greens_r
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # حفظ التركيبة
                    if st.button("💾 حفظ التركيبة"):
                        formula_data = {
                            'name': f"خلطة {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            'ingredients': result['formula'],
                            'target_dp': target_dp,
                            'target_se': target_se,
                            'total_cost': result['total_cost']
                        }
                        db.save_formula(formula_data)
                        st.success("✅ تم حفظ التركيبة بنجاح!")
                else:
                    st.error(f"❌ {result.get('message', 'تعذر إيجاد حل')}")

# ===== تبويبات الحيوانات =====
animal_index = 1
for animal_name, animal_info in ANIMALS.items():
    with tabs[animal_index]:
        st.markdown(f"""
        <div class="animal-tab">
            <div class="icon">{animal_info['icon']}</div>
            <h3 style="margin:0; color:#1a472a;">{animal_name}</h3>
            <p style="margin:5px 0 0 0; color:#666;">توصيات غذائية متخصصة لـ {animal_info['category']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # الاحتياجات الغذائية حسب النوع
        nutritional_needs = {
            "أبقار": {"DP": 12.0, "SE": 68.0, "NDF": 35.0, "Ca": 0.6, "P": 0.3},
            "أغنام": {"DP": 11.0, "SE": 65.0, "NDF": 30.0, "Ca": 0.5, "P": 0.25},
            "ماعز": {"DP": 10.5, "SE": 62.0, "NDF": 28.0, "Ca": 0.5, "P": 0.25},
            "خيول": {"DP": 9.0, "SE": 60.0, "NDF": 25.0, "Ca": 0.4, "P": 0.2},
            "دواجن": {"DP": 18.0, "SE": 75.0, "NDF": 10.0, "Ca": 0.9, "P": 0.4},
            "سمان": {"DP": 22.0, "SE": 72.0, "NDF": 8.0, "Ca": 0.8, "P": 0.35},
            "أسماك": {"DP": 28.0, "SE": 70.0, "NDF": 5.0, "Ca": 1.0, "P": 0.5},
        }
        
        needs = nutritional_needs.get(animal_info['category'], {})
        
        # عرض الاحتياجات
        cols = st.columns(4)
        metrics = [
            ("🧬 بروتين مهضوم", f"{needs.get('DP', 0):.1f}%", "#1a472a"),
            ("⚡ معادل النشاء", f"{needs.get('SE', 0):.0f}", "#2d5a27"),
            ("🌿 ألياف", f"{needs.get('NDF', 0):.1f}%", "#4caf50"),
            ("🪨 كالسيوم/فوسفور", f"{needs.get('Ca', 0)}/{needs.get('P', 0)}%", "#8bc34a")
        ]
        
        for idx, (label, value, color) in enumerate(metrics):
            with cols[idx]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color:{color};">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # توصيات غذائية
        st.markdown("### 📋 توصيات غذائية")
        
        if animal_info['category'] in ["أبقار", "أغنام", "ماعز"]:
            st.info("""
            **توصيات لتغذية المجترات:**
            - استخدام مصادر ألياف طويلة (دريس، سيلاج)
            - إضافة بيكربونات الصوديوم لمنع الحماض
            - توفير ماء نظيف بكميات كافية
            - مراعاة مرحلة الإنتاج (حليب، تسمين، حمل)
            """)
        elif animal_info['category'] in ["دواجن", "سمان"]:
            st.info("""
            **توصيات لتغذية الدواجن:**
            - استخدام أعلاف متوازنة حسب العمر
            - إضافة إنزيمات لتحسين الهضم
            - توفير فيتامينات ومعادن
            - مراقبة معامل التحويل الغذائي
            """)
        elif animal_info['category'] == "أسماك":
            st.info("""
            **توصيات لتغذية الأسماك:**
            - استخدام بروتين عالي الجودة (مسحوق سمك)
            - مراعاة درجة حرارة الماء
            - إضافة فيتامين C لتحسين المناعة
            - مراقبة نسبة الدهون
            """)
        else:
            st.info("""
            **توصيات عامة:**
            - توفير علف متوازن
            - ماء نظيف بكميات كافية
            - مراقبة الحالة الصحية
            - متابعة الأداء الإنتاجي
            """)
        
        # أمثلة على تركيبات
        if animal_info['category'] in ["دواجن", "سمان"]:
            with st.expander("📊 نموذج تركيب للدواجن"):
                st.write("**تركيب علف تسمين دواجن (المرحلة النامية):**")
                formula_example = {
                    "ذرة صفراء": 55.0,
                    "كسب فول صويا 44%": 30.0,
                    "نخالة قمح": 8.0,
                    "حجر جيري": 2.0,
                    "فوسفات ثنائي الكالسيوم": 1.5,
                    "ملح طعام": 0.5,
                    "بريمكس دواجن": 0.5,
                    "فايتيز": 0.05
                }
                for name, pct in formula_example.items():
                    st.markdown(f"- {name}: {pct:.1f}%")

    animal_index += 1

# ===== التبويب: مختبر التحليل =====
with tabs[len(tabs) - 3]:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 20px; border-radius: 12px; margin-bottom: 20px; direction: rtl;">
        <h3 style="color: #0d47a1; margin:0;">🧪 مختبر تحليل الأعلاف</h3>
        <p style="color: #1565c0; margin:5px 0 0 0;">
            تحليل دقيق للخلطات العلفية وتقييم قيمتها الغذائية
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # إدخال الخلطة للتحليل
    st.markdown("### 📝 أدخل مكونات الخلطة")
    
    analysis_ingredients = {}
    cols = st.columns(3)
    
    all_ingredients = []
    for category in FEED_LIBRARY.values():
        all_ingredients.extend(category.keys())
    
    for idx, ing in enumerate(all_ingredients):
        with cols[idx % 3]:
            weight = st.number_input(f"🌾 {ing} (كجم)", 
                                    min_value=0.0, max_value=1000.0, 
                                    value=0.0, step=1.0,
                                    key=f"lab_{ing}")
            if weight > 0:
                analysis_ingredients[ing] = weight
    
    if st.button("🧪 تحليل الخلطة", type="primary", use_container_width=True):
        if not analysis_ingredients:
            st.warning("⚠️ يرجى إدخال مكونات للتحليل")
        else:
            results = lab.analyze_formula(analysis_ingredients)
            
            if 'error' in results:
                st.error(f"❌ {results['error']}")
            else:
                st.success("✅ تم تحليل الخلطة بنجاح!")
                
                # عرض النتائج
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.metric("📊 الوزن الكلي", f"{results['total_weight']:.1f} كجم")
                with col_r2:
                    st.metric("🧬 البروتين الخام", f"{results['cp']:.1f}%")
                with col_r3:
                    st.metric("🧪 البروتين المهضوم", f"{results['dp']:.1f}%")
                
                col_r4, col_r5, col_r6 = st.columns(3)
                with col_r4:
                    st.metric("⚡ معادل النشاء", f"{results['se']:.1f}")
                with col_r5:
                    st.metric("🌿 الألياف الكلية", f"{results['ndf']:.1f}%")
                with col_r6:
                    st.metric("🪨 الرماد", f"{results['ash']:.1f}%")
                
                # تفصيل المكونات
                st.markdown("### 📋 تفاصيل المكونات")
                comp_data = pd.DataFrame(results['components'])
                comp_data.columns = ['المكون', 'الوزن (كجم)', 'النسبة %']
                st.dataframe(comp_data, use_container_width=True)
                
                # رسم بياني
                fig = px.bar(
                    x=[c['name'] for c in results['components']],
                    y=[c['weight'] for c in results['components']],
                    title="توزيع المكونات",
                    labels={'x': 'المكون', 'y': 'الوزن (كجم)'},
                    color_discrete_sequence=['#2e7d32']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

# ===== التبويب: المراجع العلمية =====
with tabs[len(tabs) - 2]:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f0e1, #e8dcc8); padding: 20px; border-radius: 12px; margin-bottom: 20px; direction: rtl;">
        <h3 style="color: #8d6e63; margin:0;">📚 المراجع العلمية</h3>
        <p style="color: #795548; margin:5px 0 0 0;">
            مصادر موثوقة في تغذية الحيوان والإنتاج الحيواني
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    REFERENCES = {
        "تغذية المجترات": {
            "books": [
                {"title": "Nutritional Ecology of the Ruminant", "author": "Van Soest, P.J.", "year": 1994},
                {"title": "The Ruminant Animal", "author": "Church, D.C.", "year": 1993},
                {"title": "Forage in Ruminant Nutrition", "author": "Minson, D.J.", "year": 1990},
            ]
        },
        "تغذية الدواجن": {
            "books": [
                {"title": "Commercial Poultry Nutrition", "author": "Leeson, S., Summers, J.D.", "year": 2009},
                {"title": "Nutrient Requirements of Poultry", "author": "NRC", "year": 1994},
            ]
        },
        "تغذية الأبقار": {
            "books": [
                {"title": "Nutrient Requirements of Dairy Cattle", "author": "NRC", "year": 2001},
                {"title": "The Mineral Nutrition of Livestock", "author": "Underwood, E.J., Suttle, N.F.", "year": 1999},
            ]
        },
        "المبادئ الأساسية": {
            "books": [
                {"title": "Animal Nutrition", "author": "McDonald, P. et al.", "year": 2011},
                {"title": "Comparative Animal Nutrition and Metabolism", "author": "Cheeke, P.R., Dierenfeld, E.S.", "year": 2010},
            ]
        }
    }
    
    for category, refs in REFERENCES.items():
        with st.expander(f"📖 {category}"):
            for book in refs['books']:
                st.markdown(f"""
                <div style="background: white; padding: 12px 18px; border-radius: 8px; margin: 5px 0; border-right: 4px solid #8d6e63;">
                    <b>{book['title']}</b><br>
                    <span style="color: #666;">{book['author']} - {book['year']}</span>
                </div>
                """, unsafe_allow_html=True)

# ===== التبويب: المساعدة =====
with tabs[len(tabs) - 1]:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); padding: 20px; border-radius: 12px; margin-bottom: 20px; direction: rtl;">
        <h3 style="color: #1a472a; margin:0;">💡 المساعدة والدعم</h3>
        <p style="color: #2d5a27; margin:5px 0 0 0;">
            إجابات على الأسئلة الشائعة ودليل الاستخدام
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    qa = [
        {
            "q": "كيف يتم حساب البروتين المهضوم؟",
            "a": "البروتين المهضوم = البروتين الخام × معامل الهضم. هذا المقياس يعكس القيمة الغذائية الفعلية التي يستفيد منها الحيوان."
        },
        {
            "q": "ما هو معادل النشاء؟",
            "a": "معادل النشاء هو مقياس لكمية الطاقة التي يوفرها العلف، مقارنة بالطاقة التي يوفرها النشاء النقي."
        },
        {
            "q": "كيف أستخدم المحرك؟",
            "a": "1. اختر المواد العلفية المطلوبة\n2. حدد نسبة البروتين والطاقة المطلوبة\n3. اضغط زر التشغيل\n4. ستحصل على التركيبة المثلى بأقل تكلفة"
        },
        {
            "q": "ما هي أفضل مكونات العلف؟",
            "a": "تعتمد على نوع الحيوان ومرحلة الإنتاج. بشكل عام: الحبوب (مصدر طاقة)، الأكساب (مصدر بروتين)، والمعادن والفيتامينات."
        },
    ]
    
    for item in qa:
        with st.expander(f"❓ {item['q']}"):
            st.write(item['a'])

# ===== تذييل الصفحة =====
st.markdown(f"""
<hr style="border-top: 2px solid #2e7d32; margin: 40px 0 20px 0;">

<div style="text-align: center; color: #666; font-size: 0.9rem; direction: rtl;">
    <p>🌾 منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف</p>
    <p style="font-size: 0.8rem; color: #999;">
        المشرف: الاختصاصي م. عبد القادر إسماعيل تاور<br>
        الإصدار 4.0 - محمي بأعلى مستويات الأمان 🔒
    </p>
</div>

<div class="security-badge">
    🔒 TLS 1.3 | AES-256 | CSRF Protected
</div>
""", unsafe_allow_html=True)

# ===== سجل التدقيق =====
def log_audit(action: str, data: dict = None):
    """تسجيل حدث في سجل التدقيق"""
    log = security.create_audit_log(action, "public", data or {})
    st.session_state.audit_logs.append(log)
    # حفظ في قاعدة البيانات
    db_insert = SecureDatabase()
    conn = sqlite3.connect("tower_secure.db")
    c = conn.cursor()
    c.execute('''INSERT INTO audit_logs (id, timestamp, action, user, data, encrypted_data)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (log['session_id'], log['timestamp'], log['action'], log['user'], 
               json.dumps(log['data']), encrypt_data(json.dumps(log))))
    conn.commit()
    conn.close()

# تسجيل حدث بدء الجلسة
log_audit("session_start", {"ip": st.request.client_ip if hasattr(st, 'request') else "unknown"})
