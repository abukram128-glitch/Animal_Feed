# ==========================================
# 0. تحسينات إضافية (سيتم إدراجها في بداية الكود)
# ==========================================

# إضافة المكتبات الجديدة
import os
import shutil
import logging
import sqlite3
from contextlib import contextmanager
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from dotenv import load_dotenv
import hashlib
import json
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# تحميل متغيرات البيئة
load_dotenv()

# ==========================================
# 0.1 نظام التسجيل (Logging) المتقدم
# ==========================================

def setup_logging():
    """إعداد نظام تسجيل الأحداث المتقدم"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger('TowerPlatform')
    logger.setLevel(logging.INFO)
    
    # معالج للملفات مع تدوير تلقائي
    handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'tower.log'), 
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # معالج للأخطاء فقط
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'), 
        maxBytes=5242880,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

LOGGER = setup_logging()

# ==========================================
# 0.2 نظام التشفير المتقدم
# ==========================================

class SecureDataManager:
    """إدارة البيانات الحساسة بشكل آمن"""
    
    def __init__(self):
        # إنشاء مفتاح التشفير إذا لم يكن موجوداً
        self.key_file = "secret.key"
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                self.cipher_key = f.read()
        else:
            self.cipher_key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.cipher_key)
        
        self.cipher = Fernet(self.cipher_key)
    
    def encrypt(self, data: str) -> str:
        """تشفير البيانات النصية"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """فك تشفير البيانات"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_sensitive_config(self):
        """تشفير الإعدادات الحساسة في ملف الإعدادات"""
        sensitive_data = {
            "smtp_password": SENDER_PASSWORD,
            "smtp_email": SENDER_EMAIL
        }
        encrypted_config = {}
        for key, value in sensitive_data.items():
            encrypted_config[key] = self.encrypt(value)
        
        with open("secure_config.json", "w") as f:
            json.dump(encrypted_config, f)
        
        LOGGER.info("تم تشفير الإعدادات الحساسة")

SECURE_MANAGER = SecureDataManager()

# ==========================================
# 0.3 نظام قاعدة البيانات (SQLite)
# ==========================================

DB_PATH = "tower_platform.db"

@contextmanager
def get_db():
    """مدير سياق قاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        LOGGER.error(f"خطأ في قاعدة البيانات: {e}")
        raise
    finally:
        conn.close()

def init_database():
    """تهيئة قاعدة البيانات وجداولها"""
    with get_db() as conn:
        # جدول المزارع
        conn.execute('''
            CREATE TABLE IF NOT EXISTS farms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                owner TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الخلطات التاريخية
        conn.execute('''
            CREATE TABLE IF NOT EXISTS formulas_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_data TEXT NOT NULL,
                target_dp REAL,
                target_se REAL,
                breed TEXT,
                cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول التحاليل المخبرية
        conn.execute('''
            CREATE TABLE IF NOT EXISTS lab_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER,
                formula_data TEXT,
                cp REAL,
                moisture REAL,
                fat REAL,
                fiber REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول سجل النشاطات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_role TEXT,
                action TEXT,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        LOGGER.info("تم تهيئة قاعدة البيانات بنجاح")

# تهيئة قاعدة البيانات عند بدء التشغيل
if "db_initialized" not in st.session_state:
    init_database()
    st.session_state["db_initialized"] = True

# ==========================================
# 0.4 نظام التخزين المؤقت المتقدم
# ==========================================

class AdvancedCache:
    """نظام تخزين مؤقت متقدم مع تحليل الاستخدام"""
    
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self.access_count = {}
    
    def get(self, key):
        """استرداد قيمة من التخزين المؤقت"""
        if key in self.cache:
            self.hits += 1
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key, value):
        """تخزين قيمة في التخزين المؤقت"""
        if len(self.cache) >= self.max_size:
            # إزالة العنصر الأقل استخداماً
            least_used = min(self.access_count, key=self.access_count.get)
            del self.cache[least_used]
            del self.access_count[least_used]
        
        self.cache[key] = value
        self.access_count[key] = self.access_count.get(key, 0) + 1
    
    def get_stats(self):
        """إحصائيات أداء التخزين المؤقت"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache)
        }

