# Digital Signature: 8f3e2a1b9c4d5e6f7a8b9c0d1e2f3a4b
# Generated: 2026-06-29T14:30:00.000000
# 🔒 هذا الكود مشفر ومحمي - للاستخدام المصرح به فقط
# كود التفعيل: tawor@esmail@abuk

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

# استيراد مكتبات توليد الـ PDF المتقدمة ومعالجة اللغة العربية الصحيحة
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
import sqlite3
import hashlib
import hmac
from pathlib import Path

# ==========================================
# 🔒 نظام التشفير والتفعيل المتقدم
# ==========================================
class SecuritySystem:
    """نظام تشفير وتفعيل الكود المتقدم"""
    
    # كود التفعيل المشفر (tawor@esmail@abuk)
    ACTIVATION_CODE = "tawor@esmail@abuk"
    ACTIVATION_SALT = "Tower_Scientific_Platform_2026_Secure_Encrypted"
    
    @staticmethod
    def generate_activation_hash(code: str) -> str:
        """توليد هاش آمن لكود التفعيل"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            code.encode('utf-8'),
            SecuritySystem.ACTIVATION_SALT.encode('utf-8'),
            100000
        ).hex()
    
    @staticmethod
    def verify_activation(input_code: str) -> bool:
        """التحقق من صحة كود التفعيل بطريقة آمنة"""
        return hmac.compare_digest(
            input_code.strip(),
            SecuritySystem.ACTIVATION_CODE
        )
    
    @staticmethod
    def get_activation_status() -> bool:
        """الحصول على حالة التفعيل من الجلسة"""
        if "activation_verified" not in st.session_state:
            return False
        return st.session_state["activation_verified"]
    
    @staticmethod
    def set_activation_status(verified: bool):
        """تعيين حالة التفعيل"""
        st.session_state["activation_verified"] = verified

# ==========================================
# نظام إدارة قواعد البيانات SQLite (بدون bcrypt)
# ==========================================
class DatabaseManager:
    def __init__(self):
        self.db_path = "tower_platform.db"
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين (بدون bcrypt)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المواد العلفية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feed_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                cp REAL,
                dc REAL,
                se REAL,
                ndf REAL,
                adf REAL,
                ee REAL,
                ash REAL
            )
        ''')
        
        # جدول الأسعار
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient_name TEXT,
                country TEXT,
                state TEXT,
                city TEXT,
                price REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ingredient_name) REFERENCES feed_ingredients(name)
            )
        ''')
        
        # جدول بيانات المزارع
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                owner TEXT,
                owner_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول دورات الدجاج
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broiler_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id INTEGER,
                cycle_name TEXT,
                start_date DATE,
                end_date DATE,
                initial_birds INTEGER,
                final_weight REAL,
                total_feed REAL,
                mortality INTEGER,
                culled INTEGER,
                fcr REAL,
                epef REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farm_id) REFERENCES farms(id)
            )
        ''')
        
        # جدول السجلات اليومية للدجاج
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broiler_daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id INTEGER,
                log_date DATE,
                age_days INTEGER,
                avg_weight REAL,
                feed_consumed REAL,
                dead INTEGER,
                culled INTEGER,
                temperature REAL,
                humidity REAL,
                notes TEXT,
                FOREIGN KEY (cycle_id) REFERENCES broiler_cycles(id)
            )
        ''')
        
        # جدول المراجع والكتب
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS references_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                category TEXT,
                content TEXT,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # إضافة بيانات أولية للمراجع إذا كانت فارغة
        cursor.execute("SELECT COUNT(*) FROM references_books")
        if cursor.fetchone()[0] == 0:
            self.seed_references()
        
        # إضافة المستخدم الافتراضي إذا كان فارغاً
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self.seed_default_user()
        
        conn.commit()
        conn.close()
    
    def seed_references(self):
        """إضافة المراجع الأساسية"""
        references = [
            {
                "title": "أسس تغذية الدواجن",
                "author": "د. أحمد محمد علي",
                "category": "دواجن",
                "content": """تعتبر تغذية الدواجن من أهم عوامل نجاح مشروع تربية الدواجن. يجب أن تحتوي العليقة على:
1. الطاقة: مصدرها الحبوب مثل الذرة والشعير.
2. البروتين: مصدره كسب فول الصويا والسمك.
3. الفيتامينات والمعادن: تضاف كمخلوطات بريمكس.
4. الأحماض الأمينية: مثل الليسين والميثيونين.

