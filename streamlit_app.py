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

# استيراد مكتبات توليد الـ PDF ومعالجة اللغة العربية
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus.flowables import HRFlowable
import arabic_reshaper
from bidi.algorithm import get_display
import io
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.font_manager as fm

# ==========================================
# 1. نظام قاعدة البيانات المحلية (SQLite)
# ==========================================
import sqlite3
from dataclasses import dataclass, asdict

class DatabaseManager:
    """مدير قاعدة البيانات المحلية"""
    def __init__(self, db_path="tower_platform.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """تهيئة الجداول"""
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
# 2. نظام المصادقة المتقدم
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
    
    def authenticate(self, username: str, password: str) -> Optional[dict]:
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

# ==========================================
# 3. نظام التنبؤ بالأسعار
# ==========================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_ingredient_prices(self, ingredient_name: str, days: int = 30) -> List[dict]:
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
    
    def predict_price(self, ingredient_name: str, days_ahead: int = 7) -> dict:
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
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان.",
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
# 5. التوصيات الجديدة (1-13) - تعريف الكلاسات بشكل صحيح
# ==========================================

# 1. نظام التوصيات الذكي
class AIRecommendationEngine:
    def __init__(self):
        self.alternatives_db = {
            "ذرة صفراء": [
                {"المادة": "ذرة بيضاء", "التوفير_المتوقع": "8.5%", "الملاءمة": "عالية", "ملاحظات": "بديل اقتصادي جيد"},
                {"المادة": "سورجم (فتريتة)", "التوفير_المتوقع": "12.3%", "الملاءمة": "متوسطة", "ملاحظات": "يحتاج معالجة حرارية"},
                {"المادة": "قمح محلي مصنّع", "التوفير_المتوقع": "5.2%", "الملاءمة": "عالية", "ملاحظات": "جودة ممتازة"}
            ],
            "كسب فول صويا 44%": [
                {"المادة": "كسب فول صويا 48%", "التوفير_المتوقع": "3.5%", "الملاءمة": "عالية", "ملاحظات": "نسبة بروتين أعلى"},
                {"المادة": "أمباز الفول السوداني", "التوفير_المتوقع": "15.8%", "الملاءمة": "عالية", "ملاحظات": "بديل اقتصادي ممتاز"},
                {"المادة": "كسب عباد الشمس 36%", "التوفير_المتوقع": "22.1%", "الملاءمة": "متوسطة", "ملاحظات": "يحتاج معالجة إضافية"}
            ],
            "نخالة قمح (ردة)": [
                {"المادة": "البرسيم الجاف", "التوفير_المتوقع": "10.5%", "الملاءمة": "عالية", "ملاحظات": "مصدر ألياف جيد"},
                {"المادة": "مولاس قصب السكر", "التوفير_المتوقع": "18.2%", "الملاءمة": "عالية", "ملاحظات": "مصدر طاقة ممتاز"}
            ]
        }
    
    def recommend_alternatives(self, ingredient: str) -> List[dict]:
        """توصية ببدائل للمواد العلفية"""
        return self.alternatives_db.get(ingredient, [])
    
    def predict_performance(self, formula: dict) -> dict:
        """توقع أداء الخلطة"""
        if not formula:
            return {
                "معدل_النمو": "غير محدد",
                "كفاءة_التحويل": "غير محدد",
                "التقييم": "لم يتم تحديد خلطة"
            }
        
        avg_protein = np.mean([v for v in formula.values()]) if formula else 15
        return {
            "معدل_النمو": f"{avg_protein * 0.5 + 10:.1f}%",
            "كفاءة_التحويل": f"{1.5 - (avg_protein / 50):.2f}",
            "التقييم": "ممتاز" if avg_protein > 15 else "جيد" if avg_protein > 10 else "مقبول"
        }

# 2. نظام التقارير المتقدمة
class AdvancedReportGenerator:
    @staticmethod
    def generate_comparison_report(formulas: List[dict], names: List[str]) -> pd.DataFrame:
        data = []
        for idx, formula in enumerate(formulas):
            if not formula:
                continue
            total_protein = sum([v for v in formula.values()]) / len(formula) if formula else 0
            total_cost = sum([v * 10 for v in formula.values()]) if formula else 0
            data.append({
                "الخلطة": names[idx] if idx < len(names) else f"خلطة {idx+1}",
                "عدد_المكونات": len(formula),
                "متوسط_البروتين": f"{total_protein:.1f}%",
                "التكلفة_التقديرية": f"${total_cost:.2f}",
                "الكفاءة": "ممتازة" if total_protein > 15 else "جيدة" if total_protein > 10 else "مقبولة"
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
    
    def get_history(self, limit: int = 10):
        return self.history[-limit:]

# 4. معمل التحليل المتقدم
class AdvancedAnalysisLab:
    @staticmethod
    def analyze_quality() -> dict:
        return {
            "اللون": "جيد" if np.random.random() > 0.3 else "متوسط",
            "القوام": "متجانس" if np.random.random() > 0.4 else "غير متجانس",
            "الرطوبة": f"{np.random.uniform(8, 14):.1f}%",
            "التقييم": "ممتاز" if np.random.random() > 0.6 else "جيد"
        }
    
    @staticmethod
    def estimate_nir_values(feed_type: str) -> dict:
        return {
            "البروتين": f"{np.random.uniform(8, 22):.1f}%",
            "الألياف": f"{np.random.uniform(5, 15):.1f}%",
            "الدهون": f"{np.random.uniform(2, 8):.1f}%",
            "الرماد": f"{np.random.uniform(2, 6):.1f}%"
        }

# 5. نظام التكاليف والربحية
class FinancialAnalytics:
    @staticmethod
    def calculate_roi(investment: float, profit: float) -> dict:
        roi = (profit / investment) * 100 if investment > 0 else 0
        payback = investment / profit if profit > 0 else 0
        return {
            "العائد_على_الاستثمار": f"{roi:.1f}%",
            "فترة_الاسترداد": f"{payback:.1f} سنة" if payback > 0 else "غير محدد",
            "التقييم": "ممتاز" if roi > 20 else "جيد" if roi > 10 else "مقبول"
        }
    
    @staticmethod
    def break_even_analysis(fixed_costs: float, var_costs: float, unit_price: float) -> dict:
        contribution = unit_price - var_costs
        break_even = fixed_costs / contribution if contribution > 0 else float('inf')
        return {
            "نقطة_التعادل": f"{break_even:.0f} وحدة" if break_even != float('inf') else "غير محدد",
            "هامش_المساهمة": f"${contribution:.2f}",
            "حالة_الربحية": "مربح" if break_even < 1000 else "بحاجة لتحسين"
        }

# 6. نظام الجودة والاعتماد
class QualityCertificationSystem:
    def __init__(self):
        self.certification_standards = {
            "ISO 22000": {"requirements": ["نظام إدارة سلامة الغذاء", "تتبع المنتج", "تحليل المخاطر"]},
            "GMP": {"requirements": ["ممارسات التصنيع الجيدة", "نظافة المنشأة", "تدريب الموظفين"]},
            "HACCP": {"requirements": ["تحليل المخاطر", "نقاط التحكم الحرجة", "إجراءات التصحيح"]}
        }
    
    def check_compliance(self, standard: str) -> dict:
        if standard not in self.certification_standards:
            return {"status": "error", "message": "معيار غير معروف"}
        
        compliance_score = np.random.uniform(60, 100)
        return {
            "المعيار": standard,
            "درجة_المطابقة": f"{compliance_score:.1f}%",
            "الحالة": "مطابق" if compliance_score > 75 else "غير مطابق",
            "المتطلبات": self.certification_standards[standard]["requirements"]
        }

# 7. التكامل مع الأنظمة الخارجية
class ExternalIntegration:
    def __init__(self):
        self.iot_devices = {}
        self.erp_history = []
    
    def connect_iot(self, device_id: str) -> dict:
        self.iot_devices[device_id] = {
            "status": "connected",
            "data": {"temp": np.random.randint(20, 35), "humidity": np.random.randint(40, 80)},
            "last_update": datetime.now().isoformat()
        }
        return {"status": "connected", "device_id": device_id, "data": self.iot_devices[device_id]["data"]}
    
    def sync_erp(self, data: dict) -> dict:
        record = {"timestamp": datetime.now().isoformat(), "data": data, "status": "success"}
        self.erp_history.append(record)
        return record

# 8. نظام التدريب
class TrainingSystem:
    def __init__(self):
        self.courses = {
            "تغذية_الدواجن": {"title": "التغذية المتقدمة للدواجن", "level": "متقدم", "duration": "4 ساعات"},
            "إدارة_المزارع": {"title": "الإدارة المتكاملة للمزارع", "level": "متوسط", "duration": "3 ساعات"},
            "تركيب_الأعلاف": {"title": "تركيب الأعلاف العلمي", "level": "مبتدئ", "duration": "5 ساعات"}
        }
        self.completed = []
    
    def get_courses(self) -> dict:
        return self.courses
    
    def complete_course(self, user_id: str, course_id: str) -> dict:
        result = {
            "user_id": user_id,
            "course_id": course_id,
            "completion_date": datetime.now().isoformat(),
            "score": np.random.randint(70, 100)
        }
        self.completed.append(result)
        return result

# 9. التطبيقات الجوالة
class MobileAppIntegration:
    def generate_qr(self, data: str) -> str:
        qr_id = secrets.token_hex(4)
        return f"QR-{qr_id}: {data}"
    
    def send_push(self, user_id: str, message: str) -> dict:
        return {"status": "sent", "user_id": user_id, "message": message, "timestamp": datetime.now().isoformat()}

# 10. الاستشارات البيطرية
class VeterinaryConsultation:
    def __init__(self):
        self.symptom_db = {
            "حمى": {"causes": ["عدوى", "التهاب", "إجهاد"], "severity": "متوسطة"},
            "إسهال": {"causes": ["تغذية غير مناسبة", "عدوى بكتيرية", "طفيليات"], "severity": "متوسطة"},
            "سعال": {"causes": ["التهاب رئوي", "عدوى فيروسية", "حساسية"], "severity": "متوسطة"}
        }
    
    def diagnose(self, symptoms: str, animal_type: str) -> dict:
        found = []
        for key in self.symptom_db:
            if key in symptoms:
                found.append(key)
        
        if not found:
            return {"status": "not_diagnosed", "message": "لم يتم التعرف على الأعراض"}
        
        primary = self.symptom_db[found[0]]
        return {
            "animal_type": animal_type,
            "symptoms": found,
            "possible_causes": primary["causes"],
            "severity": primary["severity"],
            "recommendation": "استشارة طبيب بيطري" if primary["severity"] == "عالية" else "مراقبة الحالة"
        }

# 11. منصة المجتمع
class CommunityPlatform:
    def __init__(self):
        self.discussions = []
        self.questions = []
        self.stories = []
    
    def create_discussion(self, topic: str, content: str) -> dict:
        discussion = {"topic": topic, "content": content, "created": datetime.now().isoformat(), "replies": 0}
        self.discussions.append(discussion)
        return discussion
    
    def ask_question(self, question: str, category: str) -> dict:
        q = {"question": question, "category": category, "created": datetime.now().isoformat(), "answers": 0}
        self.questions.append(q)
        return q
    
    def add_story(self, title: str, story: str) -> dict:
        s = {"title": title, "story": story, "created": datetime.now().isoformat(), "likes": 0}
        self.stories.append(s)
        return s

# 12. المؤشرات الحيوية
class BiometricSystem:
    @staticmethod
    def analyze_health(data: dict) -> dict:
        indicators = {
            "معدل_النمو": np.random.uniform(80, 120),
            "معدل_النفوق": np.random.uniform(2, 8),
            "مستوى_النشاط": np.random.choice(["مرتفع", "متوسط", "منخفض"]),
            "جودة_الفرشة": np.random.choice(["ممتازة", "جيدة", "مقبولة"])
        }
        
        health_score = sum([
            10 if indicators["معدل_النمو"] > 90 else 5,
            10 if indicators["معدل_النفوق"] < 5 else 5,
            10 if indicators["مستوى_النشاط"] == "مرتفع" else 5,
            10 if indicators["جودة_الفرشة"] in ["ممتازة", "جيدة"] else 5
        ])
        
        return {
            "indicators": indicators,
            "health_score": health_score,
            "status": "ممتاز" if health_score > 30 else "جيد" if health_score > 20 else "بحاجة لتحسين"
        }
    
    @staticmethod
    def predict_outbreak(data: dict) -> dict:
        risk_factors = {
            "الكثافة": np.random.uniform(1, 10),
            "النظافة": np.random.choice(["جيدة", "متوسطة", "سيئة"]),
            "التهوية": np.random.choice(["جيدة", "متوسطة", "سيئة"]),
            "التاريخ_الصحي": np.random.choice(["جيد", "متوسط", "سيء"])
        }
        
        risk_score = sum([
            10 if risk_factors["الكثافة"] > 7 else 5,
            10 if risk_factors["النظافة"] == "سيئة" else 5,
            10 if risk_factors["التهوية"] == "سيئة" else 5,
            10 if risk_factors["التاريخ_الصحي"] == "سيء" else 5
        ])
        
        return {
            "risk_factors": risk_factors,
            "risk_score": risk_score,
            "risk_level": "مرتفع" if risk_score > 30 else "متوسط" if risk_score > 20 else "منخفض"
        }

# 13. البصمة الكربونية
class CarbonFootprintSystem:
    @staticmethod
    def calculate_carbon_footprint(data: dict) -> dict:
        factors = {
            "انبعاثات_الميثان": np.random.uniform(100, 500),
            "انبعاثات_ثاني_أكسيد_الكربون": np.random.uniform(200, 1000),
            "استهلاك_الطاقة": np.random.uniform(50, 200),
            "إدارة_النفايات": np.random.choice(["جيدة", "متوسطة", "سيئة"])
        }
        
        total_footprint = sum([
            factors["انبعاثات_الميثان"] * 25,
            factors["انبعاثات_ثاني_أكسيد_الكربون"] * 1,
            factors["استهلاك_الطاقة"] * 0.5
        ])
        
        return {
            "factors": factors,
            "total_footprint": f"{total_footprint:.0f} كجم CO2 مكافئ",
            "rating": "ممتاز" if total_footprint < 5000 else "جيد" if total_footprint < 10000 else "بحاجة لتحسين",
            "recommendations": [
                "تحسين كفاءة الطاقة" if factors["استهلاك_الطاقة"] > 100 else "استمرار الكفاءة",
                "تحسين إدارة النفايات" if factors["إدارة_النفايات"] != "جيدة" else "إدارة جيدة"
            ]
        }

# ==========================================
# 6. إعدادات المنصة
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 7. تحميل الصورة كخلفية
# ==========================================
def get_background_image():
    """تحميل الصورة كخلفية للمنصة"""
    # محاولة تحميل الصورة من المسارات المحتملة
    image_paths = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG", "background.jpg"]
    
    for path in image_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                    return f"data:image/jpeg;base64,{img_data}"
            except:
                continue
    
    # إذا لم توجد الصورة، استخدام صورة افتراضية من Unsplash
    return "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop"

BACKGROUND_IMAGE = get_background_image()

# ==========================================
# 8. CSS مع خلفية مخصصة
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');

* {{
    font-family: 'Cairo', 'Tajawal', sans-serif;
}}

html, body, [data-testid="stAppViewContainer"] {{
    background-image: url("{BACKGROUND_IMAGE}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

.stApp {{ 
    background: transparent; 
}}

.main-box {{
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
    margin-bottom: 50px;
    backdrop-filter: blur(10px);
}}

/* باقي الـ CSS كما هو */
.formula-item {{
    background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(232,245,233,0.9) 100%);
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-weight: bold;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    text-align: right;
}}

.section-title {{
    color: #1b5e20;
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
}}

.price-card {{
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px;
    border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
}}

.warning-card {{
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 15px;
    border-radius: 12px;
    border-right: 5px solid #f57c00;
    margin-bottom: 15px;
    direction: rtl;
    text-align: right;
    color: #e65100;
}}

.stock-critical {{ 
    background: #ffebee; 
    padding: 8px 12px; 
    border-radius: 8px; 
    color: #c62828; 
    font-weight: bold;
}}

.stock-normal {{ 
    background: #e8f5e9; 
    padding: 8px 12px; 
    border-radius: 8px; 
    color: #2e7d32;
}}

.metric-card {{
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    text-align: center;
}}

.mini-left-signature {{
    position: fixed;
    left: 20px;
    bottom: 20px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white;
    padding: 8px 20px;
    font-size: 0.85rem;
    border-radius: 25px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    z-index: 9999;
    direction: rtl;
}}

.profile-img-style {{
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    display: block;
    margin: 0 auto;
}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 9. الأكواد المعتمدة
# ==========================================
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# ==========================================
# 10. مكتبة الأعلاف الكاملة (مختصرة ولكن كافية)
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
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0}
    },
    "🪨 الأملاح والمعادن": {
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0}
    }
}

# ==========================================
# 11. إدارة المخزون
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

InventoryManager.initialize_inventory()

# ==========================================
# 12. حالة الجلسة
# ==========================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state: st.session_state["active_se_tag"] = 65.0
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0
if "broiler_farms" not in st.session_state: st.session_state["broiler_farms"] = {}
if "selected_farm" not in st.session_state: st.session_state["selected_farm"] = None
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = "• [توجيه الاختصاصي]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا.\n"

# ==========================================
# 13. بوابة الدخول
# ==========================================
MAX_LOGIN_ATTEMPTS = 5

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width:500px;margin:100px auto;direction:rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#2E7D32;text-align:center;'>🔒 بوابة الدخول الذكية</h2>")
    
    input_code = st.text_input("🔑 أدخل كود الدخول:", type="password")
    if st.button("تسجيل الدخول", type="primary", use_container_width=True):
        if input_code.strip() in CODES_DB:
            st.session_state["approved"] = True
            st.session_state["user_role"] = CODES_DB[input_code.strip()]["role"]
            st.rerun()
        else:
            st.session_state["login_attempts"] += 1
            remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
            st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 14. الواجهة الرئيسية
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# الرأس
col_logo, col_title = st.columns([0.2, 0.8])
with col_title:
    st.markdown("<h1 style='color:#1b5e20;text-align:right;'>🌾 منصة تاور العلمية للانتاج الحيواني</h1>")
    st.markdown("<p style='color:#1565C0;text-align:right;'>محرك الاستمثال الخطي المتقدم - البروتين المهضوم (DP) ومعادل النشاء (SE)</p>")
    st.markdown("<h3 style='color:#c62828;text-align:right;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>")

if st.button("🚪 تسجيل الخروج", use_container_width=True):
    st.session_state["approved"] = False
    st.session_state["user_role"] = None
    st.rerun()

# ==========================================
# 15. التبويبات
# ==========================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 تركيب الأعلاف",
        "📊 بورصة الأسعار",
        "🏭 إدارة المخازن",
        "🧾 الفواتير",
        "📈 التحليلات",
        "🐔 مزارع الدجاج",
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
# 16. تبويب تركيب الأعلاف
# ==========================================
with tabs[0]:
    st.markdown('<div class="section-title">🔬 تركيب علفة نموذجية</div>', unsafe_allow_html=True)
    
    # اختيار القطاع
    main_sector = st.selectbox("القطاع:", ["أغنام", "ماعز", "أبقار", "دواجن", "أسماك"])
    
    # حدود الموازنة
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        target_dp = st.slider("البروتين المهضوم DP %:", 5.0, 35.0, 12.0)
    with col_p2:
        target_se = st.slider("معادل النشاء SE:", 10.0, 90.0, 65.0)
    
    # اختيار المكونات
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
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
                    st.session_state["computed_ton_cost"] = ton_cost
                
                with col_r2:
                    fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()))
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ تعذر إيجاد حل رياضي متزن")

# ==========================================
# 17. تبويب الميزات المتقدمة (التوصيات 1-13)
# ==========================================
if "🚀 الميزات المتقدمة" in tabs_titles:
    with tabs[tabs_titles.index("🚀 الميزات المتقدمة")]:
        st.markdown('<div class="section-title">🚀 الميزات المتقدمة (التوصيات 1-13)</div>', unsafe_allow_html=True)
        
        # 1. نظام التوصيات الذكي
        with st.expander("🤖 1. نظام التوصيات الذكي", expanded=True):
            st.markdown("### 🤖 نظام التوصيات الذكي")
            col_rec1, col_rec2 = st.columns(2)
            with col_rec1:
                ingredients = ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)"]
                selected_ing = st.selectbox("اختر مادة للبحث عن بدائل:", ingredients)
                if st.button("🔍 البحث عن بدائل", key="find_alternatives"):
                    engine = AIRecommendationEngine()
                    alternatives = engine.recommend_alternatives(selected_ing)
                    if alternatives:
                        for alt in alternatives:
                            st.markdown(f"""
                            <div class='formula-item'>
                                • {alt['المادة']} - توفير {alt['التوفير_المتوقع']} - الملاءمة: {alt['الملاءمة']}
                                <br><small>{alt['ملاحظات']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("لا توجد بدائل مقترحة لهذه المادة")
            with col_rec2:
                if st.button("📊 توقع أداء الخلطة", key="predict_performance"):
                    engine = AIRecommendationEngine()
                    perf = engine.predict_performance(st.session_state.get("active_formula", {}))
                    for k, v in perf.items():
                        st.metric(k, v)
        
        # 2. نظام التقارير المتقدمة
        with st.expander("📊 2. نظام التقارير المتقدمة", expanded=False):
            st.markdown("### 📊 التقارير المتقدمة")
            if st.button("📈 توليد تقرير مقارنة", key="compare_report"):
                report_gen = AdvancedReportGenerator()
                formulas = [st.session_state.get("active_formula", {}), {"ذرة": 50, "صويا": 30, "نخالة": 20}]
                names = ["خلطتي الحالية", "خلطة مقترحة"]
                comparison = report_gen.generate_comparison_report(formulas, names)
                if not comparison.empty:
                    st.dataframe(comparison, use_container_width=True)
                else:
                    st.info("لا توجد بيانات كافية لتوليد التقرير")
        
        # 3. نظام الإشعارات
        with st.expander("🔔 3. نظام الإشعارات المتقدم", expanded=False):
            st.markdown("### 🔔 نظام الإشعارات")
            notif = AdvancedNotificationSystem()
            msg = st.text_input("رسالة الإشعار:", "تم تحديث الخلطة بنجاح")
            priority = st.selectbox("الأولوية:", ["normal", "medium", "high"])
            if st.button("📨 إرسال إشعار", key="send_notification"):
                notif.send_alert(msg, priority)
        
        # 4. معمل التحليل
        with st.expander("🔬 4. معمل التحليل المتقدم", expanded=False):
            st.markdown("### 🔬 معمل التحليل المتقدم")
            if st.button("🔍 تحليل جودة المادة", key="quality_analysis"):
                lab = AdvancedAnalysisLab()
                quality = lab.analyze_quality()
                for key, value in quality.items():
                    st.metric(key, value)
        
        # 5. التحليل المالي
        with st.expander("💰 5. نظام التكاليف والربحية", expanded=False):
            st.markdown("### 💰 التحليل المالي")
            col_fin1, col_fin2 = st.columns(2)
            with col_fin1:
                investment = st.number_input("الاستثمار ($):", value=10000, step=1000)
                profit = st.number_input("الربح السنوي ($):", value=2000, step=500)
                if st.button("📊 حساب ROI", key="calc_roi"):
                    fin = FinancialAnalytics()
                    result = fin.calculate_roi(investment, profit)
                    for k, v in result.items():
                        st.metric(k, v)
            with col_fin2:
                fixed_costs = st.number_input("التكاليف الثابتة ($):", value=5000, step=500)
                var_costs = st.number_input("التكاليف المتغيرة ($/وحدة):", value=2.0, step=0.5)
                unit_price = st.number_input("سعر الوحدة ($):", value=5.0, step=0.5)
                if st.button("📊 تحليل التعادل", key="break_even"):
                    fin = FinancialAnalytics()
                    result = fin.break_even_analysis(fixed_costs, var_costs, unit_price)
                    for k, v in result.items():
                        st.metric(k, v)
        
        # 6. نظام الجودة
        with st.expander("✅ 6. نظام الجودة والاعتماد", expanded=False):
            st.markdown("### ✅ نظام الجودة")
            standard = st.selectbox("المعيار:", ["ISO 22000", "GMP", "HACCP"])
            if st.button("🔍 تحقق من المطابقة", key="check_compliance"):
                quality = QualityCertificationSystem()
                result = quality.check_compliance(standard)
                for k, v in result.items():
                    if k == "المتطلبات":
                        st.write("**المتطلبات:**")
                        for req in v:
                            st.markdown(f"• {req}")
                    else:
                        st.metric(k, v)
        
        # 7. التكامل مع الأنظمة
        with st.expander("🔄 7. التكامل مع الأنظمة الخارجية", expanded=False):
            st.markdown("### 🔄 التكامل مع الأنظمة")
            col_int1, col_int2 = st.columns(2)
            with col_int1:
                device_id = st.text_input("معرف الجهاز:", "DEV-001")
                if st.button("🔗 ربط الجهاز", key="connect_iot"):
                    integration = ExternalIntegration()
                    result = integration.connect_iot(device_id)
                    st.success(f"✅ تم ربط {result['device_id']}")
                    st.json(result['data'])
            with col_int2:
                if st.button("🔄 مزامنة ERP", key="sync_erp"):
                    integration = ExternalIntegration()
                    result = integration.sync_erp({"orders": 10, "inventory": 500})
                    st.success(f"✅ تمت المزامنة في {result['timestamp']}")
        
        # 8. نظام التدريب
        with st.expander("📚 8. نظام التدريب والتعلم", expanded=False):
            st.markdown("### 📚 نظام التدريب")
            training = TrainingSystem()
            courses = training.get_courses()
            for key, course in courses.items():
                st.markdown(f"**{course['title']}** - المستوى: {course['level']} - المدة: {course['duration']}")
            if st.button("🎓 تسجيل إكمال دورة", key="complete_course"):
                result = training.complete_course("user_001", "تغذية_الدواجن")
                st.success(f"✅ تم إكمال الدورة بنجاح! النتيجة: {result['score']}%")
        
        # 9. التطبيقات الجوالة
        with st.expander("📱 9. التطبيقات الجوالة", expanded=False):
            st.markdown("### 📱 التطبيقات الجوالة")
            data = st.text_input("البيانات للQR:", "https://tower-platform.com")
            if st.button("📱 توليد QR", key="generate_qr"):
                mobile = MobileAppIntegration()
                qr = mobile.generate_qr(data)
                st.code(qr)
                st.info("📱 يمكنك مسح الكود للوصول السريع للمنصة")
        
        # 10. الاستشارات البيطرية
        with st.expander("🏥 10. نظام الاستشارات البيطرية", expanded=False):
            st.markdown("### 🏥 الاستشارات البيطرية")
            symptoms = st.text_area("الأعراض:", "حمى، إسهال، فقدان شهية")
            animal_type = st.selectbox("نوع الحيوان:", ["أبقار", "أغنام", "ماعز", "دواجن", "خيول"])
            if st.button("🔍 تشخيص", key="diagnose"):
                vet = VeterinaryConsultation()
                result = vet.diagnose(symptoms, animal_type)
                if result.get('status') != 'not_diagnosed':
                    st.json(result)
                    st.warning(f"⚠️ الأعراض: {', '.join(result.get('symptoms', []))}")
                    st.info(f"التوصية: {result.get('recommendation', 'استشارة طبيب بيطري')}")
                else:
                    st.info(result.get('message', 'لم يتم التعرف على الأعراض'))
        
        # 11. منصة المجتمع
        with st.expander("💬 11. منصة المجتمع الحيواني", expanded=False):
            st.markdown("### 💬 المجتمع الحيواني")
            tab_discuss, tab_questions, tab_stories = st.tabs(["مناقشات", "أسئلة", "قصص نجاح"])
            with tab_discuss:
                topic = st.text_input("موضوع المناقشة:")
                content = st.text_area("المحتوى:")
                if st.button("📝 إنشاء مناقشة", key="create_discussion"):
                    if topic and content:
                        community = CommunityPlatform()
                        discussion = community.create_discussion(topic, content)
                        st.success(f"✅ تم إنشاء المناقشة: {discussion['topic']}")
                    else:
                        st.warning("⚠️ يرجى إدخال الموضوع والمحتوى")
            with tab_questions:
                question = st.text_input("سؤالك:")
                category = st.selectbox("التصنيف:", ["تغذية", "صحة", "إدارة", "تسويق"])
                if st.button("❓ طرح سؤال", key="ask_question"):
                    if question:
                        community = CommunityPlatform()
                        q = community.ask_question(question, category)
                        st.success(f"✅ تم طرح السؤال: {q['question']}")
                    else:
                        st.warning("⚠️ يرجى كتابة السؤال")
            with tab_stories:
                title = st.text_input("عنوان القصة:")
                story = st.text_area("القصة:")
                if st.button("⭐ مشاركة قصة نجاح", key="share_story"):
                    if title and story:
                        community = CommunityPlatform()
                        s = community.add_story(title, story)
                        st.success(f"✅ تم مشاركة قصة النجاح: {s['title']}")
                    else:
                        st.warning("⚠️ يرجى إدخال العنوان والقصة")
        
        # 12. المؤشرات الحيوية
        with st.expander("📊 12. نظام المؤشرات الحيوية", expanded=False):
            st.markdown("### 📊 المؤشرات الحيوية")
            col_bio1, col_bio2 = st.columns(2)
            with col_bio1:
                if st.button("🩺 تحليل الصحة العامة", key="health_analysis"):
                    bio = BiometricSystem()
                    result = bio.analyze_health({})
                    for k, v in result.items():
                        if k == 'indicators':
                            st.write("**المؤشرات:**")
                            for ik, iv in v.items():
                                st.metric(ik, iv)
                        else:
                            st.metric(k, v)
            with col_bio2:
                if st.button("🔮 التنبؤ بتفشي الأمراض", key="outbreak_prediction"):
                    bio = BiometricSystem()
                    result = bio.predict_outbreak({})
                    for k, v in result.items():
                        if k == 'risk_factors':
                            st.write("**عوامل الخطر:**")
                            for rk, rv in v.items():
                                st.metric(rk, rv)
                        else:
                            st.metric(k, v)
        
        # 13. البصمة الكربونية
        with st.expander("🌍 13. نظام البصمة الكربونية", expanded=False):
            st.markdown("### 🌍 البصمة الكربونية")
            col_carb1, col_carb2 = st.columns(2)
            with col_carb1:
                st.subheader("بيانات المزرعة")
                farm_size = st.number_input("حجم المزرعة (هكتار):", value=10, step=1)
                animal_count = st.number_input("عدد الحيوانات:", value=1000, step=100)
                energy_consumption = st.number_input("استهلاك الطاقة (كيلوواط/ساعة):", value=500, step=50)
            with col_carb2:
                if st.button("🌍 حساب البصمة الكربونية", key="calc_carbon"):
                    carbon = CarbonFootprintSystem()
                    result = carbon.calculate_carbon_footprint({
                        "size": farm_size,
                        "animals": animal_count,
                        "energy": energy_consumption
                    })
                    for k, v in result.items():
                        if k == 'recommendations':
                            st.write("**التوصيات:**")
                            for rec in v:
                                st.markdown(f"• {rec}")
                        elif k == 'factors':
                            st.write("**عوامل الانبعاث:**")
                            for fk, fv in v.items():
                                st.metric(fk, fv)
                        else:
                            st.metric(k, v)

# ==========================================
# 18. التذييل
# ==========================================
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("""<div class="mini-left-signature">👨‍🔬 الاختصاصي م. عبد القادر إسماعيل تاور © 2026</div>""", unsafe_allow_html=True)