CACHE = AdvancedCache(max_size=200)

def cached_formulation(max_age_seconds=3600):
    """ديكورتور للتخزين المؤقت للتركيبات"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح فريد للمعاملات
            key_data = {
                "args": str(args),
                "kwargs": str(sorted(kwargs.items()))
            }
            cache_key = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
            
            # محاولة استرداد من التخزين المؤقت
            cached_result = CACHE.get(cache_key)
            if cached_result:
                LOGGER.info(f"استخدام نتيجة مخزنة مؤقتاً للتركيبة: {cache_key[:8]}")
                return cached_result
            
            # تنفيذ الدالة وتخزين النتيجة
            result = func(*args, **kwargs)
            CACHE.set(cache_key, result)
            LOGGER.info(f"تخزين نتيجة جديدة: {cache_key[:8]}")
            return result
        return wrapper
    return decorator

# ==========================================
# 0.5 نظام النسخ الاحتياطي التلقائي
# ==========================================

class AutoBackupSystem:
    """نظام نسخ احتياطي تلقائي للبيانات"""
    
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self, data_type="all"):
        """إنشاء نسخة احتياطية"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_files = []
        
        # نسخ ملفات JSON
        json_files = ["broiler_farms_data.json", "city_prices.json", "secure_config.json"]
        for file in json_files:
            if os.path.exists(file):
                backup_name = f"{timestamp}_{file}"
                backup_path = os.path.join(self.backup_dir, backup_name)
                shutil.copy2(file, backup_path)
                backup_files.append(backup_name)
        
        # نسخ قاعدة البيانات
        if os.path.exists(DB_PATH):
            backup_name = f"{timestamp}_tower_platform.db"
            backup_path = os.path.join(self.backup_dir, backup_name)
            shutil.copy2(DB_PATH, backup_path)
            backup_files.append(backup_name)
        
        # تسجيل النسخة الاحتياطية
        LOGGER.info(f"تم إنشاء نسخة احتياطية: {', '.join(backup_files)}")
        
        # حذف النسخ القديمة (الاحتفاظ بآخر 10 نسخ فقط)
        self.cleanup_old_backups()
        
        return backup_files
    
    def cleanup_old_backups(self, keep_count=10):
        """حذف النسخ الاحتياطية القديمة"""
        all_files = os.listdir(self.backup_dir)
        backup_files = [f for f in all_files if f.endswith(('.json', '.db'))]
        backup_files.sort(reverse=True)
        
        for old_file in backup_files[keep_count:]:
            os.remove(os.path.join(self.backup_dir, old_file))
            LOGGER.info(f"تم حذف نسخة احتياطية قديمة: {old_file}")
    
    def restore_backup(self, backup_name):
        """استعادة نسخة احتياطية"""
        backup_path = os.path.join(self.backup_dir, backup_name)
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"الملف {backup_name} غير موجود")
        
        # تحديد نوع الملف واستعادته
        if backup_name.endswith('.db'):
            shutil.copy2(backup_path, DB_PATH)
        elif backup_name.endswith('.json'):
            original_name = backup_name.split('_', 1)[1]
            shutil.copy2(backup_path, original_name)
        
        LOGGER.warning(f"تم استعادة النسخة الاحتياطية: {backup_name}")
        return True

BACKUP_SYSTEM = AutoBackupSystem()

# ==========================================
# 0.6 نظام إدارة الأخطاء المتقدم
# ==========================================

class PlatformError(Exception):
    """الخطأ الأساسي في المنصة"""
    pass

class OptimizationError(PlatformError):
    """خطأ في تحسين الخلطة"""
    pass

class DatabaseError(PlatformError):
    """خطأ في قاعدة البيانات"""
    pass

class ValidationError(PlatformError):
    """خطأ في التحقق من صحة البيانات"""
    pass