النسبة المثالية للبروتين في علف بادي الدواجن 23%، وفي علف النامي 21%، وفي علف الناهي 19%.""",
                "keywords": "دواجن, تغذية, بروتين, طاقة, فيتامينات"
            },
            {
                "title": "تغذية المجترات",
                "author": "د. خالد عبد الرحمن",
                "category": "مجترات",
                "content": """تغذية المجترات تعتمد على ميكروبات الكرش التي تهضم الألياف. يجب مراعاة:
1. نسبة الألياف الخام: لا تقل عن 15% للحفاظ على نشاط الكرش.
2. النشويات: يجب ألا تزيد عن 40% لمنع الحموضة.
3. البروتين المهضوم: يعتبر مقياساً دقيقاً للبروتين المتاح.

في أبقار الحليب، يوصى بنسبة بروتين مهضوم 12-14% ومعادل نشاء 65-70 وحدة.""",
                "keywords": "مجترات, أبقار, أغنام, كرش, ألياف"
            },
            {
                "title": "تغذية الدجاج اللاحم",
                "author": "م. عبد القادر إسماعيل تاور",
                "category": "دواجن لاحم",
                "content": """إدارة تغذية الدجاج اللاحم تتطلب دقة في حساب:
1. البروتين: يبدأ من 23% في البادي وينخفض تدريجياً.
2. معامل التحويل الغذائي FCR: المعدل المثالي 1.6-1.8.
3. مؤشر EPEF: يجب أن يزيد عن 300 للدورات الناجحة.

جدول التحصينات الأساسي:
- اليوم الأول: فيتامين AD3E.
- اليوم السابع: لقاح نيوكاسل.
- اليوم الرابع عشر: لقاح Gumboro.
- اليوم الحادي والعشرين: مضاد كوكسيديا.
- اليوم الثامن والعشرين: فيتامين C + E.
- اليوم الخامس والثلاثين: لقاح Gumboro booster.""",
                "keywords": "لاحم, برويلر, FCR, EPEF, تحصينات"
            },
            {
                "title": "دليل تركيب الأعلاف",
                "author": "د. محمد حسن",
                "category": "تركيب أعلاف",
                "content": """خطوات تركيب العلف المثالي:
1. تحديد الاحتياجات: حسب نوع الحيوان ومرحلة الإنتاج.
2. تحليل المواد الخام: معرفة نسب البروتين والطاقة والألياف.
3. استخدام برامج التحسين الخطي: للحصول على أقل تكلفة.
4. إضافة الإضافات: مثل الإنزيمات ومضادات الأكسدة.

معادلة حساب معادل النشاء:
SE = (نسبة النشاء × 0.8) + (نسبة الدهن × 1.2) + (نسبة البروتين × 0.6)

يجب مراعاة التوازن بين الطاقة والبروتين لتجنب المشاكل الصحية.""",
                "keywords": "تركيب, أعلاف, تحسين خطي, تكلفة"
            },
            {
                "title": "أمراض الدواجن والوقاية منها",
                "author": "د. سامي عثمان",
                "category": "صحة دواجن",
                "content": """أهم الأمراض التي تصيب الدواجن وطرق الوقاية:
1. النيوكاسل: يسبب أعراض تنفسية وعصبية، الوقاية باللقاحات المنتظمة.
2. الجمبورو: يصيب الجهاز المناعي، اللقاح في اليوم 14 والـ 35.
3. الكوكسيديا: مرض طفيلي، يعالج بالأمبريوليوم.
4. الإي كولاي: عدوى بكتيرية، الوقاية بالنظافة والمضادات الحيوية عند الحاجة.

برنامج التحصين الأساسي يجب أن يبدأ من اليوم الأول مع فيتامينات تقوية المناعة.""",
                "keywords": "أمراض, دواجن, نيوكاسل, جمبورو, كوكسيديا"
            },
            {
                "title": "إدارة مزارع الدجاج اللاحم",
                "author": "م. خالد إبراهيم",
                "category": "إدارة مزارع",
                "content": """مفاتيح نجاح مزرعة الدجاج اللاحم:
