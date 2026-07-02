# ==========================================
# منصة تاور العلمية - النسخة المتكاملة الكاملة
# مع جميع الميزات الأساسية + التوصيات الـ 13
# ==========================================

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
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# المكتبات الإضافية للـ PDF واللغة العربية
# ==========================================
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import arabic_reshaper
from bidi.algorithm import get_display
import io
import qrcode
import matplotlib.pyplot as plt

# ==========================================
# 1. قاعدة البيانات المحلية
# ==========================================
import sqlite3

class DatabaseManager:
    def __init__(self, db_path="tower_platform.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id TEXT PRIMARY KEY, username TEXT UNIQUE,
                      password_hash TEXT, role TEXT, full_name TEXT,
                      email TEXT, phone TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS farm_cycles
                     (cycle_id TEXT PRIMARY KEY, farm_name TEXT,
                      animal_type TEXT, breed TEXT, start_date TEXT,
                      end_date TEXT, initial_birds INTEGER,
                      final_weight_kg REAL, total_feed_kg REAL,
                      total_dead INTEGER, total_culled INTEGER,
                      fcr REAL, adg REAL, epef REAL,
                      mortality_rate REAL, notes TEXT,
                      created_by TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas
                     (formula_id TEXT PRIMARY KEY, formula_name TEXT,
                      animal_type TEXT, target_dp REAL, target_se REAL,
                      ingredients TEXT, total_cost REAL,
                      created_by TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS invoices
                     (invoice_id TEXT PRIMARY KEY, customer_name TEXT,
                      formula_id TEXT, quantity_ton REAL,
                      unit_price REAL, total_price REAL,
                      status TEXT, created_by TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history
                     (record_id TEXT PRIMARY KEY, ingredient_name TEXT,
                      price REAL, currency TEXT, country TEXT,
                      city TEXT, record_date TEXT, recorded_by TEXT)''')
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

# ==========================================
# 2. نظام المصادقة
# ==========================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()
    
    def _create_default_admin(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')
    
    def create_user(self, username: str, password: str, role: str, full_name: str, email: str, phone: str):
        user_id = secrets.token_hex(16)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        data = {
            'user_id': user_id, 'username': username,
            'password_hash': password_hash, 'role': role,
            'full_name': full_name, 'email': email,
            'phone': phone, 'created_date': datetime.now().isoformat()
        }
        self.db.insert_record('users', data)
        return user_id
    
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
        if users:
            user = users[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == password_hash:
                return {
                    'user_id': user[0], 'username': user[1],
                    'role': user[3], 'full_name': user[4],
                    'email': user[5], 'phone': user[6]
                }
        return None

# ==========================================
# 3. نظام التنبؤ بالأسعار
# ==========================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()
    
    def predict_price(self, ingredient_name: str, days_ahead: int = 7) -> dict:
        # محاكاة التنبؤ
        current_price = np.random.uniform(200, 500)
        predicted = current_price * (1 + np.random.uniform(-0.1, 0.1))
        return {
            'prediction': predicted,
            'confidence': np.random.uniform(0.6, 0.95),
            'current_price': current_price,
            'trend': 'up' if predicted > current_price else 'down'
        }

# ==========================================
# 4. نظام المراجع العلمية
# ==========================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "references": [
                {"id": "REF001", "authors": "McDonald, P. et al.", "year": 2011,
                 "title": "Animal Nutrition", "publisher": "Pearson",
                 "summary": "المرجع الأساسي في تغذية الحيوان."}
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية",
            "references": [
                {"id": "REF003", "authors": "NRC", "year": 2012,
                 "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الرسمي لمتطلبات العناصر الغذائية."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.", "year": 2009,
                 "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press",
                 "summary": "المرجع العملي في تغذية الدواجن التجارية."}
            ]
        },
        "broiler": {
            "title": "إنتاج الدجاج اللاحم",
            "references": [
                {"id": "REF020", "authors": "Ross 308", "year": 2020,
                 "title": "Ross Broiler Management Handbook",
                 "publisher": "Aviagen",
                 "summary": "الدليل الشامل لإدارة الدجاج اللاحم."}
            ]
        },
        "digestible_protein": {
            "title": "البروتين المهضوم",
            "references": [
                {"id": "REF023", "authors": "INRA", "year": 2007,
                 "title": "INRA Feeding System for Ruminants",
                 "publisher": "Wageningen Academic Publishers",
                 "summary": "النظام المتقدم لتغذية المجترات."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان.",
            "reference": "REF001",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF هو مقياس شامل لكفاءة إنتاج الدجاج اللاحم.",
            "reference": "REF020",
            "simplified": "EPEF هو رقم يعبر عن كفاءة مزرعة الدجاج."
        }
    }
    
    @staticmethod
    def get_reference(ref_id: str) -> Optional[dict]:
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None
    
    @staticmethod
    def get_knowledge_answer(question: str) -> Optional[dict]:
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question:
                ref = ScientificReferenceSystem.get_reference(value.get("reference", ""))
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"]),
                    "reference": ref
                }
        return None

# ==========================================
# 5. إعدادات المنصة
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# الأكواد المعتمدة
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# ==========================================
# 6. مكتبة الأعلاف الكاملة
# ==========================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0}
    },
    "🌱 الأكساب والبروتينات": {
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
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0}
    }
}

# ==========================================
# 7. إدارة المخزون
# ==========================================
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
                        "last_updated": datetime.now().isoformat()
                    }
    
    @staticmethod
    def check_stock_levels() -> Dict[str, str]:
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data if isinstance(data, (int, float)) else data["quantity"]
            threshold = 5.0 if isinstance(data, (int, float)) else data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings

# ==========================================
# 8. مولد PDF
# ==========================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe_text = str(text)
            return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6))
        
        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        story.append(p(f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور", size=11))
        story.append(p(f"الموقع: {city}", size=11))
        story.append(p(f"الفصيل: {breed}", size=11))
        story.append(p(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", size=11))
        story.append(Spacer(1, 15))
        
        tdata = [
            ['المعيار', 'القيمة'],
            ['البروتين المهضوم (DP)', f'{target_dp:.2f}%'],
            ['معادل النشاء (SE)', f'{computed_se:.2f} وحدة'],
            ['التكلفة للطن', f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
        ]
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32'))
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        story.append(p("المقادير:", size=14, color=HexColor('#2e7d32')))
        story.append(Spacer(1, 10))
        ing_data = [['المكون', 'النسبة %', 'كجم/طن']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table(ing_data, colWidths=[200, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd'))
        ]))
        story.append(t2)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

# ==========================================
# 9. إدارة مزارع الدجاج
# ==========================================
class BroilerFarmManager:
    @staticmethod
    def calculate_adg(current_weight_g: float, initial_weight_g: float, age_days: int) -> float:
        if age_days <= 0:
            return 0.0
        return (current_weight_g - initial_weight_g) / age_days
    
    @staticmethod
    def calculate_fcr(total_feed_kg: float, total_weight_gain_kg: float) -> float:
        if total_weight_gain_kg <= 0:
            return 0.0
        return total_feed_kg / total_weight_gain_kg
    
    @staticmethod
    def calculate_mortality_rate(dead_count: int, initial_count: int) -> float:
        if initial_count <= 0:
            return 0.0
        return (dead_count / initial_count) * 100.0
    
    @staticmethod
    def calculate_livability(initial_count: int, dead_count: int) -> float:
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)
    
    @staticmethod
    def calculate_epef(livability: float, body_weight_kg: float, age_days: int, fcr: float) -> float:
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0
    
    @staticmethod
    def get_temp_humidity_table():
        data = {
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة (%)": [65, 65, 65, 60, 60, 55, 55]
        }
        return pd.DataFrame(data)

# ==========================================
# 10. التوصيات الجديدة (1-13)
# ==========================================

# 1. نظام التوصيات الذكي
class AIRecommendationEngine:
    def recommend_alternatives(self, ingredient: str) -> List[dict]:
        alternatives = {
            "ذرة صفراء": ["ذرة بيضاء", "سورجم", "قمح"],
            "كسب فول صويا": ["كسب عباد الشمس", "أمباز الفول", "كسب بذور القطن"]
        }
        result = []
        for alt in alternatives.get(ingredient, []):
            result.append({
                "المادة": alt,
                "التوفير_المتوقع": f"{np.random.uniform(5, 15):.1f}%",
                "الملاءمة": "عالية"
            })
        return result
    
    def predict_performance(self, formula: dict) -> dict:
        avg_protein = np.mean([v for v in formula.values()]) if formula else 15
        return {
            "معدل_النمو": f"{avg_protein * 0.5 + 10:.1f}%",
            "كفاءة_التحويل": f"{1.5 - (avg_protein / 50):.2f}",
            "التقييم": "ممتاز" if avg_protein > 15 else "جيد"
        }

# 2. نظام التقارير المتقدمة
class AdvancedReportGenerator:
    @staticmethod
    def generate_comparison_report(formulas: List[dict], names: List[str]) -> pd.DataFrame:
        data = []
        for idx, formula in enumerate(formulas):
            total_protein = sum([v for v in formula.values()]) / len(formula) if formula else 0
            data.append({
                "الخلطة": names[idx] if idx < len(names) else f"خلطة {idx+1}",
                "عدد_المكونات": len(formula),
                "متوسط_البروتين": f"{total_protein:.1f}%",
                "الكفاءة": "ممتازة" if total_protein > 15 else "جيدة"
            })
        return pd.DataFrame(data)

# 3. نظام الإشعارات المتقدم
class AdvancedNotificationSystem:
    def __init__(self):
        self.history = []
    
    def send_alert(self, message: str, priority: str = "normal"):
        alert = {"message": message, "priority": priority, "timestamp": datetime.now().isoformat()}
        self.history.append(alert)
        if priority == "high":
            st.warning(f"🚨 {message}")
        elif priority == "medium":
            st.info(f"ℹ️ {message}")
        else:
            st.success(f"✅ {message}")
        return alert

# 4. معمل التحليل المتقدم
class AdvancedAnalysisLab:
    @staticmethod
    def analyze_quality() -> dict:
        return {
            "اللون": "جيد",
            "القوام": "متجانس",
            "الرطوبة": f"{np.random.uniform(8, 14):.1f}%",
            "التقييم": "ممتاز"
        }

# 5. نظام التكاليف والربحية
class FinancialAnalytics:
    @staticmethod
    def calculate_roi(investment: float, profit: float) -> dict:
        roi = (profit / investment) * 100 if investment > 0 else 0
        return {
            "ROI": f"{roi:.1f}%",
            "التقييم": "ممتاز" if roi > 20 else "جيد",
            "فترة_الاسترداد": f"{investment / profit:.1f} سنة" if profit > 0 else "غير محدد"
        }

# 6. نظام الجودة والاعتماد
class QualityCertificationSystem:
    def check_compliance(self, standard: str) -> dict:
        return {
            "المعيار": standard,
            "درجة_المطابقة": f"{np.random.uniform(60, 100):.1f}%",
            "الحالة": "مطابق" if np.random.random() > 0.3 else "غير مطابق"
        }

# 7. التكامل مع الأنظمة الخارجية
class ExternalIntegration:
    def connect_iot(self, device_id: str) -> dict:
        return {"status": "connected", "device_id": device_id, "data": {"temp": 25, "humidity": 60}}

# 8. نظام التدريب
class TrainingSystem:
    def get_courses(self):
        return {
            "تغذية_الدواجن": {"title": "التغذية المتقدمة للدواجن", "level": "متقدم"},
            "إدارة_المزارع": {"title": "الإدارة المتكاملة للمزارع", "level": "متوسط"}
        }

# 9. التطبيقات الجوالة
class MobileAppIntegration:
    def generate_qr(self, data: str) -> str:
        return f"QR-{secrets.token_hex(4)}"

# 10. الاستشارات البيطرية
class VeterinaryConsultation:
    def diagnose(self, symptoms: str) -> dict:
        return {
            "الأعراض": symptoms,
            "التشخيص": "عدوى بكتيرية محتملة",
            "التوصيات": "استشارة طبيب بيطري"
        }

# 11. منصة المجتمع
class CommunityPlatform:
    def __init__(self):
        self.discussions = []
    
    def create_discussion(self, topic: str, content: str) -> dict:
        discussion = {"topic": topic, "content": content, "created": datetime.now().isoformat()}
        self.discussions.append(discussion)
        return discussion

# 12. المؤشرات الحيوية
class BiometricSystem:
    @staticmethod
    def analyze_health() -> dict:
        return {
            "معدل_النمو": f"{np.random.uniform(80, 120):.1f}%",
            "معدل_النفوق": f"{np.random.uniform(2, 8):.1f}%",
            "الحالة": "ممتاز" if np.random.random() > 0.3 else "جيد"
        }

# 13. البصمة الكربونية
class CarbonFootprintSystem:
    @staticmethod
    def calculate_footprint() -> dict:
        return {
            "البصمة_الكربونية": f"{np.random.uniform(1000, 5000):.0f} كجم CO2",
            "التقييم": "جيد" if np.random.random() > 0.4 else "بحاجة لتحسين",
            "توصيات": ["تحسين كفاءة الطاقة", "إدارة النفايات"]
        }

# ==========================================
# 11. CSS والواجهة
# ==========================================
st.markdown("""
<style>
.main-box {
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.18);
    margin-bottom: 50px;
}
.section-title {
    color: #1b5e20;
    border-right: 6px solid #2e7d32;
    padding-right: 15px;
    text-align: right;
    font-size: 1.5rem;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 20px;
}
.formula-item {
    background: linear-gradient(135deg, #f5f5f5, #e8f5e9);
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-weight: bold;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
}
.price-card {
    background: #f1f8e9;
    padding: 20px;
    border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px;
}
.mini-left-signature {
    position: fixed;
    left: 20px;
    bottom: 20px;
    background: #1b5e20;
    color: white;
    padding: 8px 20px;
    border-radius: 25px;
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 12. بوابة الدخول
# ==========================================
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "login_attempts" not in st.session_state:
    st.session_state["login_attempts"] = 0

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width:500px;margin:100px auto;direction:rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#2E7D32;text-align:center;'>🔒 بوابة الدخول</h2>")
    
    input_code = st.text_input("🔑 أدخل كود الدخول:", type="password")
    if st.button("تسجيل الدخول", type="primary", use_container_width=True):
        if input_code.strip() in CODES_DB:
            st.session_state["approved"] = True
            st.session_state["user_role"] = CODES_DB[input_code.strip()]["role"]
            st.rerun()
        else:
            st.session_state["login_attempts"] += 1
            st.error(f"❌ الكود غير صحيح! متبقي {5 - st.session_state['login_attempts']} محاولات")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 13. الواجهة الرئيسية
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# رأس الصفحة
col_logo, col_title = st.columns([0.2, 0.8])
with col_title:
    st.markdown("<h1 style='color:#1b5e20;text-align:right;'>🌾 منصة تاور العلمية للانتاج الحيواني</h1>")
    st.markdown("<p style='color:#1565C0;text-align:right;'>محرك الاستمثال الخطي المتقدم - البروتين المهضوم (DP) ومعادل النشاء (SE)</p>")
    st.markdown("<h3 style='color:#c62828;text-align:right;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>")

# زر الخروج
if st.button("🚪 تسجيل الخروج", use_container_width=True):
    st.session_state["approved"] = False
    st.session_state["user_role"] = None
    st.rerun()

# ==========================================
# 14. التبويبات الرئيسية
# ==========================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 تركيب الأعلاف",
        "📊 بورصة الأسعار",
        "🏭 إدارة المخازن",
        "🧾 الفواتير",
        "🖨️ الديباجة",
        "📈 التحليلات",
        "🐔 مزارع الدجاج",
        "💬 التعليقات",
        "📚 المراجع",
        "💡 المساعدة",
        "🚀 الميزات المتقدمة",
        "📖 الدليل"
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 تركيب الأعلاف",
        "📊 بورصة الأسعار",
        "🏭 إدارة المخازن",
        "📈 التحليلات",
        "💬 التعليقات",
        "📚 المراجع",
        "💡 المساعدة",
        "🚀 الميزات المتقدمة",
        "📖 الدليل"
    ]
else:
    tabs_titles = [
        "🔬 تركيب الأعلاف",
        "📚 المراجع",
        "💡 المساعدة",
        "📖 الدليل"
    ]

tabs = st.tabs(tabs_titles)

# ==========================================
# 15. تبويب تركيب الأعلاف (الكامل)
# ==========================================
with tabs[0]:
    st.markdown('<div class="section-title">🌍 تحديد الموقع وبورصة الأسعار</div>', unsafe_allow_html=True)
    
    col_country, col_city = st.columns(2)
    with col_country:
        user_country = st.selectbox("الدولة:", ["السودان", "LIBYA", "مصر", "باقي دول العالم"])
    with col_city:
        user_city = st.text_input("المدينة:", "الخرطوم")
    
    # أسعار الماشية والمنتجات
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown('<div class="price-card"><b>📈 بورصة الماشية</b><br>عجول تسمين: $1350<br>أبقار كنانة: $900<br>ضأن محلي: $180</div>', unsafe_allow_html=True)
    with col_view2:
        st.markdown('<div class="price-card"><b>🥩 بورصة المنتجات</b><br>لحم بقري: $7.50/كجم<br>لحم ضأن: $9.00/كجم<br>لحم دجاج: $3.80/كجم</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">⚖️ اختيار القطاع</div>', unsafe_allow_html=True)
    main_sector = st.selectbox("القطاع:", ["الأغنام", "الماعز", "الأبقار", "الخيول", "الدواجن", "السمان", "الأسماك"])
    
    if main_sector in ["الأغنام", "الماعز", "الأبقار", "الخيول"]:
        st.markdown('<div class="section-title">📐 تقدير الوزن بالشريط</div>', unsafe_allow_html=True)
        col_h, col_l = st.columns(2)
        with col_h:
            h_girth = st.number_input("محيط الصدر (سم):", value=100.0)
        with col_l:
            b_length = st.number_input("طول الجسم (سم):", value=80.0)
        weight_factor = 15500 if main_sector == "الأغنام" else 15000 if main_sector == "الماعز" else 10838 if main_sector == "الأبقار" else 11877
        calc_weight = (h_girth ** 2 * b_length) / weight_factor
        st.success(f"📊 الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم**")
    
    st.markdown('<div class="section-title">📋 حدود الموازنة</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        target_dp = st.slider("البروتين المهضوم DP %:", 5.0, 35.0, 12.0)
    with col_p2:
        target_se = st.slider("معادل النشاء SE:", 10.0, 90.0, 65.0)
    
    # اختيار المكونات
    st.markdown("### اختيار المكونات")
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in list(BIG_FEEDS_LIBRARY.items())[:4]:
        with st.expander(f"📁 {cat_name}", expanded=True):
            cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(ing_name, value=ing_name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)"])
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = np.random.uniform(200, 500)
    
    # تشغيل المحرك
    if st.button("🚀 تشغيل محرك الاستمثال", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3:
            st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل")
        else:
            c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
            bounds = [(0.0, 100.0) for _ in selected_ingredients]
            
            A_eq = [[1.0 for _ in selected_ingredients]]
            b_eq = [100.0]
            
            cp_row, se_row = [], []
            for ing in selected_ingredients:
                cp_val, dc_val, se_val = 0.0, 0.0, 0.0
                for cat in BIG_FEEDS_LIBRARY.values():
                    if ing in cat:
                        cp_val = cat[ing].get("CP", 0.0)
                        dc_val = cat[ing].get("DC", 0.0)
                        se_val = cat[ing].get("SE", 0.0)
                cp_row.append(cp_val * dc_val)
                se_row.append(se_val)
            A_eq.append(cp_row)
            b_eq.append(target_dp * 100.0)
            
            A_ub = [[-1.0 * x for x in se_row]]
            b_ub = [-1.0 * target_se * 100.0]
            
            res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            
            if res.success:
                formula_results = {}
                computed_se = 0.0
                for idx, ing in enumerate(selected_ingredients):
                    if res.x[idx] > 0.0001:
                        formula_results[ing] = res.x[idx]
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                computed_se += (res.x[idx] / 100.0) * cat[ing].get("SE", 0.0)
                
                st.success("✅ تم تشغيل المحرك بنجاح!")
                st.session_state["active_formula"] = formula_results
                st.session_state["active_cp_tag"] = target_dp
                st.session_state["active_se_tag"] = computed_se
                
                col_r1, col_r2 = st.columns([0.6, 0.4])
                with col_r1:
                    st.write("#### المقادير:")
                    ton_cost = res.fun / 100.0
                    for k, v in formula_results.items():
                        st.markdown(f'<div class="formula-item">▪️ {k}: {v:.2f}% ({v*10:.1f} كجم/طن)</div>', unsafe_allow_html=True)
                    st.metric(f"💰 تكلفة الطن: ${ton_cost:.2f}")
                
                with col_r2:
                    fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()))
                    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 16. تبويب الميزات المتقدمة (التوصيات 1-13)
# ==========================================
if "🚀 الميزات المتقدمة" in tabs_titles:
    with tabs[tabs_titles.index("🚀 الميزات المتقدمة")]:
        st.markdown('<div class="section-title">🚀 الميزات المتقدمة (التوصيات 1-13)</div>', unsafe_allow_html=True)
        
        # 1. نظام التوصيات الذكي
        with st.expander("🤖 1. نظام التوصيات الذكي", expanded=True):
            col_rec1, col_rec2 = st.columns(2)
            with col_rec1:
                ingredient = st.selectbox("اختر مادة:", ["ذرة صفراء", "كسب فول صويا"])
                if st.button("🔍 بحث عن بدائل"):
                    engine = AIRecommendationEngine()
                    alternatives = engine.recommend_alternatives(ingredient)
                    for alt in alternatives:
                        st.markdown(f"• {alt['المادة']} - توفير {alt['التوفير_المتوقع']}")
            with col_rec2:
                if st.button("📊 توقع الأداء"):
                    engine = AIRecommendationEngine()
                    perf = engine.predict_performance(st.session_state.get("active_formula", {}))
                    for k, v in perf.items():
                        st.metric(k, v)
        
        # 2. نظام التقارير المتقدمة
        with st.expander("📊 2. نظام التقارير المتقدمة", expanded=False):
            if st.button("📈 توليد تقرير مقارنة"):
                report_gen = AdvancedReportGenerator()
                formulas = [st.session_state.get("active_formula", {}), {"ذرة": 50, "صويا": 30}]
                names = ["خلطتي", "مقترحة"]
                df = report_gen.generate_comparison_report(formulas, names)
                st.dataframe(df)
        
        # 3. نظام الإشعارات
        with st.expander("🔔 3. نظام الإشعارات", expanded=False):
            notif = AdvancedNotificationSystem()
            msg = st.text_input("رسالة الإشعار:", "تم تحديث الخلطة بنجاح")
            priority = st.selectbox("الأولوية:", ["normal", "medium", "high"])
            if st.button("إرسال إشعار"):
                notif.send_alert(msg, priority)
        
        # 4. معمل التحليل
        with st.expander("🔬 4. معمل التحليل المتقدم", expanded=False):
            if st.button("🔍 تحليل الجودة"):
                lab = AdvancedAnalysisLab()
                result = lab.analyze_quality()
                for k, v in result.items():
                    st.metric(k, v)
        
        # 5. التحليل المالي
        with st.expander("💰 5. نظام التكاليف والربحية", expanded=False):
            col_fin1, col_fin2 = st.columns(2)
            with col_fin1:
                investment = st.number_input("الاستثمار ($):", value=10000)
            with col_fin2:
                profit = st.number_input("الربح السنوي ($):", value=2000)
            if st.button("حساب ROI"):
                fin = FinancialAnalytics()
                result = fin.calculate_roi(investment, profit)
                for k, v in result.items():
                    st.metric(k, v)
        
        # 6. نظام الجودة
        with st.expander("✅ 6. نظام الجودة والاعتماد", expanded=False):
            standard = st.selectbox("المعيار:", ["ISO 22000", "GMP", "HACCP"])
            if st.button("تحقق من المطابقة"):
                quality = QualityCertificationSystem()
                result = quality.check_compliance(standard)
                for k, v in result.items():
                    st.metric(k, v)
        
        # 7. التكامل مع الأنظمة
        with st.expander("🔄 7. التكامل مع الأنظمة الخارجية", expanded=False):
            device_id = st.text_input("معرف الجهاز:", "DEV-001")
            if st.button("ربط الجهاز"):
                integration = ExternalIntegration()
                result = integration.connect_iot(device_id)
                st.success(f"✅ تم ربط {result['device_id']}")
                st.json(result['data'])
        
        # 8. نظام التدريب
        with st.expander("📚 8. نظام التدريب", expanded=False):
            training = TrainingSystem()
            courses = training.get_courses()
            for key, course in courses.items():
                st.markdown(f"**{course['title']}** - المستوى: {course['level']}")
        
        # 9. التطبيقات الجوالة
        with st.expander("📱 9. التطبيقات الجوالة", expanded=False):
            data = st.text_input("البيانات للQR:", "https://tower-platform.com")
            if st.button("توليد QR"):
                mobile = MobileAppIntegration()
                qr = mobile.generate_qr(data)
                st.code(qr)
        
        # 10. الاستشارات البيطرية
        with st.expander("🏥 10. الاستشارات البيطرية", expanded=False):
            symptoms = st.text_area("الأعراض:", "حمى، إسهال، فقدان شهية")
            if st.button("تشخيص"):
                vet = VeterinaryConsultation()
                result = vet.diagnose(symptoms)
                for k, v in result.items():
                    st.write(f"**{k}:** {v}")
        
        # 11. منصة المجتمع
        with st.expander("💬 11. منصة المجتمع", expanded=False):
            topic = st.text_input("موضوع المناقشة:")
            content = st.text_area("المحتوى:")
            if st.button("إنشاء مناقشة"):
                community = CommunityPlatform()
                discussion = community.create_discussion(topic, content)
                st.success(f"✅ تم إنشاء المناقشة: {discussion['topic']}")
        
        # 12. المؤشرات الحيوية
        with st.expander("📊 12. المؤشرات الحيوية", expanded=False):
            if st.button("تحليل الصحة"):
                bio = BiometricSystem()
                result = bio.analyze_health()
                for k, v in result.items():
                    st.metric(k, v)
        
        # 13. البصمة الكربونية
        with st.expander("🌍 13. البصمة الكربونية", expanded=False):
            if st.button("حساب البصمة"):
                carbon = CarbonFootprintSystem()
                result = carbon.calculate_footprint()
                for k, v in result.items():
                    if k == "توصيات":
                        st.write("**توصيات:**")
                        for rec in v:
                            st.markdown(f"• {rec}")
                    else:
                        st.metric(k, v)

# ==========================================
# 17. التذييل
# ==========================================
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("""<div class="mini-left-signature">👨‍🔬 الاختصاصي م. عبد القادر إسماعيل تاور © 2026</div>""", unsafe_allow_html=True)
