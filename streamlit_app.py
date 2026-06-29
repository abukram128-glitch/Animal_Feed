# Digital Signature: 8f7e3d9c2b1a5e7f9d4c3b2a1e7f9d4c
# Generated: 2026-06-29T12:00:00.000000

import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import base64
import smtplib
import time
import urllib.parse
import hashlib
import secrets
import sqlite3
import pickle
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات المنصة المتقدمة
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية - النظام المتكامل للإنتاج الحيواني",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. قاعدة البيانات المحلية (SQLite)
# ==========================================
@dataclass
class FarmCycle:
    """نموذج دورة إنتاجية"""
    cycle_id: str
    farm_name: str
    animal_type: str
    breed: str
    start_date: str
    end_date: str
    initial_birds: int
    final_weight_kg: float
    total_feed_kg: float
    total_dead: int
    total_culled: int
    fcr: float
    adg: float
    epef: float
    mortality_rate: float
    notes: str

@dataclass
class FeedFormula:
    """نموذج خلطة علفية"""
    formula_id: str
    formula_name: str
    animal_type: str
    target_dp: float
    target_se: float
    ingredients: Dict[str, float]
    total_cost: float
    created_by: str
    created_date: str

class DatabaseManager:
    """مدير قاعدة البيانات"""
    def __init__(self, db_path="tower_platform.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """تهيئة الجداول"""
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
        
        # جدول الدورات الإنتاجية
        c.execute('''CREATE TABLE IF NOT EXISTS farm_cycles
                     (cycle_id TEXT PRIMARY KEY,
                      farm_name TEXT,
                      animal_type TEXT,
                      breed TEXT,
                      start_date TEXT,
                      end_date TEXT,
                      initial_birds INTEGER,
                      final_weight_kg REAL,
                      total_feed_kg REAL,
                      total_dead INTEGER,
                      total_culled INTEGER,
                      fcr REAL,
                      adg REAL,
                      epef REAL,
                      mortality_rate REAL,
                      notes TEXT,
                      created_by TEXT,
                      created_date TEXT)''')
        
        # جدول الخلطات العلفية
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
        
        # جدول الأسعار التاريخية
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
        """تنفيذ استعلام"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    
    def insert_record(self, table: str, data: dict):
        """إدراج سجل جديد"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        c.execute(query, list(data.values()))
        conn.commit()
        conn.close()

# ==========================================
# 3. نظام المصادقة المتقدم
# ==========================================
class AuthManager:
    """مدير المصادقة والصلاحيات"""
    
    SESSION_TIMEOUT = 3600  # ثانية
    
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()
    
    def _create_default_admin(self):
        """إنشاء مستخدم افتراضي"""
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')
    
    def create_user(self, username: str, password: str, role: str, full_name: str, email: str, phone: str):
        """إنشاء مستخدم جديد"""
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
        """مصادقة المستخدم"""
        users = self.db.execute_query(
            "SELECT * FROM users WHERE username=?", 
            (username,)
        )
        if users:
            user = users[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == password_hash:  # password_hash
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'full_name': user[4],
                    'email': user[5],
                    'phone': user[6]
                }
        return None
    
    def check_permission(self, user_role: str, required_role: str) -> bool:
        """التحقق من الصلاحية"""
        roles_hierarchy = {
            'owner': 4,
            'manager': 3,
            'specialist': 2,
            'breeder': 1
        }
        return roles_hierarchy.get(user_role, 0) >= roles_hierarchy.get(required_role, 0)

# ==========================================
# 4. نظام إدارة المزارع والدورات المتقدم
# ==========================================
class FarmCycleManager:
    """مدير الدورات الإنتاجية"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_cycle(self, farm_name: str, animal_type: str, breed: str, 
                     initial_birds: int, created_by: str) -> dict:
        """إنشاء دورة إنتاجية جديدة"""
        cycle_id = f"CYC_{datetime.now().strftime('%Y%m%d')}_{secrets.token_hex(4)}"
        data = {
            'cycle_id': cycle_id,
            'farm_name': farm_name,
            'animal_type': animal_type,
            'breed': breed,
            'start_date': datetime.now().isoformat(),
            'end_date': '',
            'initial_birds': initial_birds,
            'final_weight_kg': 0.0,
            'total_feed_kg': 0.0,
            'total_dead': 0,
            'total_culled': 0,
            'fcr': 0.0,
            'adg': 0.0,
            'epef': 0.0,
            'mortality_rate': 0.0,
            'notes': '',
            'created_by': created_by,
            'created_date': datetime.now().isoformat()
        }
        self.db.insert_record('farm_cycles', data)
        return data
    
    def update_cycle(self, cycle_id: str, data: dict):
        """تحديث بيانات الدورة"""
        # تنفيذ تحديث
        pass
    
    def get_cycle(self, cycle_id: str) -> dict:
        """جلب بيانات دورة"""
        result = self.db.execute_query(
            "SELECT * FROM farm_cycles WHERE cycle_id=?", 
            (cycle_id,)
        )
        if result:
            row = result[0]
            return {
                'cycle_id': row[0],
                'farm_name': row[1],
                'animal_type': row[2],
                'breed': row[3],
                'start_date': row[4],
                'end_date': row[5],
                'initial_birds': row[6],
                'final_weight_kg': row[7],
                'total_feed_kg': row[8],
                'total_dead': row[9],
                'total_culled': row[10],
                'fcr': row[11],
                'adg': row[12],
                'epef': row[13],
                'mortality_rate': row[14],
                'notes': row[15],
                'created_by': row[16],
                'created_date': row[17]
            }
        return None
    
    def list_cycles(self, farm_name: str = None) -> List[dict]:
        """قائمة الدورات"""
        query = "SELECT * FROM farm_cycles"
        params = ()
        if farm_name:
            query += " WHERE farm_name=?"
            params = (farm_name,)
        results = self.db.execute_query(query, params)
        return [{
            'cycle_id': r[0],
            'farm_name': r[1],
            'animal_type': r[2],
            'breed': r[3],
            'start_date': r[4],
            'end_date': r[5],
            'initial_birds': r[6],
            'final_weight_kg': r[7],
            'fcr': r[11],
            'adg': r[12],
            'epef': r[13],
            'mortality_rate': r[14]
        } for r in results]
    
    def calculate_metrics(self, cycle_data: dict) -> dict:
        """حساب مؤشرات الأداء"""
        initial = cycle_data.get('initial_birds', 1)
        dead = cycle_data.get('total_dead', 0)
        culled = cycle_data.get('total_culled', 0)
        final_weight = cycle_data.get('final_weight_kg', 0)
        feed = cycle_data.get('total_feed_kg', 0)
        
        alive = initial - dead - culled
        
        # ADG - متوسط النمو اليومي
        days = 42  # فترة افتراضية
        adg = (final_weight * 1000) / days if days > 0 else 0
        
        # FCR - معامل التحويل
        weight_gain = alive * final_weight
        fcr = feed / weight_gain if weight_gain > 0 else 0
        
        # EPEF - مؤشر الأداء
        mortality_rate = (dead / initial) * 100 if initial > 0 else 0
        livability = 100 - mortality_rate
        epef = (livability * final_weight) / (days * fcr) * 100 if fcr > 0 else 0
        
        return {
            'adg': adg,
            'fcr': fcr,
            'epef': epef,
            'mortality_rate': mortality_rate,
            'livability': livability,
            'alive_birds': alive
        }