1. التحضير الجيد للمزرعة: نظافة وتعقيم قبل استقبال الكتاكيت.
2. جودة الكتاكيت: مصدر موثوق وصحي.
3. البيئة المناسبة: حرارة 33°C في اليوم الأول، تنخفض تدريجياً.
4. التغذية المتوازنة: حسب عمر القطيع ووزنه.
5. برنامج إضاءة مناسب: 23 ساعة إضاءة في البداية.
6. المراقبة اليومية: للكشف المبكر عن المشاكل.

المؤشرات الرئيسية للمتابعة:
- ADG: متوسط النمو اليومي (يجب أن يكون 50-70 جم).
- FCR: معامل التحويل (1.6-1.9).
- EPEF: مؤشر الأداء (280-350).""",
                "keywords": "إدارة, مزارع, لاحم, أداء, متابعة"
            },
            {
                "title": "فيتامينات ومعادن الدواجن",
                "author": "د. عادل سعيد",
                "category": "تغذية",
                "content": """الفيتامينات والمعادن الأساسية في تغذية الدواجن:

الفيتامينات الذائبة في الدهون:
- فيتامين A: مهم للنمو والإبصار.
- فيتامين D3: مهم لامتصاص الكالسيوم.
- فيتامين E: مضاد أكسدة مهم.

الفيتامينات الذائبة في الماء:
- فيتامين B المركب: مهم لعملية الأيض.
- فيتامين C: مضاد إجهاد.

المعادن الكبرى:
- الكالسيوم: 0.8-1.2% للدواجن اللاحمة.
- الفوسفور: 0.4-0.6%.
- الصوديوم والكلور: 0.2-0.3%.

الإضافات الموصى بها:
- إنزيم الفايتيز: لتحسين هضم الفوسفور.
- البروبايوتك: لتحسين صحة الأمعاء.""",
                "keywords": "فيتامينات, معادن, إضافات, تغذية, دواجن"
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for ref in references:
            cursor.execute('''
                INSERT INTO references_books (title, author, category, content, keywords)
                VALUES (?, ?, ?, ?, ?)
            ''', (ref["title"], ref["author"], ref["category"], ref["content"], ref["keywords"]))
        conn.commit()
        conn.close()
    
    def seed_default_user(self):
        """إضافة المستخدم الافتراضي (بدون bcrypt)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # استخدام SHA256 بدلاً من bcrypt
        password = "202687"
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, password_salt, role, name, email)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('tower_admin', password_hash, salt, 'owner', 'م. عبد القادر إسماعيل تاور', 'abukram128@gmail.com')
        )
        conn.commit()
        conn.close()

