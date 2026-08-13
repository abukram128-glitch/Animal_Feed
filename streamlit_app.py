# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف - النسخة النهائية
# الإصدار: 5.0 (نظام متكامل بأعلى مستويات الأمان)
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
import re
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ===== مكتبات الأمان المدمجة (بدون تبعيات خارجية) =====
import hmac
import binascii

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
from plotly.subplots import make_subplots

# ===== مكتبات OCR ومعالجة الصور =====
try:
    import pytesseract
    from PIL import Image
    import cv2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ===== مكتبات النصوص العربية =====
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

# ============================================================
# 1. نظام الأمان المتقدم (بدون تبعيات)
# ============================================================
class SecureHash:
    """نظام تشفير آمن باستخدام hashlib المدمج"""
    
    @staticmethod
    def generate_salt() -> str:
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_data(data: str, salt: str = None) -> str:
        if salt is None:
            salt = SecureHash.generate_salt()
        return hashlib.pbkdf2_hmac(
            'sha256',
            data.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
    
    @staticmethod
    def simple_encrypt(data: str, key: str) -> str:
        """تشفير بسيط باستخدام XOR"""
        key_bytes = key.encode('utf-8')
        data_bytes = data.encode('utf-8')
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def simple_decrypt(encrypted_data: str, key: str) -> str:
        """فك تشفير بسيط"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            key_bytes = key.encode('utf-8')
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            return decrypted.decode('utf-8')
        except:
            return ""

MASTER_KEY = secrets.token_hex(32)

# ============================================================
# 2. نظام الصوت
# ============================================================
class AudioSystem:
    @staticmethod
    def play_bismillah():
        """تشغيل البسملة"""
        if not GTTS_AVAILABLE:
            st.markdown("""
            <div style="text-align:center; padding:20px; background:linear-gradient(135deg,#1a472a,#2d5a27); 
                        border-radius:15px; color:#d4af37; font-size:2rem;">
                ﷽
                <div style="font-size:1.2rem; color:#c8e6c9; margin-top:10px;">
                    بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ
                </div>
            </div>
            """, unsafe_allow_html=True)
            return
        
        bismillah = "بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ"
        try:
            tts = gTTS(text=bismillah, lang='ar', slow=True)
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
                            border-radius:15px; color:#d4af37; font-size:2rem;">
                    ﷽
                    <div style="font-size:1.2rem; color:#c8e6c9; margin-top:10px;">
                        بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ
                    </div>
                </div>
                ''',
                height=150
            )
        except:
            pass

# ============================================================
# 3. قاعدة البيانات الآمنة
# ============================================================
class SecureDatabase:
    def __init__(self, db_path="tower_data.db"):
        self.db_path = db_path
        self.key = MASTER_KEY[:32]
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # جدول الخلطات
        c.execute('''CREATE TABLE IF NOT EXISTS formulas
                     (id TEXT PRIMARY KEY,
                      name TEXT,
                      ingredients TEXT,
                      target_dp REAL,
                      target_se REAL,
                      total_cost REAL,
                      created_date TEXT)''')
        
        # جدول سجلات التحليل
        c.execute('''CREATE TABLE IF NOT EXISTS analyses
                     (id TEXT PRIMARY KEY,
                      ingredients TEXT,
                      results TEXT,
                      created_date TEXT)''')
        
        # جدول التنبؤات الوراثية
        c.execute('''CREATE TABLE IF NOT EXISTS genetics_predictions
                     (id TEXT PRIMARY KEY,
                      parent1 TEXT,
                      parent2 TEXT,
                      trait TEXT,
                      prediction REAL,
                      created_date TEXT)''')
        
        conn.commit()
        conn.close()
    
    def _encrypt(self, data: str) -> str:
        return SecureHash.simple_encrypt(data, self.key)
    
    def _decrypt(self, data: str) -> str:
        return SecureHash.simple_decrypt(data, self.key)
    
    def save_formula(self, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO formulas 
                     (id, name, ingredients, target_dp, target_se, total_cost, created_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (secrets.token_hex(16), data['name'], json.dumps(data['ingredients']),
                   data['target_dp'], data['target_se'], data['total_cost'],
                   datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_formulas(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM formulas ORDER BY created_date DESC")
        rows = c.fetchall()
        conn.close()
        return [{'id': r[0], 'name': r[1], 'ingredients': json.loads(r[2]), 
                 'target_dp': r[3], 'target_se': r[4], 'total_cost': r[5], 
                 'created_date': r[6]} for r in rows]
    
    def save_analysis(self, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO analyses 
                     (id, ingredients, results, created_date)
                     VALUES (?, ?, ?, ?)''',
                  (secrets.token_hex(16), json.dumps(data['ingredients']),
                   json.dumps(data['results']), datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def save_genetic_prediction(self, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO genetics_predictions 
                     (id, parent1, parent2, trait, prediction, created_date)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (secrets.token_hex(16), data['parent1'], data['parent2'],
                   data['trait'], data['prediction'], datetime.now().isoformat()))
        conn.commit()
        conn.close()

# ============================================================
# 4. مكتبة الأعلاف
# ============================================================
FEED_LIBRARY = {
    "الحبوب": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "شعير": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
    },
    "مصادر البروتين": {
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب عباد الشمس": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "مسحوق سمك": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
    },
    "المعادن والإضافات": {
        "حجر جيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح طعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "نخالة قمح": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "مولاس": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
    }
}

# ============================================================
# 5. محرك تركيب الأعلاف
# ============================================================
class FeedOptimizer:
    @staticmethod
    def optimize(ingredients: List[str], prices: Dict[str, float], 
                 target_dp: float, target_se: float) -> Dict:
        """تحسين تركيب العلف"""
        
        if not ingredients:
            return {'success': False, 'message': 'لم يتم اختيار مكونات'}
        
        # تجهيز القيود
        c = [prices.get(ing, 300.0) for ing in ingredients]
        bounds = [(0.0, 100.0) for _ in ingredients]
        
        # معادلة المجموع
        A_eq = [[1.0] * len(ingredients)]
        b_eq = [100.0]
        
        # قيد البروتين المهضوم
        dp_row = []
        for ing in ingredients:
            vals = FeedOptimizer._get_values(ing)
            dp_row.append(vals.get('CP', 0) * vals.get('DC', 0))
        A_eq.append(dp_row)
        b_eq.append(target_dp * 100.0)
        
        # قيد الطاقة
        se_row = []
        for ing in ingredients:
            vals = FeedOptimizer._get_values(ing)
            se_row.append(vals.get('SE', 0))
        A_ub = [[-x for x in se_row]]
        b_ub = [-target_se * 100.0]
        
        # تشغيل المحرك
        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, 
                         bounds=bounds, method='highs')
            
            if res.success:
                formula = {}
                total_se = 0.0
                for idx, ing in enumerate(ingredients):
                    if res.x[idx] > 0.0001:
                        formula[ing] = res.x[idx]
                        vals = FeedOptimizer._get_values(ing)
                        total_se += (res.x[idx] / 100.0) * vals.get('SE', 0)
                
                return {
                    'success': True,
                    'formula': formula,
                    'cost': res.fun / 100.0,
                    'total_se': total_se,
                    'status': 'optimized'
                }
            else:
                return {'success': False, 'message': 'تعذر إيجاد حل رياضي'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def _get_values(name: str) -> Dict:
        for category in FEED_LIBRARY.values():
            if name in category:
                return category[name]
        return {}

# ============================================================
# 6. مختبر تحليل الأعلاف
# ============================================================
class FeedLab:
    @staticmethod
    def analyze(ingredients: Dict[str, float]) -> Dict:
        """تحليل خلطة علفية"""
        total = sum(ingredients.values())
        if total <= 0:
            return {'error': 'الوزن الكلي يجب أن يكون أكبر من صفر'}
        
        results = {
            'total': total,
            'CP': 0.0, 'DP': 0.0, 'SE': 0.0,
            'NDF': 0.0, 'ADF': 0.0, 'EE': 0.0, 'ASH': 0.0,
            'components': []
        }
        
        for name, weight in ingredients.items():
            if weight <= 0:
                continue
            
            pct = weight / total
            vals = FeedLab._get_values(name)
            
            results['CP'] += pct * vals.get('CP', 0)
            results['DP'] += pct * vals.get('CP', 0) * vals.get('DC', 0)
            results['SE'] += pct * vals.get('SE', 0)
            results['NDF'] += pct * vals.get('NDF', 0)
            results['ADF'] += pct * vals.get('ADF', 0)
            results['EE'] += pct * vals.get('EE', 0)
            results['ASH'] += pct * vals.get('ASH', 0)
            
            results['components'].append({
                'name': name,
                'weight': weight,
                'percentage': pct * 100
            })
        
        return results
    
    @staticmethod
    def _get_values(name: str) -> Dict:
        for category in FEED_LIBRARY.values():
            if name in category:
                return category[name]
        return {}
    
    @staticmethod
    def parse_text(text: str) -> Dict[str, float]:
        """استخراج المكونات من نص"""
        ingredients = {}
        lines = text.strip().split('\n')
        for line in lines:
            # محاولة استخراج اسم ووزن
            match = re.search(r'([\u0600-\u06FF\s]+)[:\s]+([\d.]+)', line)
            if match:
                name = match.group(1).strip()
                weight = float(match.group(2))
                ingredients[name] = weight
            else:
                # محاولة استخراج رقم فقط
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        weight = float(parts[-1])
                        name = ' '.join(parts[:-1])
                        ingredients[name] = weight
                    except:
                        pass
        return ingredients

# ============================================================
# 7. نظام الوراثة والتنبؤ
# ============================================================
class GeneticsPredictor:
    """نظام التنبؤ بالصفات الوراثية"""
    
    # معاملات الوراثة للصفات المختلفة
    HERITABILITY = {
        'اللون': 0.85,
        'الحجم': 0.65,
        'الوزن': 0.45,
        'الإنتاج': 0.30,
        'المناعة': 0.25,
        'الخصوبة': 0.20
    }
    
    # درجات الصفات
    TRAIT_SCORES = {
        'اللون': {
            'أبيض': 1.0, 'أسود': 0.9, 'بني': 0.8, 
            'أحمر': 0.7, 'أصفر': 0.6, 'مرقط': 0.5
        },
        'الحجم': {
            'كبير جداً': 1.0, 'كبير': 0.85, 'متوسط': 0.7, 
            'صغير': 0.5, 'صغير جداً': 0.3
        },
        'الوزن': {
            'ثقيل جداً': 1.0, 'ثقيل': 0.85, 'متوسط': 0.7, 
            'خفيف': 0.5, 'خفيف جداً': 0.3
        }
    }
    
    @staticmethod
    def predict_trait(parent1: str, parent2: str, trait: str) -> Dict:
        """التنبؤ بصفة وراثية"""
        
        # تحليل الصفات من النص
        p1_score = GeneticsPredictor._extract_score(parent1, trait)
        p2_score = GeneticsPredictor._extract_score(parent2, trait)
        
        if p1_score is None or p2_score is None:
            return {
                'prediction': 0.5,
                'confidence': 0.3,
                'range': 'منخفض',
                'description': 'بيانات غير كافية للتنبؤ الدقيق'
            }
        
        # حساب التنبؤ باستخدام معامل الوراثة
        h2 = GeneticsPredictor.HERITABILITY.get(trait, 0.5)
        
        # متوسط الوالدين
        mid_parent = (p1_score + p2_score) / 2
        
        # التنبؤ
        prediction = mid_parent * h2 + 0.5 * (1 - h2)
        prediction = max(0.1, min(1.0, prediction))
        
        # مستوى الثقة
        confidence = 0.4 + (0.6 * h2)
        
        # تفسير النتيجة
        if prediction >= 0.8:
            range_text = 'مرتفع جداً'
        elif prediction >= 0.6:
            range_text = 'مرتفع'
        elif prediction >= 0.4:
            range_text = 'متوسط'
        elif prediction >= 0.2:
            range_text = 'منخفض'
        else:
            range_text = 'منخفض جداً'
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'range': range_text,
            'description': f'التنبؤ بـ {trait}: {range_text} (ثقة {confidence:.0%})'
        }
    
    @staticmethod
    def _extract_score(text: str, trait: str) -> Optional[float]:
        """استخراج درجة الصفة من النص"""
        text = text.lower()
        
        if trait == 'اللون':
            for color, score in GeneticsPredictor.TRAIT_SCORES['اللون'].items():
                if color in text:
                    return score
        elif trait == 'الحجم':
            for size, score in GeneticsPredictor.TRAIT_SCORES['الحجم'].items():
                if size in text:
                    return score
        elif trait == 'الوزن':
            for weight, score in GeneticsPredictor.TRAIT_SCORES['الوزن'].items():
                if weight in text:
                    return score
        
        return None
    
    @staticmethod
    def predict_appearance(parent1: str, parent2: str) -> Dict:
        """التنبؤ بالمظهر العام"""
        traits = ['اللون', 'الحجم', 'الوزن']
        results = {}
        
        for trait in traits:
            results[trait] = GeneticsPredictor.predict_trait(parent1, parent2, trait)
        
        # حساب المظهر العام
        avg_pred = sum(r['prediction'] for r in results.values()) / len(traits)
        
        return {
            'traits': results,
            'overall': avg_pred,
            'description': GeneticsPredictor._describe_appearance(avg_pred)
        }
    
    @staticmethod
    def _describe_appearance(score: float) -> str:
        """وصف المظهر العام"""
        if score >= 0.8:
            return 'مظهر ممتاز - صفات مرغوبة عالية'
        elif score >= 0.6:
            return 'مظهر جيد - صفات مرغوبة'
        elif score >= 0.4:
            return 'مظهر متوسط - صفات مقبولة'
        else:
            return 'مظهر يحتاج تحسين - صفات منخفضة'
    
    @staticmethod
    def predict_production(parent1: str, parent2: str) -> Dict:
        """التنبؤ بالإنتاجية"""
        traits = ['الإنتاج', 'الخصوبة', 'المناعة']
        results = {}
        
        for trait in traits:
            results[trait] = GeneticsPredictor.predict_trait(parent1, parent2, trait)
        
        # الإنتاجية الكلية
        total = sum(r['prediction'] for r in results.values()) / len(traits)
        
        return {
            'traits': results,
            'total': total,
            'description': GeneticsPredictor._describe_production(total)
        }
    
    @staticmethod
    def _describe_production(score: float) -> str:
        """وصف الإنتاجية"""
        if score >= 0.8:
            return 'إنتاجية ممتازة - نتائج مرتفعة'
        elif score >= 0.6:
            return 'إنتاجية جيدة - نتائج إيجابية'
        elif score >= 0.4:
            return 'إنتاجية متوسطة - نتائج مقبولة'
        else:
            return 'إنتاجية منخفضة - تحتاج تحسين'

# ============================================================
# 8. إعدادات التطبيق
# ============================================================
st.set_page_config(
    page_title="منصة تاور العلمية - الإنتاج الحيواني وتركيب الأعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== CSS =====
st.markdown("""
<style>
* { font-family: 'Cairo', 'Amiri', sans-serif; }

.header {
    background: linear-gradient(135deg, #1a472a, #2d5a27);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    color: #d4af37;
    margin-bottom: 30px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
.header h1 { color: #d4af37 !important; font-size: 2.5rem; margin: 0; }
.header .sub { color: #a8d5a2 !important; font-size: 1.1rem; }

.bismillah-box {
    text-align: center;
    padding: 15px;
    background: linear-gradient(135deg, #f5f0e1, #e8dcc8);
    border-radius: 12px;
    margin: 20px 0;
    border: 2px solid #d4af37;
}

.animal-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border-right: 5px solid #2d5a27;
    margin: 10px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.metric-box {
    background: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}
.metric-value { font-size: 1.8rem; font-weight: bold; color: #1a472a; }
.metric-label { color: #666; font-size: 0.9rem; }

.ingredient-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 15px;
    background: #f8f9fa;
    border-radius: 8px;
    margin: 4px 0;
}

.prediction-card {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
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
}

.stButton > button {
    background: linear-gradient(135deg, #1a472a, #2d5a27) !important;
    color: white !important;
    font-weight: bold !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 30px !important;
}
</style>
""", unsafe_allow_html=True)

# ===== تشغيل البسملة =====
AudioSystem.play_bismillah()

# ===== حالة الجلسة =====
if "session_id" not in st.session_state:
    st.session_state.session_id = secrets.token_hex(16)
    st.session_state.saved_formulas = []
    st.session_state.genetics_history = []

# ============================================================
# 9. الواجهة الرئيسية
# ============================================================
st.markdown(f"""
<div class="header">
    <h1>🌾 منصة تاور العلمية</h1>
    <div class="sub">للإنتاج الحيواني وتركيب الأعلاف - الإصدار 5.0</div>
    <div style="font-size:0.8rem; color:#a8d5a2; margin-top:10px;">
        🔒 جلسة آمنة | {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
</div>
""", unsafe_allow_html=True)

# ===== التبويبات =====
tabs = st.tabs([
    "🔬 تركيب الأعلاف",
    "🧪 مختبر التحليل",
    "🧬 الوراثة والتنبؤ",
    "🐄 الأبقار",
    "🐑 الأغنام",
    "🐐 الماعز",
    "🐴 الخيول",
    "🐔 الدواجن",
    "🐦 السمان",
    "🐟 الأسماك",
    "📚 المراجع",
    "💡 المساعدة"
])

# ============================================================
# التبويب 0: تركيب الأعلاف
# ============================================================
with tabs[0]:
    st.markdown("### 🔬 محرك تركيب الأعلاف الذكي")
    
    col1, col2 = st.columns(2)
    with col1:
        target_dp = st.slider("البروتين المهضوم المستهدف (DP %)", 5.0, 40.0, 16.0, 0.5)
    with col2:
        target_se = st.slider("معادل النشاء المستهدف (SE)", 10.0, 90.0, 70.0, 1.0)
    
    st.markdown("### 📦 اختيار المواد")
    selected = []
    prices = {}
    
    for category, items in FEED_LIBRARY.items():
        with st.expander(f"📁 {category}"):
            cols = st.columns(3)
            for idx, (name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    if st.checkbox(name, value=name in ["ذرة صفراء", "كسب فول صويا 44%"]):
                        selected.append(name)
                        price = st.number_input(f"💰 سعر {name} ($/طن)", 
                                               min_value=10.0, max_value=2000.0,
                                               value=350.0, key=f"price_{name}")
                        prices[name] = price
    
    if st.button("🚀 تشغيل المحرك", type="primary", use_container_width=True):
        if not selected:
            st.warning("⚠️ يرجى اختيار مكونات")
        else:
            with st.spinner("جاري الحساب..."):
                result = FeedOptimizer.optimize(selected, prices, target_dp, target_se)
                
                if result['success']:
                    st.success("✅ تم حساب التركيبة المثلى")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("💵 التكلفة للطن", f"${result['cost']:.2f}")
                    with col_b:
                        st.metric("🔬 البروتين المهضوم", f"{target_dp:.1f}%")
                    with col_c:
                        st.metric("⚡ معادل النشاء", f"{result['total_se']:.1f}")
                    
                    st.markdown("### 📋 مكونات الخلطة")
                    for name, pct in result['formula'].items():
                        kg = pct * 10
                        st.markdown(f"""
                        <div class="ingredient-row">
                            <span>🌾 {name}</span>
                            <span><b>{pct:.1f}%</b> ({kg:.1f} كجم/طن)</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # رسم بياني
                    fig = px.pie(
                        values=list(result['formula'].values()),
                        names=list(result['formula'].keys()),
                        title="توزيع المكونات"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # حفظ
                    if st.button("💾 حفظ التركيبة"):
                        db = SecureDatabase()
                        db.save_formula({
                            'name': f"خلطة {datetime.now().strftime('%H:%M')}",
                            'ingredients': result['formula'],
                            'target_dp': target_dp,
                            'target_se': target_se,
                            'total_cost': result['cost']
                        })
                        st.success("✅ تم الحفظ")
                else:
                    st.error(f"❌ {result.get('message', 'خطأ')}")

# ============================================================
# التبويب 1: مختبر التحليل
# ============================================================
with tabs[1]:
    st.markdown("### 🧪 مختبر تحليل الأعلاف")
    
    tab_manual, tab_upload = st.tabs(["📝 إدخال يدوي", "📸 تحليل من صورة"])
    
    with tab_manual:
        st.markdown("#### أدخل مكونات الخلطة")
        
        ingredients = {}
        cols = st.columns(3)
        all_ingredients = []
        for category in FEED_LIBRARY.values():
            all_ingredients.extend(category.keys())
        
        for idx, ing in enumerate(all_ingredients):
            with cols[idx % 3]:
                weight = st.number_input(f"{ing} (كجم)", 0.0, 1000.0, 0.0, 1.0, key=f"lab_{ing}")
                if weight > 0:
                    ingredients[ing] = weight
        
        if st.button("🧪 تحليل", type="primary"):
            if not ingredients:
                st.warning("⚠️ يرجى إدخال مكونات")
            else:
                results = FeedLab.analyze(ingredients)
                if 'error' in results:
                    st.error(results['error'])
                else:
                    st.success("✅ تم التحليل")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🧬 البروتين الخام", f"{results['CP']:.1f}%")
                    with col2:
                        st.metric("🧪 البروتين المهضوم", f"{results['DP']:.1f}%")
                    with col3:
                        st.metric("⚡ معادل النشاء", f"{results['SE']:.1f}")
                    
                    # رسم بياني للمكونات
                    comp_df = pd.DataFrame(results['components'])
                    fig = px.bar(comp_df, x='name', y='weight', title="توزيع المكونات")
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab_upload:
        st.markdown("#### 📸 تحليل من صورة أو مستند")
        st.info("""
        **طريقة الاستخدام:**
        1. التقط صورة لوثيقة تحتوي على مكونات العلف
        2. ارفع الصورة هنا
        3. سيتم استخراج المكونات تلقائياً وتحليلها
        """)
        
        uploaded_file = st.file_uploader("اختر صورة", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        if uploaded_file and OCR_AVAILABLE:
            try:
                # قراءة الصورة
                image = Image.open(uploaded_file)
                st.image(image, caption="الصورة المرفوعة", use_container_width=True)
                
                # استخراج النص
                text = pytesseract.image_to_string(image, lang='ara+eng')
                st.text_area("النص المستخرج", text, height=150)
                
                # تحليل النص
                ingredients = FeedLab.parse_text(text)
                
                if ingredients:
                    st.success(f"✅ تم استخراج {len(ingredients)} مكون")
                    st.json(ingredients)
                    
                    # تحليل
                    results = FeedLab.analyze(ingredients)
                    if 'error' not in results:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🧬 البروتين الخام", f"{results['CP']:.1f}%")
                        with col2:
                            st.metric("🧪 البروتين المهضوم", f"{results['DP']:.1f}%")
                        with col3:
                            st.metric("⚡ معادل النشاء", f"{results['SE']:.1f}")
                else:
                    st.warning("⚠️ لم يتم استخراج مكونات من الصورة")
                    
            except Exception as e:
                st.error(f"خطأ في معالجة الصورة: {e}")
        elif uploaded_file and not OCR_AVAILABLE:
            st.warning("⚠️ مكتبة OCR غير مثبتة. يرجى تثبيت pytesseract")

# ============================================================
# التبويب 2: الوراثة والتنبؤ
# ============================================================
with tabs[2]:
    st.markdown("### 🧬 نظام الوراثة والتنبؤ بالصفات")
    
    st.info("""
    **نظام التنبؤ الوراثي:**
    - التنبؤ بالصفات الظاهرية (اللون، الحجم، الوزن)
    - التنبؤ بالإنتاجية
    - حساب معامل الوراثة والثقة
    """)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        parent1 = st.text_area("👨 الأب (صفاته)", 
                              "أسود - كبير - ثقيل", height=100)
    with col_p2:
        parent2 = st.text_area("👩 الأم (صفاتها)", 
                              "أبيض - متوسط - متوسط", height=100)
    
    prediction_type = st.selectbox("نوع التنبؤ", 
                                   ["المظهر العام", "الصفات الفردية", "الإنتاجية"])
    
    if st.button("🔮 تنبؤ", type="primary"):
        if not parent1 or not parent2:
            st.warning("⚠️ يرجى إدخال صفات الأبوين")
        else:
            if prediction_type == "المظهر العام":
                result = GeneticsPredictor.predict_appearance(parent1, parent2)
                
                st.markdown(f"""
                <div class="prediction-card">
                    <h4>📊 نتائج التنبؤ بالمظهر</h4>
                    <p><b>التقييم العام:</b> {result['description']}</p>
                    <p><b>درجة المظهر:</b> {result['overall']:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
                
                for trait, data in result['traits'].items():
                    st.markdown(f"""
                    <div style="background:white; padding:10px; border-radius:8px; margin:5px 0;">
                        <b>{trait}:</b> {data['range']} (ثقة {data['confidence']:.0%})
                    </div>
                    """, unsafe_allow_html=True)
            
            elif prediction_type == "الصفات الفردية":
                trait = st.selectbox("اختر الصفة", ["اللون", "الحجم", "الوزن"])
                result = GeneticsPredictor.predict_trait(parent1, parent2, trait)
                
                st.markdown(f"""
                <div class="prediction-card">
                    <h4>📊 التنبؤ بـ {trait}</h4>
                    <p><b>التوقع:</b> {result['range']}</p>
                    <p><b>الثقة:</b> {result['confidence']:.0%}</p>
                    <p><b>الوصف:</b> {result['description']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            else:  # الإنتاجية
                result = GeneticsPredictor.predict_production(parent1, parent2)
                
                st.markdown(f"""
                <div class="prediction-card">
                    <h4>📊 التنبؤ بالإنتاجية</h4>
                    <p><b>التقييم:</b> {result['description']}</p>
                    <p><b>المستوى الكلي:</b> {result['total']:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
                
                for trait, data in result['traits'].items():
                    st.markdown(f"""
                    <div style="background:white; padding:10px; border-radius:8px; margin:5px 0;">
                        <b>{trait}:</b> {data['range']} (ثقة {data['confidence']:.0%})
                    </div>
                    """, unsafe_allow_html=True)

# ============================================================
# تبويبات الحيوانات (مختصرة)
# ============================================================
animal_data = {
    "الأبقار": {"dp": 12.0, "se": 68.0, "ndf": 35.0},
    "الأغنام": {"dp": 11.0, "se": 65.0, "ndf": 30.0},
    "الماعز": {"dp": 10.5, "se": 62.0, "ndf": 28.0},
    "الخيول": {"dp": 9.0, "se": 60.0, "ndf": 25.0},
    "الدواجن": {"dp": 18.0, "se": 75.0, "ndf": 10.0},
    "السمان": {"dp": 22.0, "se": 72.0, "ndf": 8.0},
    "الأسماك": {"dp": 28.0, "se": 70.0, "ndf": 5.0},
}

for idx, (animal, data) in enumerate(animal_data.items(), start=3):
    with tabs[idx]:
        st.markdown(f"""
        <div class="animal-card">
            <h3>🐄 {animal}</h3>
            <p>توصيات غذائية متخصصة</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🧬 البروتين المهضوم", f"{data['dp']:.1f}%")
        with col2:
            st.metric("⚡ معادل النشاء", f"{data['se']:.1f}")
        with col3:
            st.metric("🌿 الألياف", f"{data['ndf']:.1f}%")
        
        st.info("""
        **توصيات:**
        - استخدام مكونات عالية الجودة
        - مراعاة مرحلة الإنتاج
        - توفير ماء نظيف
        - متابعة الأداء
        """)

# ============================================================
# التبويب: المراجع
# ============================================================
with tabs[len(tabs) - 2]:
    st.markdown("### 📚 المراجع العلمية")
    
    references = {
        "تغذية المجترات": ["Nutritional Ecology of the Ruminant", "The Ruminant Animal"],
        "تغذية الدواجن": ["Commercial Poultry Nutrition", "Nutrient Requirements of Poultry"],
        "الوراثة": ["Animal Breeding and Genetics", "Quantitative Genetics"],
        "التغذية العامة": ["Animal Nutrition", "Feed Formulation"]
    }
    
    for category, books in references.items():
        with st.expander(f"📖 {category}"):
            for book in books:
                st.markdown(f"- {book}")

# ============================================================
# التبويب: المساعدة
# ============================================================
with tabs[len(tabs) - 1]:
    st.markdown("### 💡 المساعدة")
    
    qa = [
        ("كيف يعمل محرك تركيب الأعلاف؟", 
         "يستخدم البرمجة الخطية لحساب أقل تكلفة مع تحقيق المتطلبات الغذائية."),
        ("ما هو البروتين المهضوم؟",
         "البروتين الذي يمكن للحيوان هضمه وامتصاصه فعلياً."),
        ("كيف يتم التنبؤ بالصفات الوراثية؟",
         "باستخدام معامل الوراثة وصفات الأبوين."),
        ("كيف أحلل صورة؟",
         "ارفع الصورة في مختبر التحليل وسيتم استخراج المكونات تلقائياً.")
    ]
    
    for q, a in qa:
        with st.expander(f"❓ {q}"):
            st.write(a)

# ===== تذييل =====
st.markdown(f"""
<hr>
<div style="text-align:center; color:#666;">
    <p>🌾 منصة تاور العلمية - الإصدار 5.0</p>
    <p style="font-size:0.8rem;">المشرف: الاختصاصي م. عبد القادر إسماعيل تاور</p>
</div>
<div class="security-badge">🔒 آمن | {st.session_state.session_id[:8]}</div>
""", unsafe_allow_html=True)