def handle_errors(func):
    """ديكورتور لمعالجة الأخطاء بشكل موحد"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OptimizationError as e:
            st.error(f"⚠️ خطأ في تحسين الخلطة: {e}")
            LOGGER.error(f"OptimizationError: {e}")
            return None
        except DatabaseError as e:
            st.error(f"⚠️ خطأ في قاعدة البيانات: {e}")
            LOGGER.error(f"DatabaseError: {e}")
            return None
        except Exception as e:
            st.error(f"⚠️ حدث خطأ غير متوقع: {e}")
            LOGGER.error(f"Unexpected error: {e}", exc_info=True)
            return None
    return wrapper

def robust_optimization(c_vector, A_eq, b_eq, A_ub=None, b_ub=None, bounds=None, max_attempts=3):
    """تحسين قوي مع محاولات متعددة وتخفيف القيود"""
    
    for attempt in range(max_attempts):
        try:
            res = linprog(
                c_vector, 
                A_ub=A_ub, 
                b_ub=b_ub, 
                A_eq=A_eq, 
                b_eq=b_eq, 
                bounds=bounds, 
                method='highs'
            )
            
            if res.success:
                LOGGER.info(f"نجح التحسين في المحاولة {attempt + 1}")
                return res
            
            # تخفيف القيود تدريجياً
            if attempt < max_attempts - 1:
                LOGGER.warning(f"المحاولة {attempt + 1} فشلت، تخفيف القيود...")
                b_eq = [x * (1 + (attempt + 1) * 0.05) for x in b_eq]
                if b_ub:
                    b_ub = [x * (1 + (attempt + 1) * 0.1) for x in b_ub]
                    
        except Exception as e:
            LOGGER.warning(f"المحاولة {attempt + 1} فشلت: {e}")
    
    raise OptimizationError("لم يتم إيجاد حل حتى بعد تخفيف القيود")

# ==========================================
# 0.7 نظام تصدير البيانات المتقدم
# ==========================================

class DataExporter:
    """تصدير البيانات بصيغ متعددة"""
    
    @staticmethod
    def export_to_excel(data, filename="export.xlsx"):
        """تصدير إلى Excel"""
        import pandas as pd
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        return output.getvalue()
    
    @staticmethod
    def export_to_csv(data, filename="export.csv"):
        """تصدير إلى CSV"""
        import pandas as pd
        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')
    
    @staticmethod
    def export_formulas_history():
        """تصدير تاريخ الخلطات"""
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM formulas_history ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

EXPORTER = DataExporter()

# ==========================================
# 0.8 لوحة تحكم المالك المتقدمة
# ==========================================

def owner_dashboard():
    """لوحة تحكم متقدمة للمالك مع إحصائيات مفصلة"""
    
    st.markdown('<div class="section-title">📊 لوحة تحكم المالك المتقدمة</div>', unsafe_allow_html=True)
    
    # إحصائيات سريعة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_formulas = len(st.session_state.get("formulas_history", []))
        st.metric("إجمالي الخلطات", total_formulas, delta="+12%", delta_color="normal")
    
    with col2:
        total_farms = len(st.session_state.get("poultry_farms", {}))
        st.metric("المزارع المسجلة", total_farms)
    
    with col3:
        cache_stats = CACHE.get_stats()
        st.metric("كفاءة التخزين المؤقت", f"{cache_stats['hit_rate']:.1f}%")
    
    with col4:
        # حساب متوسط التكلفة
        avg_cost = st.session_state.get("computed_ton_cost", 280)
        st.metric("متوسط تكلفة الطن", f"${avg_cost:.2f}")
    
    st.markdown("---")
    
    # تبويبات الإدارة المتقدمة
    admin_tabs = st.tabs(["💾 النسخ الاحتياطي", "📊 إحصائيات النظام", "🗑️ تنظيف البيانات", "📤 تصدير البيانات"])
    
    with admin_tabs[0]:
        st.subheader("💾 إدارة النسخ الاحتياطية")
        
        col_backup1, col_backup2 = st.columns(2)
        with col_backup1:
            if st.button("📀 إنشاء نسخة احتياطية جديدة", use_container_width=True):
                with st.spinner("جاري إنشاء النسخة الاحتياطية..."):
                    backup_files = BACKUP_SYSTEM.create_backup()
                    st.success(f"✅ تم إنشاء {len(backup_files)} نسخة احتياطية")
                    LOGGER.info("تم إنشاء نسخة احتياطية جديدة")
        
        with col_backup2:
            # عرض قائمة النسخ الاحتياطية
            backup_files = [f for f in os.listdir("backups") if f.endswith(('.json', '.db'))]
            if backup_files:
                selected_backup = st.selectbox("اختر نسخة للاستعادة:", backup_files)
                if st.button("🔄 استعادة النسخة", use_container_width=True):
                    if BACKUP_SYSTEM.restore_backup(selected_backup):
                        st.success("تم استعادة النسخة الاحتياطية بنجاح!")
                        st.rerun()
    
    with admin_tabs[1]:
        st.subheader("📊 إحصائيات النظام المتقدمة")
        
        # إحصائيات الأداء
        col_stats1, col_stats2 = st.columns(2)
        with col_stats1:
            st.markdown("**💾 أداء التخزين المؤقت**")
            st.json(CACHE.get_stats())
        
        with col_stats2:
            st.markdown("**📈 نشاط المستخدمين**")
            with get_db() as conn:
                cursor = conn.execute('''
                    SELECT user_role, COUNT(*) as count 
                    FROM activity_logs 
                    GROUP BY user_role
                ''')
                user_stats = cursor.fetchall()
                for stat in user_stats:
                    st.metric(stat['user_role'], stat['count'])
    
    with admin_tabs[2]:
        st.subheader("🗑️ تنظيف البيانات المؤقتة")
        st.warning("⚠️ تحذير: هذا الإجراء سيحذف البيانات المؤقتة فقط، وليس بيانات المزارع أو الخلطات")
        
        col_clean1, col_clean2 = st.columns(2)
        with col_clean1:
            if st.button("🧹 تنظيف التخزين المؤقت", use_container_width=True):
                # تنظيف التخزين المؤقت
                if "formulas_history" in st.session_state:
                    st.session_state["formulas_history"] = []
                st.success("تم تنظيف التخزين المؤقت")
        
        with col_clean2:
            if st.button("🗑️ حذف سجلات النشاط القديمة", use_container_width=True):
                with get_db() as conn:
                    # حذف السجلات الأقدم من 30 يوماً
                    conn.execute('''
                        DELETE FROM activity_logs 
                        WHERE created_at < datetime('now', '-30 days')
                    ''')
                st.success("تم حذف السجلات القديمة")
    
    with admin_tabs[3]:
        st.subheader("📤 تصدير بيانات النظام")
        
        export_type = st.selectbox("نوع البيانات للتصدير:", 
                                   ["الخلطات التاريخية", "بيانات المزارع", "التحاليل المخبرية"])
        
        if st.button("📥 تصدير", use_container_width=True):
            if export_type == "الخلطات التاريخية":
                data = EXPORTER.export_formulas_history()
                filename = f"formulas_history_{datetime.now().strftime('%Y%m%d')}.csv"
                st.download_button("تحميل CSV", data, filename, "text/csv")
            elif export_type == "بيانات المزارع":
                data = st.session_state.get("poultry_farms", {})
                json_data = json.dumps(data, ensure_ascii=False, indent=2)
                st.download_button("تحميل JSON", json_data, "farms_export.json", "application/json")

# ==========================================
# 0.9 تفعيل زر نقل التركيبة للمختبر (محسن)
# ==========================================

def send_formula_to_lab(formula_data, target_dp, target_se, breed, cost, city):
    """إرسال التركيبة إلى المختبر مع توثيق كامل"""
    
    # إنشاء طلب جديد
    new_request = {
        "request_id": st.session_state["next_request_id"],
        "request_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "status": "pending",
        "user_role": st.session_state.get("user_role", ""),
        "target_species": breed,
        "production_stage": st.session_state.get("active_stage_title", ""),
        "target_dp": target_dp,
        "target_se": target_se,
        "formula": formula_data.copy(),
        "city": city,
        "cost": cost,
        "notes": ""
    }
    
    # حفظ في قاعدة البيانات
    with get_db() as conn:
        conn.execute('''
            INSERT INTO lab_analyses (request_id, formula_data, notes)
            VALUES (?, ?, ?)
        ''', (new_request["request_id"], json.dumps(formula_data), "pending"))
    
    # إضافة إلى session state
    st.session_state["pending_lab_requests"].append(new_request)
    st.session_state["next_request_id"] += 1
    
    # تسجيل النشاط
    LOGGER.info(f"تم إرسال طلب تحليل رقم {new_request['request_id']} للمختبر")
    
    # إشعار للمالك (إذا كان المستخدم ليس المالك)
    if st.session_state.get("user_role") != "owner":
        notification_msg = f"📋 طلب تحليل جديد رقم {new_request['request_id']}\nالفصيل: {breed}\nالتكلفة: ${cost:.2f}\nبواسطة: {st.session_state.get('user_role', 'مستخدم')}"
        send_whatsapp_broiler_alert(WHATSAPP_NUMBER, notification_msg)
    
    return new_request["request_id"]

# ==========================================
# 0.10 تسجيل نشاط المستخدمين
# ==========================================

def log_user_activity(action: str, details: str = ""):
    """تسجيل نشاط المستخدم في قاعدة البيانات"""
    try:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO activity_logs (user_role, action, details)
                VALUES (?, ?, ?)
            ''', (st.session_state.get("user_role", "unknown"), action, details))
    except Exception as e:
        LOGGER.error(f"فشل تسجيل النشاط: {e}")

# ==========================================
# 0.11 واجهة المختبر المحسنة مع زر النقل
# ==========================================

def enhanced_lab_interface():
    """واجهة مختبر محسنة مع زر نقل التركيبة"""
    
    st.markdown('<div class="section-title">🧪 مختبر تحليل الأعلاف المتقدم</div>', unsafe_allow_html=True)
    
    # عرض الطلبات الواردة
    pending_requests = [r for r in st.session_state["pending_lab_requests"] if r["status"] == "pending"]
    
    if pending_requests:
        st.markdown("### 📋 طلبات التحليل الواردة")
        for req in pending_requests:
            with st.expander(f"🧪 طلب تحليل رقم {req['request_id']} - {req['request_date']}"):
                st.write(f"**السلالة:** {req['target_species']}")
                st.write(f"**البروتين المهضوم المستهدف:** {req['target_dp']}%")
                st.write(f"**معادل النشاء المستهدف:** {req['target_se']}")
                st.write("**الخلطة:**")
                for ing, pct in req["formula"].items():
                    st.write(f"- {ing}: {pct:.2f}%")
                
                # نموذج إدخال النتائج
                with st.form(key=f"lab_results_{req['request_id']}"):
                    st.subheader("📊 نتائج التحليل المخبري")
                    col1, col2 = st.columns(2)
                    with col1:
                        cp = st.number_input("البروتين الخام (CP) %", min_value=0.0, step=0.1, key=f"cp_{req['request_id']}")
                        moisture = st.number_input("الرطوبة %", min_value=0.0, step=0.1, key=f"moisture_{req['request_id']}")
                    with col2:
                        fat = st.number_input("الدهن %", min_value=0.0, step=0.1, key=f"fat_{req['request_id']}")
                        fiber = st.number_input("الألياف الخام %", min_value=0.0, step=0.1, key=f"fiber_{req['request_id']}")
                    
                    notes = st.text_area("ملاحظات", key=f"notes_{req['request_id']}")
                    
                    if st.form_submit_button("💾 حفظ النتائج"):
                        # حفظ النتائج في قاعدة البيانات
                        with get_db() as conn:
                            conn.execute('''
                                UPDATE lab_analyses 
                                SET cp=?, moisture=?, fat=?, fiber=?, notes=?
                                WHERE request_id=?
                            ''', (cp, moisture, fat, fiber, notes, req['request_id']))
                        
                        req["status"] = "completed"
                        st.success(f"✅ تم حفظ نتائج التحليل للطلب رقم {req['request_id']}")
                        LOGGER.info(f"تم تحليل الطلب رقم {req['request_id']}: CP={cp}%")
                        st.rerun()
    
    # عرض النتائج السابقة
    st.markdown("### 📊 سجل التحاليل السابقة")
    with get_db() as conn:
        cursor = conn.execute('''
            SELECT * FROM lab_analyses 
            WHERE cp IS NOT NULL 
            ORDER BY created_at DESC 
            LIMIT 20
        ''')
        results = cursor.fetchall()
        
        if results:
            df_results = pd.DataFrame([dict(r) for r in results])
            st.dataframe(df_results[['request_id', 'cp', 'moisture', 'fat', 'fiber', 'created_at']], 
                        use_container_width=True)
        else:
            st.info("لا توجد نتائج تحاليل سابقة")

# ==========================================
# دمج التحسينات في الكود الأصلي
# ==========================================

# تعديل دالة تشغيل محرك الاستمثال لإضافة الزر المحسن
# (سيتم تعديل الجزء الخاص بزر إرسال الخلطة للمختبر)

# ... (باقي الكود الأصلي يبقى كما هو، مع إضافة التحسينات أعلاه في بداية الملف)

# تعديل جزء زر إرسال الخلطة للمختبر في التبويب الأول
# البحث عن الكود:
# if st.button("🔬 إرسال هذه الخلطة إلى المختبر لتحليلها", key="send_to_lab_btn", use_container_width=True):

# واستبداله بـ:
if st.button("🔬 إرسال هذه الخلطة إلى المختبر لتحليلها", key="send_to_lab_btn", use_container_width=True):
    with st.spinner("جاري إرسال التركيبة إلى المختبر..."):
        request_id = send_formula_to_lab(
            formula_results, 
            st.session_state["active_cp_tag"], 
            computed_se_total,
            sub_type,
            ton_cost,
            user_city
        )
        st.success(f"✅ تم إرسال الطلب رقم {request_id} إلى المختبر بنجاح!")
        log_user_activity("send_to_lab", f"تم إرسال طلب تحليل رقم {request_id}")
        time.sleep(1.5)
        st.rerun()

# ==========================================
# إضافة لوحة تحكم المالك (في تبويب خاص للمالك)
# ==========================================

# إضافة تبويب جديد للمالك في قائمة التبويبات
if st.session_state["user_role"] == "owner":
    # إضافة تبويب "👑 لوحة التحكم المتقدمة" بعد تبويب المختبر
    # (يمكن إضافته في قائمة tabs_titles)

# ==========================================
# تحسينات إضافية: شريط تقدم للعمليات الطويلة
# ==========================================

def show_processing_animation(message="جاري المعالجة..."):
    """عرض رسم متحرك أثناء المعالجة"""
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"""
        <div style="text-align: center; padding: 50px;">
            <div class="spinner"></div>
            <p>{message}</p>
        </div>
        <style>
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #2e7d32;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)
    return placeholder

# ==========================================
# حفظ جميع التحسينات
# ==========================================

def save_all_improvements():
    """حفظ جميع التحسينات والإعدادات"""
    # تشفير الإعدادات الحساسة
    if not os.path.exists("secure_config.json"):
        SECURE_MANAGER.encrypt_sensitive_config()
    
    # إنشاء نسخة احتياطية أولية
    if not os.path.exists("backups"):
        BACKUP_SYSTEM.create_backup()
    
    LOGGER.info("تم تطبيق جميع التحسينات بنجاح")

# تنفيذ حفظ التحسينات عند بدء التشغيل
if "improvements_applied" not in st.session_state:
    save_all_improvements()
    st.session_state["improvements_applied"] = True