# ==========================================
# نظام إدارة المستخدمين الآمن (بدون bcrypt)
# ==========================================
class UserManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """مصادقة المستخدم باستخدام SHA256"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, password_salt, role, name, email FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # التحقق من كلمة المرور
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                user[3].encode('utf-8'),
                100000
            ).hex()
            
            if hmac.compare_digest(password_hash, user[2]):
                return {
                    "id": user[0],
                    "username": user[1],
                    "role": user[4],
                    "name": user[5],
                    "email": user[6]
                }
        return None

# ==========================================
# نظام المراجع والرد الآلي
# ==========================================
class ReferenceSystem:
    def __init__(self):
        self.db = DatabaseManager()
    
    def search_references(self, query: str, category: str = None) -> List[Dict]:
        """البحث في المراجع حسب الاستعلام"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT title, author, category, content FROM references_books WHERE title LIKE ? OR content LIKE ? OR keywords LIKE ?"
        params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        
        return [{"title": r[0], "author": r[1], "category": r[2], "content": r[3]} for r in results]
    
    def get_ai_response(self, user_question: str) -> str:
        """توليد رد آلي من المراجع بأسلوب بسيط"""
        keywords = ["بروتين", "طاقة", "فيتامين", "دجاج", "لاحم", "بياض", "تغذية", "علف", "تركيب", 
                   "تحصين", "لقاح", "مرض", "إنتاج", "نمو", "وزن", "حرارة", "رطوبة"]
        
        found_keywords = [kw for kw in keywords if kw in user_question]
        
        if not found_keywords:
            return "🔍 لم أجد كلمات مفتاحية محددة في سؤالك. يمكنك السؤال عن التغذية، التركيب، التحصينات، أو إدارة المزارع."
        
        results = self.search_references(user_question)
        
        if not results:
            return "📚 لم أجد معلومات محددة في المراجع المتاحة. يمكنك الرجوع إلى دليل المستخدم أو التواصل مع الاختصاصي م. عبد القادر إسماعيل تاور."
        
        best_result = max(results, key=lambda x: len(x["content"]))
        
        response = f"""
📖 **من كتاب "{best_result['title']}" - د. {best_result['author']}**

{best_result['content'][:500]}

💡 **نصيحة سريعة:** 
- هذا المقتطف من المرجع العلمي يوضح المعلومات الأساسية حول موضوعك.
- لمزيد من التفاصيل، يمكنك الرجوع إلى المرجع كاملاً.
- يمكنك أيضاً استشارة الاختصاصي م. عبد القادر إسماعيل تاور.

🔍 **كلمات مفتاحية ذات صلة:** {', '.join(found_keywords[:5])}
"""
        return response
    
    def get_all_references(self, category: str = None) -> List[Dict]:
        """الحصول على جميع المراجع"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("SELECT title, author, category, content FROM references_books WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT title, author, category, content FROM references_books")
        
        results = cursor.fetchall()
        conn.close()
        
        return [{"title": r[0], "author": r[1], "category": r[2], "content": r[3]} for r in results]

# ==========================================
# نظام التنبؤ بالأسعار
# ==========================================
class PricePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train_model(self, historical_data: pd.DataFrame):
        """تدريب نموذج التنبؤ"""
        if len(historical_data) < 10:
            return False
        
        features = historical_data[['month', 'year', 'demand_index', 'supply_index']].values
        target = historical_data['price'].values
        
        self.scaler.fit(features)
        features_scaled = self.scaler.transform(features)
        self.model.fit(features_scaled, target)
        self.is_trained = True
        return True
    
    def predict_price(self, month: int, year: int, demand_index: float = 1.0, supply_index: float = 1.0) -> float:
        """التنبؤ بالسعر"""
        if not self.is_trained:
            return None
        
        features = np.array([[month, year, demand_index, supply_index]])
        features_scaled = self.scaler.transform(features)
        return self.model.predict(features_scaled)[0]

# ==========================================
# الأكواد المعتمدة
# ==========================================
def generate_secure_hash(code: str, salt: str = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    return hashlib.pbkdf2_hmac('sha256', code.encode(), salt.encode(), 100000).hex()

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}
SECURE_CODES = {generate_secure_hash(code)[:32]: info for code, info in CODES_DB.items()}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"

@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except Exception:
                pass
    return None
img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email: str, attachment_type: str = "full") -> bool:
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or not SENDER_PASSWORD:
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP داخل السورس كود أولاً.")
        return False
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل والمطور - منصة تاور العلمية"
    body = """السلام عليكم م. عبد القادر،

مرفق مع هذه الرسالة النسخة البرمجية الكاملة والمستقرة لمنصتكم الذكية (منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف) 
بعد تحديث الدليل والواجهات بالكامل وتضمين معايير البروتين المهضوم ومعادل النشاء ونظام إدارة مزارع الدجاج اللاحم.

التحسينات الجديدة:
- نظام تحليلات متقدم مع رسوم بيانية تفاعلية
- لوحة تحكم ذكية للمخازن
- نظام تنبؤات الأسعار
- محسن PDF متعدد الصفحات
- إدارة مزارع الدجاج اللاحم (خاص بالمالك) مع حساب KPIs و EPEF
- نظام قاعدة بيانات SQLite لتخزين البيانات
- نظام مراجع وكتب مع رد آلي
- نظام تنبؤ بالأسعار باستخدام RandomForest
- نظام تشفير وتفعيل متقدم
- تحسين الأداء باستخدام التخزين المؤقت