# ==========================================
# 5. محرك تحليل الأسعار والتنبؤ
# ==========================================
class PricePredictor:
    """محلل وتنبؤ الأسعار"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_ingredient_prices(self, ingredient_name: str, days: int = 30) -> List[dict]:
        """جلب أسعار المادة خلال فترة"""
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
        """توقع السعر المستقبلي باستخدام المتوسط المتحرك"""
        prices = self.get_ingredient_prices(ingredient_name, 30)
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0}
        
        price_list = [p['price'] for p in prices]
        # متوسط متحرك مرجح
        weights = np.array(range(1, len(price_list) + 1))
        weighted_avg = np.average(price_list, weights=weights)
        
        # توقع بسيط
        trend = (price_list[0] - price_list[-1]) / len(price_list) if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        
        return {
            'prediction': max(0, prediction),
            'confidence': min(1, len(price_list) / 30),
            'current_price': price_list[0] if price_list else None,
            'trend': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'
        }

# ==========================================
# 6. نظام التقارير المتقدم
# ==========================================
class ReportGenerator:
    """مولد التقارير المتقدم"""
    
    def generate_cycle_report(self, cycle_id: str) -> dict:
        """تقرير دورة إنتاجية كامل"""
        cycle_mgr = FarmCycleManager()
        cycle = cycle_mgr.get_cycle(cycle_id)
        if not cycle:
            return None
        
        metrics = cycle_mgr.calculate_metrics(cycle)
        
        report = {
            'cycle_info': cycle,
            'metrics': metrics,
            'summary': {
                'total_days': 42,
                'total_feed_cost': cycle.get('total_feed_kg', 0) * 0.45,  # تقدير
                'revenue': metrics.get('alive_birds', 0) * cycle.get('final_weight_kg', 0) * 3.8,
                'profit_margin': 0
            }
        }
        
        # حساب هامش الربح
        revenue = report['summary']['revenue']
        cost = report['summary']['total_feed_cost'] + (cycle.get('initial_birds', 0) * 0.65)
        report['summary']['profit_margin'] = ((revenue - cost) / revenue * 100) if revenue > 0 else 0
        
        return report

# ==========================================
# 7. واجهة المستخدم الرئيسية - النسخة المطورة
# ==========================================
def main():
    """الدالة الرئيسية للتطبيق"""
    
    # تهيئة مدير المصادقة
    auth = AuthManager()
    
    # حالة الجلسة
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.user_role = 'guest'
    
    # شريط جانبي
    with st.sidebar:
        st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=200", use_column_width=True)
        st.title("🌾 منصة تاور العلمية")
        st.caption("النظام المتكامل للإنتاج الحيواني")
        
        # لوحة التحكم (Dashboard)
        if st.session_state.authenticated:
            user = st.session_state.user
            st.markdown(f"""
            <div style='background: #f0fdf4; padding: 15px; border-radius: 10px;'>
                <p style='margin: 0;'><b>{user.get('full_name', 'مستخدم')}</b></p>
                <p style='margin: 0; font-size: 0.8rem; color: #666;'>@{user.get('username', '')}</p>
                <p style='margin: 0; font-size: 0.8rem;'><span style='background: #2e7d32; color: white; padding: 2px 10px; border-radius: 12px;'>{user.get('role', 'ضيف')}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # قائمة التنقل الرئيسية
            pages = {
                "🏠 الرئيسية": "dashboard",
                "📊 الدورات الإنتاجية": "cycles",
                "🔬 الخلطات العلفية": "formulas",
                "📈 التحليلات": "analytics",
                "📜 التقارير": "reports",
                "⚙️ الإعدادات": "settings"
            }
            
            selection = st.radio("التنقل", list(pages.keys()))
            st.session_state.current_page = pages[selection]
            
            if st.button("🚪 تسجيل الخروج", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.user_role = 'guest'
                st.rerun()
        else:
            # صفحة تسجيل الدخول
            st.markdown("### 🔐 تسجيل الدخول")
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            
            if st.button("دخول", use_container_width=True):
                user = auth.authenticate(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.user_role = user['role']
                    st.success("✅ تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    
    # المحتوى الرئيسي
    if not st.session_state.authenticated:
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>🌾 منصة تاور العلمية</h1>
            <p style='font-size: 1.2rem; color: #555;'>النظام المتكامل للإنتاج الحيواني وتركيب الأعلاف</p>
            <p style='font-size: 1rem; color: #888;'>يرجى تسجيل الدخول من الشريط الجانبي</p>
            <div style='margin-top: 30px;'>
                <p>👨‍🔬 الاختصاصي: <b>م. عبد القادر إسماعيل تاور</b></p>
                <p style='font-size: 0.9rem;'>© 2026 جميع الحقوق محفوظة</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # الصفحات
    current_page = st.session_state.get('current_page', 'dashboard')
    
    if current_page == 'dashboard':
        render_dashboard()
    elif current_page == 'cycles':
        render_cycles()
    elif current_page == 'formulas':
        render_formulas()
    elif current_page == 'analytics':
        render_analytics()
    elif current_page == 'reports':
        render_reports()
    elif current_page == 'settings':
        render_settings()

def render_dashboard():
    """لوحة التحكم الرئيسية"""
    st.title("🏠 لوحة التحكم الرئيسية")
    
    # مؤشرات الأداء العامة
    cycle_mgr = FarmCycleManager()
    cycles = cycle_mgr.list_cycles()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 عدد الدورات", len(cycles))
    with col2:
        active = len([c for c in cycles if not c.get('end_date')])
        st.metric("🔄 دورات نشطة", active)
    with col3:
        completed = len([c for c in cycles if c.get('end_date')])
        st.metric("✅ دورات مكتملة", completed)
    with col4:
        avg_epef = np.mean([c.get('epef', 0) for c in cycles if c.get('epef', 0) > 0])
        st.metric("📈 متوسط EPEF", f"{avg_epef:.0f}")
    
    st.divider()
    
    # آخر النشاطات
    st.subheader("📋 آخر النشاطات")
    if cycles:
        recent = sorted(cycles, key=lambda x: x.get('start_date', ''), reverse=True)[:5]
        for cycle in recent:
            with st.expander(f"🐔 {cycle.get('farm_name', '')} - {cycle.get('breed', '')}"):
                cols = st.columns(3)
                with cols[0]:
                    st.write(f"**البداية:** {cycle.get('start_date', '')[:10]}")
                    st.write(f"**العدد:** {cycle.get('initial_birds', 0)}")
                with cols[1]:
                    st.write(f"**FCR:** {cycle.get('fcr', 0):.2f}")
                    st.write(f"**ADG:** {cycle.get('adg', 0):.1f} جم")
                with cols[2]:
                    st.write(f"**EPEF:** {cycle.get('epef', 0):.0f}")
                    st.write(f"**النفوق:** {cycle.get('mortality_rate', 0):.1f}%")
    else:
        st.info("لا توجد دورات إنتاجية مسجلة")

def render_cycles():
    """صفحة إدارة الدورات الإنتاجية"""
    st.title("📊 إدارة الدورات الإنتاجية")
    
    tab1, tab2, tab3 = st.tabs(["📝 تسجيل دورة جديدة", "📋 قائمة الدورات", "📊 تحليل الأداء"])
    
    with tab1:
        st.subheader("تسجيل دورة إنتاجية جديدة")
        
        col1, col2 = st.columns(2)
        with col1:
            farm_name = st.text_input("اسم المزرعة")
            animal_type = st.selectbox("نوع الحيوان", ["دواجن لاحم", "دواجن بياض", "أبقار", "أغنام", "ماعز", "أسماك"])
            breed = st.text_input("السلالة")
        with col2:
            initial_birds = st.number_input("العدد الأولي", min_value=1, value=1000, step=100)
            start_date = st.date_input("تاريخ البداية")
        
        if st.button("💾 إنشاء الدورة", type="primary"):
            if farm_name:
                cycle_mgr = FarmCycleManager()
                cycle = cycle_mgr.create_cycle(
                    farm_name=farm_name,
                    animal_type=animal_type,
                    breed=breed,
                    initial_birds=initial_birds,
                    created_by=st.session_state.user.get('username', 'unknown')
                )
                st.success(f"✅ تم إنشاء الدورة {cycle['cycle_id']}")
                st.rerun()
            else:
                st.warning("⚠️ يرجى إدخال اسم المزرعة")
    
    with tab2:
        st.subheader("قائمة الدورات الإنتاجية")
        cycle_mgr = FarmCycleManager()
        cycles = cycle_mgr.list_cycles()
        
        if cycles:
            df = pd.DataFrame(cycles)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("لا توجد دورات مسجلة")
    
    with tab3:
        st.subheader("تحليل أداء الدورات")
        # رسوم بيانية تحليلية
        st.info("جاري تطوير هذه الصفحة...")

def render_formulas():
    """صفحة الخلطات العلفية"""
    st.title("🔬 تركيب الخلطات العلفية")
    st.info("🧪 محرك الاستمثال الخطي المتقدم - قيد التطوير")
    # يمكن دمج الكود السابق هنا

def render_analytics():
    """صفحة التحليلات"""
    st.title("📈 التحليلات والتنبؤات")
    
    tab1, tab2 = st.tabs(["📊 تحليل الأسعار", "📈 تنبؤات"])
    
    with tab1:
        st.subheader("تحليل أسعار المواد الخام")
        predictor = PricePredictor()
        ingredients = ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح"]
        
        for ing in ingredients:
            prices = predictor.get_ingredient_prices(ing, 30)
            if prices:
                st.write(f"**{ing}:**")
                df = pd.DataFrame(prices)
                st.line_chart(df.set_index('record_date')['price'])
    
    with tab2:
        st.subheader("تنبؤات الأسعار")
        for ing in ["ذرة صفراء", "كسب فول صويا 44%"]:
            pred = predictor.predict_price(ing, 7)
            if pred.get('prediction'):
                st.metric(
                    f"🔮 {ing}",
                    f"${pred['prediction']:.2f}",
                    delta=f"{pred['prediction'] - pred.get('current_price', 0):.2f}",
                    help=f"الثقة: {pred.get('confidence', 0)*100:.0f}%"
                )

def render_reports():
    """صفحة التقارير"""
    st.title("📜 التقارير المتقدمة")
    
    report_type = st.selectbox("نوع التقرير", ["تقرير دورة إنتاجية", "تقرير خلطات", "تقرير مالي"])
    
    if report_type == "تقرير دورة إنتاجية":
        cycle_mgr = FarmCycleManager()
        cycles = cycle_mgr.list_cycles()
        if cycles:
            cycle_names = {c['cycle_id']: f"{c['farm_name']} - {c['breed']}" for c in cycles}
            selected = st.selectbox("اختر الدورة", list(cycle_names.keys()), format_func=lambda x: cycle_names[x])
            
            if st.button("📄 إنشاء التقرير"):
                report_gen = ReportGenerator()
                report = report_gen.generate_cycle_report(selected)
                if report:
                    st.json(report)
                    # يمكن إضافة تصدير PDF هنا
        else:
            st.info("لا توجد دورات لتوليد تقرير عنها")

def render_settings():
    """صفحة الإعدادات"""
    st.title("⚙️ الإعدادات")
    
    tab1, tab2 = st.tabs(["👤 إدارة المستخدمين", "🔧 إعدادات النظام"])
    
    with tab1:
        st.subheader("إدارة المستخدمين")
        if st.session_state.user_role == 'owner':
            # إضافة مستخدم جديد
            st.markdown("#### إضافة مستخدم جديد")
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_username = st.text_input("اسم المستخدم")
                    new_password = st.text_input("كلمة المرور", type="password")
                    new_fullname = st.text_input("الاسم الكامل")
                with col2:
                    new_role = st.selectbox("الدور", ["breeder", "specialist", "manager"])
                    new_email = st.text_input("البريد الإلكتروني")
                    new_phone = st.text_input("رقم الهاتف")
                
                if st.form_submit_button("إضافة مستخدم"):
                    auth = AuthManager()
                    try:
                        auth.create_user(new_username, new_password, new_role, new_fullname, new_email, new_phone)
                        st.success("✅ تم إنشاء المستخدم بنجاح!")
                    except Exception as e:
                        st.error(f"❌ فشل إنشاء المستخدم: {e}")
        else:
            st.info("🔒 إدارة المستخدمين متاحة للمالك فقط")
    
    with tab2:
        st.subheader("إعدادات النظام")
        st.info("🔧 إعدادات متقدمة قيد التطوير")

# ==========================================
# 8. تشغيل التطبيق
# ==========================================
if __name__ == "__main__":
    main()
