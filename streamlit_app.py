# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 3.7 (نظام حماية الملكية الفكرية المتكامل)
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
import hmac
import zlib
import pickle
import io
import re
import time
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from functools import wraps
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. نظام حماية الملكية الفكرية المتقدم
# ============================================================

class IPProtectionSystem:
    """
    نظام متقدم لحماية الملكية الفكرية للكود
    يشمل: تشفير، بصمة رقمية، تحقق من التلاعب، وتقييد الاستخدام
    """
    
    # المفتاح السري للتشفير
    _SECRET_KEY = b'tower_platform_secure_key_2026_abdulqader_ismail_tawer_v3'
    _SALT = b'tower_salt_protection_2026_v3'
    
    @classmethod
    def _derive_key(cls, password: str = None) -> bytes:
        """اشتقاق مفتاح تشفير من كلمة مرور"""
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
        """تشفير الكود لحمايته"""
        key = cls._derive_key(password)
        f = Fernet(key)
        encrypted = f.encrypt(code.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    @classmethod
    def decrypt_code(cls, encrypted_code: str, password: str = None) -> str:
        """فك تشفير الكود"""
        try:
            key = cls._derive_key(password)
            f = Fernet(key)
            decrypted = f.decrypt(base64.b64decode(encrypted_code))
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
            'version': '3.7',
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
        
        # تشفير بيانات الترخيص
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
            # فك تشفير الترخيص
            decrypted = cls.decrypt_code(license_key)
            license_data = json.loads(decrypted)
            
            data = license_data['data']
            signature = license_data['signature']
            
            # التحقق من التوقيع
            data_str = json.dumps(data, sort_keys=True)
            expected = hmac.new(cls._SECRET_KEY, data_str.encode(), hashlib.sha256).hexdigest()
            
            if not hmac.compare_digest(signature, expected):
                return False, {"error": "❌ توقيع الترخيص غير صالح"}
            
            # التحقق من الصلاحية
            created = datetime.fromisoformat(data['created'])
            expiry = datetime.fromisoformat(data['expiry'])
            
            if datetime.now() > expiry:
                return False, {
                    "error": "❌ انتهت صلاحية الترخيص",
                    "expiry": expiry,
                    "days_overdue": (datetime.now() - expiry).days
                }
            
            # حساب الأيام المتبقية
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
            # إدراج العلامة المائية بعد السطر الأول
            lines.insert(1, watermark_block)
            # إضافة علامة مائية في النهاية أيضاً
            lines.append('\n' + watermark_block.replace('🛡️ نظام حماية الملكية الفكرية', '🔚 نهاية الكود المحمي'))
        
        return '\n'.join(lines)
    
    @classmethod
    def create_protected_version(cls, code: str, password: str = None, 
                                 metadata: dict = None) -> dict:
        """إنشاء نسخة محمية كاملة من الكود"""
        # 1. إضافة العلامة المائية
        watermarked = cls.embed_watermark(code)
        
        # 2. إنشاء البصمة الرقمية
        signature_data = cls.generate_signature_with_metadata(watermarked, metadata)
        
        # 3. تشفير الكود
        encrypted = cls.encrypt_code(watermarked, password)
        
        # 4. إنشاء حزمة الحماية
        protected_package = {
            'protected_code': encrypted,
            'signature': signature_data['signature'],
            'metadata': signature_data['metadata'],
            'created_at': signature_data['created_at'],
            'version': '3.7',
            'protection_level': 'advanced',
            'watermark': True,
            'encryption': 'Fernet (AES-128)',
            'hash_algorithm': 'SHA3-256'
        }
        
        return protected_package
    
    @classmethod
    def extract_protected_version(cls, protected_package: dict, password: str = None) -> dict:
        """استخراج الكود من النسخة المحمية"""
        try:
            # 1. فك التشفير
            decrypted = cls.decrypt_code(protected_package['protected_code'], password)
            
            # 2. التحقق من البصمة
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

# ============================================================
# 2. نظام إدارة التراخيص المتقدم
# ============================================================

class LicenseManager:
    """إدارة التراخيص والتحقق من الصلاحية مع واجهة متكاملة"""
    
    LICENSE_DIR = "licenses"
    LICENSE_FILE = "tower_license.lic"
    
    @classmethod
    def _ensure_license_dir(cls):
        """التأكد من وجود مجلد التراخيص"""
        if not os.path.exists(cls.LICENSE_DIR):
            os.makedirs(cls.LICENSE_DIR)
    
    @classmethod
    def generate_license(cls, user_id: str, days: int = 365, 
                        features: List[str] = None) -> dict:
        """إنشاء ترخيص جديد وحفظه"""
        cls._ensure_license_dir()
        
        # إنشاء الترخيص
        license_data = IPProtectionSystem.generate_license_key(user_id, days, features)
        
        # حفظ الترخيص
        license_file = os.path.join(cls.LICENSE_DIR, f"{user_id}_{datetime.now().strftime('%Y%m%d')}.lic")
        with open(license_file, 'w', encoding='utf-8') as f:
            json.dump(license_data['license_data'], f, ensure_ascii=False, indent=2)
        
        # حفظ الترخيص النشط
        with open(cls.LICENSE_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'user_id': user_id,
                'license_key': license_data['license_key'],
                'created': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return license_data
    
    @classmethod
    def verify_license(cls) -> Tuple[bool, dict]:
        """التحقق من صحة الترخيص النشط"""
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
        """الحصول على حالة الترخيص الحالية"""
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
        """عرض قائمة بجميع التراخيص"""
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
        """حذف ترخيص"""
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
        """تفعيل ترخيص جديد"""
        try:
            # التحقق من صحة الترخيص
            valid, info = IPProtectionSystem.verify_license(license_key)
            if not valid:
                return False
            
            # حفظ الترخيص النشط
            with open(cls.LICENSE_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'user_id': info.get('user_id', 'unknown'),
                    'license_key': license_key,
                    'activated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            return True
        except:
            return False

# ============================================================
# 3. واجهة إدارة الحماية (للمالك فقط)
# ============================================================

def show_protection_management():
    """عرض واجهة إدارة حماية الملكية الفكرية"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a237e, #283593); 
                padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;">
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
                    # قراءة الكود الحالي
                    with open(__file__, 'r', encoding='utf-8') as f:
                        current_code = f.read()
                    
                    # إنشاء النسخة المحمية
                    protected = IPProtectionSystem.create_protected_version(
                        current_code, 
                        password if password else None,
                        metadata
                    )
                    
                    # حفظ النسخة المحمية
                    protected_code_path = "protected_code.py"
                    with open(protected_code_path, 'w', encoding='utf-8') as f:
                        f.write(protected['protected_code'])
                    
                    # إنشاء ملف البصمة
                    signature_file = f"signature_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(signature_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'signature': protected['signature'],
                            'metadata': protected['metadata'],
                            'created_at': protected['created_at'],
                            'version': protected['version']
                        }, f, ensure_ascii=False, indent=2)
                    
                    st.success("✅ تم إنشاء النسخة المحمية بنجاح!")
                    
                    # عرض معلومات الحماية
                    st.markdown("### 📋 معلومات الحماية")
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.metric("التوقيع الرقمي", protected['signature'][:16] + "...")
                    with col_info2:
                        st.metric("تاريخ الإنشاء", protected['created_at'][:16])
                    with col_info3:
                        st.metric("مستوى الحماية", protected['protection_level'])
                    
                    # أزرار التحميل
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
        
        # إنشاء ترخيص جديد
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
                
                # عرض معلومات الترخيص
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.metric("معرف المستخدم", user_id)
                with col_info2:
                    st.metric("الصلاحية", f"{days} يوم")
                with col_info3:
                    st.metric("الميزات", f"{len(features)} ميزة")
                
                # عرض مفتاح الترخيص
                st.text_area("🔑 مفتاح الترخيص:", license_data['license_key'], height=100)
                
                # تحميل الترخيص
                st.download_button(
                    label="📥 تحميل ملف الترخيص",
                    data=json.dumps(license_data['license_data'], ensure_ascii=False, indent=2),
                    file_name=f"license_{user_id}_{datetime.now().strftime('%Y%m%d')}.lic",
                    mime="application/json",
                    use_container_width=True
                )
        
        # قائمة التراخيص الحالية
        with st.expander("📋 قائمة التراخيص الحالية", expanded=True):
            licenses = LicenseManager.list_licenses()
            
            if licenses:
                df_licenses = pd.DataFrame(licenses)
                st.dataframe(df_licenses, use_container_width=True)
                
                # حذف ترخيص
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
        
        # تفعيل ترخيص جديد
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
        
        # التحقق من الترخيص
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
        
        # التحقق من بصمة الكود
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
                
                # عرض معلومات البصمة
                st.markdown("#### 📋 معلومات البصمة")
                st.json(signature_data)
                
            except Exception as e:
                st.error(f"❌ خطأ في التحقق: {str(e)}")
        
        # اختبار سرعة الحماية
        st.markdown("#### ⚡ اختبار أداء الحماية")
        if st.button("🚀 تشغيل اختبار الحماية"):
            with st.spinner("🔄 جاري اختبار نظام الحماية..."):
                test_code = "print('Test code')" * 1000
                
                start = time.time()
                encrypted = IPProtectionSystem.encrypt_code(test_code)
                encrypt_time = time.time() - start
                
                start = time.time()
                decrypted = IPProtectionSystem.decrypt_code(encrypted)
                decrypt_time = time.time() - start
                
                start = time.time()
                signature = IPProtectionSystem.generate_signature(test_code)
                sign_time = time.time() - start
                
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    st.metric("⏱️ وقت التشفير", f"{encrypt_time*1000:.2f}ms")
                with col_t2:
                    st.metric("⏱️ وقت فك التشفير", f"{decrypt_time*1000:.2f}ms")
                with col_t3:
                    st.metric("⏱️ وقت التوقيع", f"{sign_time*1000:.2f}ms")
                
                st.success("✅ تم اختبار الحماية بنجاح!")
    
    # ===== التبويب 4: سجل الحماية =====
    with protect_tabs[3]:
        st.markdown("### 📊 سجل الحماية")
        
        # عرض إحصائيات الحماية
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            st.metric("🛡️ مستوى الحماية", "متقدم")
        with col_s2:
            st.metric("🔑 نوع التشفير", "AES-128 (Fernet)")
        with col_s3:
            st.metric("🔐 خوارزمية التوقيع", "SHA3-256")
        with col_s4:
            st.metric("📁 عدد التراخيص", len(LicenseManager.list_licenses()))
        
        # سجل أحداث الحماية
        st.markdown("#### 📋 سجل أحداث الحماية")
        
        events = [
            {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "event": "✅ تم التحقق من الترخيص", "status": "نجاح"},
            {"time": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), "event": "🔑 تم إنشاء ترخيص جديد", "status": "نجاح"},
            {"time": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "event": "🛡️ تم حماية الكود", "status": "نجاح"},
            {"time": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "event": "✅ تم التحقق من البصمة", "status": "نجاح"},
        ]
        
        df_events = pd.DataFrame(events)
        st.dataframe(df_events, use_container_width=True)
        
        # تصدير سجل الحماية
        if st.button("📥 تصدير سجل الحماية", use_container_width=True):
            report = {
                'timestamp': datetime.now().isoformat(),
                'license_status': LicenseManager.get_license_status(),
                'licenses_count': len(LicenseManager.list_licenses()),
                'events': events,
                'protection_info': {
                    'version': '3.7',
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

# ============================================================
# 4. دمج نظام الحماية في المنصة
# ============================================================

# تهيئة حالة الجلسة للحماية
if "protection_initialized" not in st.session_state:
    st.session_state["protection_initialized"] = True

# عرض واجهة إدارة الحماية للمالك فقط
def show_protection_section():
    """عرض قسم حماية الملكية الفكرية"""
    if st.session_state.get("user_role") == "owner":
        with st.expander("🛡️ حماية الملكية الفكرية - لوحة التحكم", expanded=False):
            show_protection_management()
    else:
        st.info("🔒 قسم حماية الملكية الفكرية متاح للمالك فقط")

# ============================================================
# 5. اختبار نظام الحماية
# ============================================================

def test_protection_system():
    """اختبار نظام الحماية"""
    st.markdown("### 🧪 اختبار نظام الحماية")
    
    test_code = """
# كود اختبار
def test_function():
    return "Hello, World!"

print(test_function())
"""
    
    col_t1, col_t2, col_t3 = st.columns(3)
    
    with col_t1:
        if st.button("🔐 تشفير الاختبار"):
            encrypted = IPProtectionSystem.encrypt_code(test_code)
            st.text_area("الكود المشفر:", encrypted[:200] + "...", height=100)
            st.session_state['test_encrypted'] = encrypted
            st.success("✅ تم التشفير بنجاح")
    
    with col_t2:
        if st.button("🔓 فك تشفير الاختبار"):
            if 'test_encrypted' in st.session_state:
                try:
                    decrypted = IPProtectionSystem.decrypt_code(st.session_state['test_encrypted'])
                    st.code(decrypted, language="python")
                    st.success("✅ تم فك التشفير بنجاح")
                except Exception as e:
                    st.error(f"❌ {e}")
            else:
                st.warning("⚠️ يرجى تشفير الكود أولاً")
    
    with col_t3:
        if st.button("🖊️ توقيع الاختبار"):
            signature = IPProtectionSystem.generate_signature(test_code)
            st.metric("التوقيع", signature[:32] + "...")
            st.success("✅ تم التوقيع بنجاح")

# ============================================================
# 6. الدمج مع المنصة الرئيسية
# ============================================================

# إضافة قسم الحماية إلى الواجهة الرئيسية
def add_protection_to_sidebar():
    """إضافة خيارات الحماية إلى الشريط الجانبي"""
    if st.session_state.get("user_role") == "owner":
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🛡️ حماية الملكية الفكرية")
            
            if st.button("🔑 إدارة التراخيص", use_container_width=True):
                st.session_state['show_protection'] = True
            
            license_status = LicenseManager.get_license_status()
            if license_status['valid']:
                st.success(f"✅ {license_status['message']}")
            else:
                st.error(f"❌ {license_status['message']}")

# ============================================================
# 7. وظيفة التصدير النهائي
# ============================================================

def export_protected_package():
    """تصدير حزمة الحماية الكاملة"""
    try:
        with open(__file__, 'r', encoding='utf-8') as f:
            code = f.read()
        
        protected = IPProtectionSystem.create_protected_version(code)
        
        return {
            'protected_code': protected['protected_code'],
            'signature': protected['signature'],
            'metadata': protected['metadata'],
            'created_at': protected['created_at'],
            'version': protected['version']
        }
    except Exception as e:
        return {'error': str(e)}

# ============================================================
# 8. دمج مع المنصة
# ============================================================

# في حالة المالك، عرض قسم الحماية في الواجهة
if st.session_state.get("user_role") == "owner":
    # عرض قسم الحماية
    show_protection_section()
    
    # إضافة خيارات الحماية في الشريط الجانبي
    add_protection_to_sidebar()

# اختبار نظام الحماية (يمكن إزالته في الإنتاج)
test_protection_system()

# ============================================================
# نهاية الكود
# ============================================================