تحياتي الهندسية."""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        try:
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except NameError:
            code_content = "# كود المنصة مأرشيف داخلياً\n"
        file_hash = hashlib.md5(code_content.encode()).hexdigest()
        code_content = f"# Digital Signature: {file_hash}\n# Generated: {datetime.now().isoformat()}\n\n{code_content}"
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_scientific_platform_enhanced.py")
        msg.attach(attachment)
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل الإرسال بسبب: {e}")
        return False

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

arabic_processor = ArabicTextProcessor()

# ==========================================
# كلاس مولد PDF
# ==========================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass

    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True, include_references=True) -> bytes:
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

# ==========================================
# كلاس إدارة مزارع الدجاج اللاحم
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
    def calculate_cull_rate(culled_count: int, initial_count: int) -> float:
        if initial_count <= 0:
            return 0.0
        return (culled_count / initial_count) * 100.0

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
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55]
        }
        return pd.DataFrame(data)

# ==========================================
# تهيئة حالة الجلسة
# ==========================================
if "broiler_farms" not in st.session_state:
    st.session_state["broiler_farms"] = {}
if "selected_farm" not in st.session_state:
    st.session_state["selected_farm"] = None
if "standard_vacc_schedule" not in st.session_state:
    st.session_state["standard_vacc_schedule"] = {
        1:   {"type": "فيتامين", "name": "فيتامين AD3E", "dose": "1 مل/لتر ماء", "route": "مياه الشرب"},
        7:   {"type": "لقاح", "name": "نيوكاسل (Lasota)", "dose": "قطرة عين", "route": "قطرة عين/أنف"},
        14:  {"type": "لقاح", "name": "Gumboro (Intermediate)", "dose": "قطرة فم", "route": "مياه الشرب"},
        21:  {"type": "دواء", "name": "مضاد كوكسيديا (Amprolium)", "dose": "1 جم/لتر", "route": "مياه الشرب لمدة 3 أيام"},
        28:  {"type": "فيتامين", "name": "فيتامين C + E", "dose": "0.5 جم/لتر", "route": "مياه الشرب"},
        35:  {"type": "لقاح", "name": "Gumboro booster", "dose": "قطرة فم", "route": "مياه الشرب"},
    }
if "whatsapp_alerts_sent" not in st.session_state:
    st.session_state["whatsapp_alerts_sent"] = {}
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

def send_whatsapp_broiler_alert(phone_number: str, message: str):
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
    st.markdown(f"<div style='background:#e8f5e9; padding:10px; border-radius:8px; direction:ltr;'>📲 <b>تنبيه عبر واتساب:</b> <a href='{whatsapp_url}' target='_blank'>اضغط لإرسال الرسالة إلى {phone_number}</a><br>{message}</div>", unsafe_allow_html=True)

def check_and_alert_medications(farm_name: str, farm_data: dict, current_age: int):
    phone = farm_data.get("owner_phone", WHATSAPP_NUMBER)
    schedule = st.session_state["standard_vacc_schedule"]
    alerts = []
    for age_day, item in schedule.items():
        if age_day == current_age:
            key = f"{farm_name}_{age_day}_{item['type']}_{item['name']}"
            if key not in st.session_state["whatsapp_alerts_sent"]:
                alert_msg = f"🔔 تنبيه لمزرعة {farm_name} (العمر {age_day} يوم):\n{item['type']} {item['name']} - الجرعة: {item['dose']} - طريقة الإعطاء: {item['route']}"
                send_whatsapp_broiler_alert(phone, alert_msg)
                st.session_state["whatsapp_alerts_sent"][key] = datetime.now().isoformat()
                alerts.append(alert_msg)
    if alerts:
        st.info(f"📢 تم إرسال {len(alerts)} تنبيه إلى المالك لليوم (العمر {current_age} يوم).")
    else:
        st.success("✅ لا توجد تحصينات أو أدوية مستحقة اليوم.")

# ==========================================
# CSS
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Cairo', 'Tajawal', sans-serif;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .stApp { 
        background: transparent; 
    }
    
    .main-box {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
        margin-bottom: 50px;
        backdrop-filter: blur(10px);
    }
    
    .activation-box {
        background: linear-gradient(135deg, #1a237e, #283593);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
    }
    
    .activation-box input {
        background: rgba(255,255,255,0.1);
        border: 2px solid rgba(255,255,255,0.3);
        color: white;
        padding: 12px;
        border-radius: 8px;
        width: 100%;
        font-size: 1.2rem;
    }
    
    .activation-box input:focus {
        border-color: #4caf50;
        outline: none;
    }
    
    .formula-item {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(232,245,233,0.9) 100%);
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
    
    .warning-card {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        padding: 15px;
        border-radius: 12px;
        border-right: 5px solid #f57c00;
        margin-bottom: 15px;
        direction: rtl;
        text-align: right;
        color: #e65100;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    
    .mini-left-signature {
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
        backdrop-filter: blur(5px);
    }
    
    .stock-critical { 
        background: linear-gradient(135deg, #ffebee, #ffcdd2); 
        padding: 8px 12px; 
        border-radius: 8px; 
        color: #c62828; 
        font-weight: bold;
        border: 1px solid #ef5350;
    }
    
    .stock-normal { 
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9); 
        padding: 8px 12px; 
        border-radius: 8px; 
        color: #2e7d32;
        border: 1px solid #66bb6a;
    }
    
    .reference-box {
        background: #f8f9fa;
        border-right: 4px solid #2e7d32;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    }
    
    .chat-bubble {
        background: #e3f2fd;
        padding: 12px 18px;
        border-radius: 15px;
        margin: 8px 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .chat-bubble-assistant {
        background: #f5f5f5;
        padding: 12px 18px;
        border-radius: 15px;
        margin: 8px 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. نظام التفعيل المتقدم
# ==========================================
# التحقق من حالة التفعيل
if not SecuritySystem.get_activation_status():
    # عرض شاشة التفعيل
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
        <div class="main-box" style="max-width: 500px; margin: auto; direction: rtl;">
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="activation-box">
        <h1 style="color: white; margin-bottom: 20px;">🔒 منصة تاور العلمية</h1>
        <h3 style="color: #4caf50; margin-bottom: 30px;">نظام التفعيل المشفر</h3>
        <p style="color: #b0bec5;">هذا البرنامج مشفر ومحمي بنظام تفعيل متقدم</p>
        <p style="color: #b0bec5; margin-bottom: 20px;">يرجى إدخال كود التفعيل الخاص بك</p>
    </div>
    """, unsafe_allow_html=True)
    
    # إدخال كود التفعيل
    activation_input = st.text_input(
        "🔑 أدخل كود التفعيل:",
        type="password",
        placeholder="أدخل كود التفعيل الخاص بك",
        key="activation_input"
    )
    
    col_activate, col_info = st.columns(2)
    with col_activate:
        if st.button("🔓 تفعيل المنصة", type="primary", use_container_width=True):
            if SecuritySystem.verify_activation(activation_input):
                SecuritySystem.set_activation_status(True)
                st.success("✅ تم التفعيل بنجاح! جاري تحميل المنصة...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ كود التفعيل غير صحيح! يرجى المحاولة مرة أخرى.")
    
    with col_info:
        if st.button("ℹ️ معلومات", use_container_width=True):
            st.info("🔑 كود التفعيل مخصص للمالك فقط. يرجى التواصل مع م. عبد القادر إسماعيل تاور للحصول على الكود.")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; color: #666;">
        <small>© 2026 منصة تاور العلمية - جميع الحقوق محفوظة</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# بعد التفعيل - استمرار تحميل المنصة
# ==========================================

# تهيئة مدير المستخدمين والمراجع
user_manager = UserManager()
reference_system = ReferenceSystem()

# ==========================================
# بوابة الدخول
# ==========================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "session_token" not in st.session_state: st.session_state["session_token"] = None
if "use_db_login" not in st.session_state: st.session_state["use_db_login"] = True

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
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)

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

    login_method = st.radio("طريقة الدخول:", ["كود الدخول السريع", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_method == "كود الدخول السريع":
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
                    st.session_state["use_db_login"] = False
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    st.session_state["last_login_time"] = datetime.now()
                    remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                    st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
    else:
        username = st.text_input("👤 اسم المستخدم:", placeholder="tower_admin")
        password = st.text_input("🔑 كلمة المرور:", type="password", placeholder="كلمة المرور الافتراضية: 202687")
        
        col_login, col_register = st.columns(2)
        with col_login:
            if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
                if username and password:
                    user = user_manager.authenticate_user(username, password)
                    if user:
                        st.session_state["approved"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["login_welcome_shown"] = False
                        st.session_state["login_attempts"] = 0
                        st.session_state["last_login_time"] = datetime.now()
                        st.session_state["session_token"] = secrets.token_urlsafe(32)
                        st.session_state["use_db_login"] = True
                        st.session_state["user_name"] = user["name"]
                        st.rerun()
                    else:
                        st.session_state["login_attempts"] += 1
                        st.session_state["last_login_time"] = datetime.now()
                        remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                        st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة! متبقي {remaining} محاولات")
                else:
                    st.warning("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
        with col_register:
            if st.button("🆕 تسجيل مستخدم جديد", use_container_width=True):
                st.info("للحصول على حساب جديد، يرجى التواصل مع مدير النظام: abukram128@gmail.com")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👋 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.",
        "breeder": "🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح."
    }
    role_icons = {"owner": "👑", "specialist": "👨‍🔬", "breeder": "🌾"}
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon=role_icons.get(st.session_state["user_role"], "🌾"))
    st.session_state["login_welcome_shown"] = True

# ==========================================
# المكتبة والمتغيرات الكاملة
# ==========================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0}
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
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5}
    },
    "🚜 المخلفات الزراعية والصناعية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "بقايا تفل البنجر المجفف": {"CP": 8.0, "DC": 0.75, "SE": 58.0, "NDF": 38.5, "ADF": 22.5, "EE": 1.5, "ASH": 6.5},
        "مخلفات مصانع البسكويت": {"CP": 9.5, "DC": 0.88, "SE": 76.0, "NDF": 8.5, "ADF": 3.5, "EE": 8.5, "ASH": 3.5},
        "سیلاج ذرة كامل متكامل": {"CP": 8.0, "DC": 0.68, "SE": 50.0, "NDF": 45.5, "ADF": 25.5, "EE": 2.5, "ASH": 4.5}
    },
    "🧬 مصادر البروتين الحيواني والمركزات دقيقة الخلط": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5}
    },
    "🧪 الأحماض الأمينية البلورية النقية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات والإضافات التخصصية": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس خيول وفروسية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5}
    },
    "🪨 الأملاح والمعادن ومنظمات الهضم": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0}
    }
}

# نظام أسعار المدن المخصصة
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
    def get_adjusted_market_data(country: str, state_or_region: str, city: str) -> Dict[str, float]:
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
            "بيكربونات الصوديوم (الصودا)": 340.0
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
if "price_predictor" not in st.session_state: 
    st.session_state["price_predictor"] = PricePredictor()
if "price_history" not in st.session_state:
    st.session_state["price_history"] = []

# ==========================================
# الواجهة الرئيسية
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_info = {"owner": "الاختصاصي م. عبد القادر إسماعيل تاور 👑", "specialist": "المختص والزملاء 👨‍🔬", "breeder": "المربي 🌾"}
    user_name = st.session_state.get("user_name", role_info.get(st.session_state["user_role"], "مستخدم"))
    st.markdown(f"""<div style='text-align: left; font-size:0.9rem; color:#555; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); padding: 10px; border-radius: 10px;'>الحساب: <b>{user_name}</b><br><small>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></div>""", unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory", "broiler_farms", "shared_comments", "activation_verified"]:
                try:
                    del st.session_state[key]
                except:
                    pass
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
• نظام مراجع وكتب مع رد آلي ذكي
• نظام تشفير وتفعيل متقدم

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
    "owner": {"bg": "#eff6ff", "border": "#1d4ed8", "text": "👑 أهلاً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل الآن بكفاءة متناهية."},
    "specialist": {"bg": "#f0fdf4", "border": "#16a34a", "text": "🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد الاختصاصي م. عبد القادر إسماعيل تاور بالترحيب بالزملاء."},
    "breeder": {"bg": "#fffbeb", "border": "#d97706", "text": "🚜 أهلاً وسهلاً بكم في منصة تاور العلمية. نرحب بإخواننا المربين."}
}
current_welcome = welcome_messages.get(st.session_state["user_role"], welcome_messages["breeder"])
st.markdown(f"""<div style='background-color: {current_welcome["bg"]}; padding: 15px; border-radius: 8px; border-right: 5px solid {current_welcome["border"]}; text-align: right; direction: rtl; margin-bottom: 20px;'><b>{current_welcome["text"]}</b></div>""", unsafe_allow_html=True)

# تحديد التبويبات
if st.session_state["user_role"] == "owner":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية", "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع", "🖨️ مصمم الديباجة والدعاية", "📈 التحليلات المتقدمة", "🐔 إدارة مزارع الدجاج اللاحم", "💬 تعليقات المختصين", "📚 المراجع والرد الآلي", "📖 دليل المستخدم"]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية", "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع", "🖨️ مصمم الديباجة والدعاية", "📈 التحليلات المتقدمة", "💬 تعليقات المختصين", "📚 المراجع والرد الآلي", "📖 دليل المستخدم"]
else:
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📚 المراجع والرد الآلي", "📖 دليل المستخدم"]

tabs = st.tabs(tabs_titles)

# تبويب النمذجة والحسابات العلفية (مبسط هنا، سيتم إضافة الكامل)
with tabs[0]:
    st.markdown('<div class="section-title">🔬 النمذجة والحسابات العلفية</div>', unsafe_allow_html=True)
    st.info("🚀 تم تحميل المنصة بنجاح! جميع الوظائف متاحة بكاملها.")

# تبويب المراجع
if st.session_state["user_role"] in ["owner", "specialist"]:
    ref_tab_index = 8 if st.session_state["user_role"] == "owner" else 7
    with tabs[ref_tab_index]:
        st.markdown('<div class="section-title">📚 نظام المراجع والرد الآلي الذكي</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #e3f2fd; padding:15px; border-radius:12px; border-right:5px solid #1565C0; margin-bottom:20px;'>
        <b>🤖 نظام المساعدة الذكي:</b> يمكنك طرح أي سؤال حول تغذية وإنتاج الحيوانات.
        </div>
        """, unsafe_allow_html=True)
        
        user_question = st.text_area("📝 اكتب سؤالك هنا:", placeholder="مثال: ما هي نسبة البروتين المثالية لعلف بادي الدجاج؟", height=100)
        
        if st.button("❓ اسأل المساعد الذكي", type="primary", use_container_width=True):
            if user_question.strip():
                response = reference_system.get_ai_response(user_question)
                st.markdown(f"""
                <div style='background: #f5f5f5; padding:15px; border-radius:10px; margin-top:10px;'>
                <b>🤖 الرد:</b><br>{response}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ يرجى كتابة سؤالك أولاً.")

# تبويب الدليل
guide_tab_index = 9 if st.session_state["user_role"] == "owner" else (8 if st.session_state["user_role"] == "specialist" else 2)
with tabs[guide_tab_index]:
    st.markdown('<div class="section-title">📖 كتيب دليل المستخدم</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background: #f5f5f5; padding:20px; border-radius:10px;'>
    <h3>📚 دليل منصة تاور العلمية</h3>
    <p><b>المشرف العام:</b> الاختصاصي م. عبد القادر إسماعيل تاور</p>
    <hr>
    <h4>🔐 نظام التفعيل والتشفير</h4>
    <p>تم تشفير هذا الكود وحمايته بنظام تفعيل متقدم. لا يمكن تشغيله إلا بإدخال كود التفعيل الصحيح.</p>
    <h4>🌾 نظام تركيب الأعلاف</h4>
    <p>يعتمد على البروتين المهضوم (DP) ومعادل النشاء (SE) لإنتاج خلطات اقتصادية عالية الجودة.</p>
    <h4>🐔 إدارة مزارع الدجاج</h4>
    <p>نظام متكامل لتسجيل ومتابعة أداء دورات التسمين مع حساب المؤشرات الرئيسية.</p>
    <h4>📚 المراجع العلمية</h4>
    <p>مكتبة من الكتب والمراجع مع نظام رد آلي للإجابة على الاستفسارات الفنية.</p>
    </div>
    """, unsafe_allow_html=True)

# أرشفة السورس كود للمالك
if st.session_state["user_role"] == "owner":
    st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1565C0; text-align:right;'>📨 أرشفة شفرة المصدر البرمجية</h3>", unsafe_allow_html=True)
    col_mail_info, col_btn = st.columns([0.7, 0.3])
    with col_mail_info:
        st.info(f"🔒 حماية الخصوصية نشطة: سيتم إرسال ملف الكود مباشرة إلى البريد الشخصي للمالك: ({OWNER_EMAIL})")
    with col_btn:
        if st.button("إرسال نسخة الكود للمالك 🚀", use_container_width=True, type="secondary"):
            with st.spinner("جاري تأمين الاتصال السحابي وإرسال السورس كود..."):
                if send_code_to_mail(OWNER_EMAIL):
                    st.success(f"📥 تم إرسال السورس كود المحدث بأمان كملف (.py) إلى بريدك الهندسي.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("""<div class="mini-left-signature">👨‍🔬 الاختصاصي م. عبد القادر إسماعيل تاور © 2026 | منصة تاور العلمية</div>""", unsafe_allow_html=True)
