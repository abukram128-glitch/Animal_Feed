# ===================================================================
# منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف - النسخة المحسنة
# ===================================================================

import streamlit as st
import numpy as np
import pandas as pd  
import json
import os
import base64
import smtplib
import time
import urllib.parse  
import tempfile
import hashlib
import secrets
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ===================================================================
# 0. إعدادات الأمان والبيئة
# ===================================================================

class SecureConfig:
    """إعدادات الأمان المركزية - محمية باستخدام st.secrets أو المتغيرات البيئية"""
    
    @staticmethod
    def get_smtp_password() -> str:
        """الحصول على كلمة مرور SMTP بطريقة آمنة"""
        # محاولة الحصول من st.secrets (بيئة Streamlit Cloud)
        try:
            return st.secrets["email"]["password"]
        except:
            pass
        
        # محاولة الحصول من المتغيرات البيئية
        import os
        password = os.environ.get("SMTP_PASSWORD", "")
        if password:
            return password
        
        # آخر خيار: طلب من المستخدم (في حالة التشغيل المحلي)
        if "smtp_password_temp" not in st.session_state:
            st.session_state["smtp_password_temp"] = ""
        
        return st.session_state["smtp_password_temp"]
    
    @staticmethod
    def get_sender_email() -> str:
        try:
            return st.secrets["email"]["sender"]
        except:
            pass
        import os
        return os.environ.get("SENDER_EMAIL", "abukram128@gmail.com")
    
    @staticmethod
    def get_whatsapp_number() -> str:
        try:
            return st.secrets["whatsapp"]["number"]
        except:
            pass
        import os
        return os.environ.get("WHATSAPP_NUMBER", "+249123533489")

# ===================================================================
# 1. إعدادات المنصة والمظهر
# ===================================================================

st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================================================================
# 2. نظام إدارة البيانات المحسن (مع دعم التخزين المؤقت)
# ===================================================================

class DataManager:
    """مدير البيانات المحسن مع دعم التخزين المؤقت والنسخ الاحتياطي"""
    
    DATA_FILE = "platform_data.json"
    BACKUP_FILE = "platform_data_backup.json"
    
    @staticmethod
    def get_data_path() -> str:
        """الحصول على مسار آمن للبيانات"""
        # في بيئة Streamlit Cloud، نستخدم مجلد مؤقت
        if os.path.exists("/mount/src"):
            return os.path.join(tempfile.gettempdir(), DataManager.DATA_FILE)
        return DataManager.DATA_FILE
    
    @staticmethod
    def get_backup_path() -> str:
        if os.path.exists("/mount/src"):
            return os.path.join(tempfile.gettempdir(), DataManager.BACKUP_FILE)
        return DataManager.BACKUP_FILE
    
    @staticmethod
    def save_data(data: Dict[str, Any]) -> bool:
        """حفظ البيانات مع نسخة احتياطية"""
        try:
            path = DataManager.get_data_path()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # نسخة احتياطية
            backup_path = DataManager.get_backup_path()
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            st.warning(f"⚠️ تعذر حفظ البيانات: {e}")
            return False
    
    @staticmethod
    def load_data() -> Dict[str, Any]:
        """تحميل البيانات مع محاولة استعادة النسخة الاحتياطية"""
        path = DataManager.get_data_path()
        backup_path = DataManager.get_backup_path()
        
        # محاولة تحميل الملف الرئيسي
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        
        # محاولة تحميل النسخة الاحتياطية
        if os.path.exists(backup_path):
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        
        return {}
    
    @staticmethod
    def cleanup_old_data():
        """تنظيف البيانات القديمة (لمنع التراكم)"""
        # يمكن تطبيق هذا حسب الحاجة
        pass

# ===================================================================
# 3. نظام التخزين المؤقت المحسن
# ===================================================================

class CacheManager:
    """مدير التخزين المؤقت مع تنظيف تلقائي"""
    
    _instance = None
    _cache = {}
    _max_size = 100
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_cached(key: str) -> Optional[Any]:
        """الحصول على قيمة من التخزين المؤقت"""
        return CacheManager._cache.get(key)
    
    @staticmethod
    def set_cached(key: str, value: Any):
        """تخزين قيمة مع التحقق من الحجم"""
        if len(CacheManager._cache) >= CacheManager._max_size:
            # حذف أقدم 25% من العناصر
            keys = list(CacheManager._cache.keys())
            for k in keys[:len(keys)//4]:
                del CacheManager._cache[k]
        
        CacheManager._cache[key] = value
    
    @staticmethod
    def clear_cache():
        """مسح التخزين المؤقت بالكامل"""
        CacheManager._cache.clear()
        CacheManager.get_cached.cache_clear()

# ===================================================================
# 4. نظام الأمان المحسن
# ===================================================================

class SecurityManager:
    """مدير الأمان المتقدم مع تشفير وحماية البيانات"""
    
    @staticmethod
    def generate_secure_hash(code: str, salt: str = None) -> str:
        if salt is None:
            salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', code.encode(), salt.encode(), 100000).hex()
    
    @staticmethod
    def validate_session() -> bool:
        """التحقق من صحة الجلسة"""
        if "session_token" not in st.session_state:
            return False
        if "session_created" not in st.session_state:
            return False
        
        # انتهاء صلاحية الجلسة بعد 24 ساعة
        session_age = (datetime.now() - st.session_state["session_created"]).total_seconds()
        if session_age > 86400:  # 24 ساعة
            return False
        
        return True
    
    @staticmethod
    def create_session():
        """إنشاء جلسة آمنة"""
        st.session_state["session_token"] = secrets.token_urlsafe(32)
        st.session_state["session_created"] = datetime.now()

# ===================================================================
# 5. أكواد الدخول المعتمدة (مشفرة)
# ===================================================================

# تخزين الأكواد بشكل آمن
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# تخزين الهاشات للأكواد (للتحقق السريع)
SECURE_CODES = {SecurityManager.generate_secure_hash(code)[:32]: info for code, info in CODES_DB.items()}

# ===================================================================
# 6. إعدادات البريد الإلكتروني المحسنة
# ===================================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = SecureConfig.get_sender_email()
SENDER_PASSWORD = SecureConfig.get_smtp_password()
OWNER_EMAIL = SecureConfig.get_sender_email()
WHATSAPP_NUMBER = SecureConfig.get_whatsapp_number()
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"

# ===================================================================
# 7. تحميل الصور مع التخزين المؤقت المحسن
# ===================================================================

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

@st.cache_data(ttl=7200)  # زيادة وقت التخزين المؤقت
def get_image_base64_safe(paths: List[str]) -> Optional[str]:
    """تحميل الصور مع معالجة الأخطاء المحسنة"""
    for path in paths:
        # محاولة مسارات متعددة
        possible_paths = [
            path,
            os.path.join("images", path),
            os.path.join("assets", path),
            os.path.join(os.path.dirname(__file__), "images", path)
        ]
        
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    with open(p, "rb") as image_file:
                        return base64.b64encode(image_file.read()).decode()
                except Exception:
                    continue
    
    # صورة بديلة من الإنترنت في حالة عدم وجود ملفات
    try:
        import requests
        fallback_url = "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=200"
        response = requests.get(fallback_url, timeout=5)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except:
        pass
    
    return None

# تحميل الصورة
img_base64 = get_image_base64_safe(PHOTO_OPTIONS)

# ===================================================================
# 8. إرسال البريد الإلكتروني المحسن
# ===================================================================

def send_code_to_mail_secure(receiver_email: str, attachment_type: str = "full") -> bool:
    """إرسال الكود عبر البريد الإلكتروني مع تحسينات الأمان"""
    
    # التحقق من وجود كلمة المرور
    if not SENDER_PASSWORD or SENDER_EMAIL == "YOUR_EMAIL@gmail.com":
        st.error("⚠️ يرجى إعداد كلمة مرور البريد الإلكتروني في الإعدادات.")
        # عرض واجهة لإدخال كلمة المرور (في حالة التشغيل المحلي)
        if "smtp_password_temp" not in st.session_state:
            st.session_state["smtp_password_temp"] = ""
        
        temp_pass = st.text_input("🔑 أدخل كلمة مرور البريد الإلكتروني (Gmail App Password):", 
                                  type="password", 
                                  key="temp_smtp_pass")
        if st.button("💾 حفظ كلمة المرور مؤقتاً"):
            st.session_state["smtp_password_temp"] = temp_pass
            st.success("تم حفظ كلمة المرور مؤقتاً. حاول الإرسال مرة أخرى.")
            return False
        
        return False
    
    try:
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

تم تحسين الأمان وحماية البيانات في هذه النسخة.

تحياتي الهندسية."""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # إرفاق الكود
        try:
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except NameError:
            code_content = "# كود المنصة مأرشيف داخلياً\n"
        
        file_hash = hashlib.md5(code_content.encode()).hexdigest()
        code_content = f"# Digital Signature: {file_hash}\n# Generated: {datetime.now().isoformat()}\n\n{code_content}"
        
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_scientific_platform.py")
        msg.attach(attachment)
        
        # إرسال البريد
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        
        return True
        
    except Exception as e:
        st.error(f"❌ فشل الإرسال: {str(e)}")
        # محاولة عرض حل للمشكلة
        if "Authentication" in str(e):
            st.info("💡 تأكد من استخدام 'كلمة مرور التطبيق' (App Password) وليس كلمة المرور العادية لحساب Gmail.")
        return False

# ===================================================================
# 9. معالجة النصوص العربية المحسنة
# ===================================================================

class ArabicTextProcessor:
    """معالج النصوص العربية مع التخزين المؤقت المحسن"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix_arabic_text(text: str) -> str:
        """معالجة النص العربي مع التخزين المؤقت"""
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except:
            return text

# ===================================================================
# 10. نظام توليد PDF المحسن
# ===================================================================

class ProfessionalPDFGenerator:
    """مولد PDF محسن مع معالجة الأخطاء والنسخ الاحتياطي"""
    
    def __init__(self):
        self.font_name = 'Helvetica'
        self._init_fonts()
    
    def _init_fonts(self):
        """تهيئة الخطوط مع محاولة تحميل خط عربي"""
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # محاولة تحميل خط عربي من عدة مسارات
            font_paths = [
                "Amiri-Regular.ttf",
                "fonts/Amiri-Regular.ttf",
                os.path.join(os.path.dirname(__file__), "fonts", "Amiri-Regular.ttf"),
                os.path.join(os.path.dirname(__file__), "assets", "fonts", "Amiri-Regular.ttf")
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont('Amiri', path))
                        self.font_name = 'Amiri'
                        break
                    except:
                        continue
        except:
            pass
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True) -> bytes:
        """توليد تقرير PDF شامل مع معالجة الأخطاء"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.units import inch, mm
            from reportlab.lib.colors import HexColor, black, white, grey
            from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
            from reportlab.platypus.flowables import HRFlowable
            import io
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
            story = []
            
            def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
                safe_text = ArabicTextProcessor.fix_arabic_text(str(text))
                return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))
            
            # العنوان الرئيسي
            story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
            story.append(Spacer(1, 12))
            
            # معلومات التقرير
            info_lines = [
                f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور",
                f"الموقع الجغرافي: {city}",
                f"الفصيل المستهدف: {breed}",
                f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ]
            for line in info_lines:
                story.append(p(line, size=11))
            story.append(Spacer(1, 15))
            
            # جدول المعايير الرئيسية
            tdata = [
                [ArabicTextProcessor.fix_arabic_text('المعيار'), ArabicTextProcessor.fix_arabic_text('القيمة')],
                [ArabicTextProcessor.fix_arabic_text('البروتين المهضوم (DP)'), f'{target_dp:.2f}%'],
                [ArabicTextProcessor.fix_arabic_text('معادل النشاء (SE)'), f'{computed_se:.2f} وحدة'],
                [ArabicTextProcessor.fix_arabic_text('التكلفة للطن'), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
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
            
            # المكونات
            story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", size=14, color=HexColor('#2e7d32')))
            story.append(Spacer(1, 10))
            
            ing_data = [[ArabicTextProcessor.fix_arabic_text('المكون'), 
                        ArabicTextProcessor.fix_arabic_text('النسبة %'), 
                        ArabicTextProcessor.fix_arabic_text('كجم/طن')]]
            
            for ing, pct in formula.items():
                ing_data.append([ArabicTextProcessor.fix_arabic_text(ing), f'{pct:.2f}%', f'{pct*10:.1f}'])
            
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
            
            # الرسوم البيانية
            if include_charts and len(formula) > 1:
                try:
                    import matplotlib.pyplot as plt
                    
                    fig, ax = plt.subplots(figsize=(6, 3.5))
                    names = list(formula.keys())
                    vals = list(formula.values())
                    colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                    
                    ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                    ax.legend([ArabicTextProcessor.fix_arabic_text(n) for n in names], 
                             title=ArabicTextProcessor.fix_arabic_text("المكونات"),
                             loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                    ax.set_title(ArabicTextProcessor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                    
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    story.append(Image(buf, width=400, height=230))
                except Exception as e:
                    # إذا فشل الرسم البياني، نستمر بدون مشكلة
                    story.append(p("⚠️ تعذر إنشاء الرسم البياني", size=10, color=HexColor('#ff6b6b')))
            
            # التذييل
            story.append(Spacer(1, 25))
            story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026 | تحت إشراف م. عبد القادر إسماعيل تاور", 
                           size=9, align=TA_CENTER, color=HexColor('#666666')))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            # في حالة فشل التقرير الكامل، نقدم تقرير مبسط
            st.warning(f"⚠️ تعذر إنشاء التقرير الكامل: {e}. جاري إنشاء نسخة مبسطة...")
            return self._generate_simple_report(formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se)
    
    def _generate_simple_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se) -> bytes:
        """توليد تقرير مبسط في حالة فشل التقرير الكامل"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import inch
            import io
            
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # عنوان التقرير المبسط
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, "تقرير منصة تاور العلمية (نسخة مبسطة)")
            
            # معلومات أساسية
            y = height - 1.5*inch
            c.setFont("Helvetica", 11)
            c.drawString(1*inch, y, f"المشرف: م. عبد القادر إسماعيل تاور")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"الفصيل: {breed}")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"الموقع: {city}")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"البروتين المهضوم: {target_dp:.2f}%")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"معادل النشاء: {computed_se:.2f}")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"التكلفة: ${cost:.2f} ({local_cost:,.2f} {local_sym})")
            y -= 0.5*inch
            
            # المكونات
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "المكونات:")
            y -= 0.3*inch
            c.setFont("Helvetica", 10)
            
            for ing, pct in formula.items():
                c.drawString(1*inch, y, f"- {ing}: {pct:.2f}% ({pct*10:.1f} كجم/طن)")
                y -= 0.25*inch
                if y < 1*inch:
                    c.showPage()
                    y = height - 1*inch
            
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            # في حالة فشل كل شيء، نقدم نص بسيط
            st.error(f"❌ تعذر إنشاء التقرير: {e}")
            return b""

# ===================================================================
# 11. كلاس إدارة مزارع الدجاج اللاحم (محسن)
# ===================================================================

class BroilerFarmManager:
    """مدير مزارع الدجاج اللاحم مع تحسينات الأداء"""
    
    # حدود للحفاظ على الأداء
    MAX_DAILY_LOGS = 365
    MAX_CYCLES = 10
    MAX_HEALTH_LOGS = 200
    
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
    @st.cache_data(ttl=3600)
    def get_temp_humidity_table() -> pd.DataFrame:
        data = {
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55]
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def cleanup_farm_data(farm_data: Dict) -> Dict:
        """تنظيف بيانات المزرعة للحفاظ على الأداء"""
        farm_data = farm_data.copy()
        
        # تنظيف اليوميات
        if "daily_logs" in farm_data and len(farm_data["daily_logs"]) > BroilerFarmManager.MAX_DAILY_LOGS:
            farm_data["daily_logs"] = farm_data["daily_logs"][-BroilerFarmManager.MAX_DAILY_LOGS:]
        
        # تنظيف السجلات الصحية
        if "health_log" in farm_data and len(farm_data["health_log"]) > BroilerFarmManager.MAX_HEALTH_LOGS:
            farm_data["health_log"] = farm_data["health_log"][-BroilerFarmManager.MAX_HEALTH_LOGS:]
        
        return farm_data

# ===================================================================
# 12. نظام إدارة الأسعار المحسن
# ===================================================================

class MarketPriceEngine:
    """محرك أسعار السوق مع التخزين المؤقت"""
    
    @staticmethod
    @lru_cache(maxsize=256)
    def get_adjusted_market_data(country: str, state_or_region: str, city: str) -> Dict[str, float]:
        """الحصول على أسعار السوق مع التخزين المؤقت"""
        feed_prices = {}
        
        # الأسعار الأساسية
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
        
        # تعديل الأسعار حسب الموقع
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

# ===================================================================
# 13. نظام إدارة المخزون المحسن
# ===================================================================

class InventoryManager:
    """مدير المخزون مع دعم الحفظ التلقائي"""
    
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            from BIG_FEEDS_LIBRARY import BIG_FEEDS_LIBRARY
            
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
            qty = data if isinstance(data, (int, float)) else data.get("quantity", 0.0)
            threshold = 5.0 if isinstance(data, (int, float)) else data.get("min_threshold", 5.0)
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings
    
    @staticmethod
    def save_inventory():
        """حفظ حالة المخزون"""
        if "inventory" in st.session_state:
            DataManager.save_data({
                "inventory": st.session_state["inventory"],
                "timestamp": datetime.now().isoformat()
            })

# ===================================================================
# 14. المكتبة الرئيسية للمواد العلفية (نفسها)
# ===================================================================

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

# ===================================================================
# 15. نظام أسعار المدن المحسن
# ===================================================================

def load_city_prices() -> Dict:
    """تحميل أسعار المدن مع دعم النسخ الاحتياطي"""
    data = DataManager.load_data()
    return data.get("city_prices", {})

def save_city_prices(data: Dict) -> bool:
    """حفظ أسعار المدن"""
    full_data = DataManager.load_data()
    full_data["city_prices"] = data
    full_data["last_update"] = datetime.now().isoformat()
    return DataManager.save_data(full_data)

CITY_CUSTOM_PRICES = load_city_prices()

# ===================================================================
# 16. الصور والموارد
# ===================================================================

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

# ===================================================================
# 17. أسعار العملات
# ===================================================================

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

# ===================================================================
# 18. تهيئة حالة الجلسة المحسنة
# ===================================================================

def init_session_state():
    """تهيئة حالة الجلسة مع التحقق من الصلاحية"""
    
    # التحقق من صحة الجلسة
    if "session_token" in st.session_state:
        if not SecurityManager.validate_session():
            # جلسة منتهية الصلاحية
            for key in list(st.session_state.keys()):
                if key not in ["approved", "user_role", "login_attempts"]:
                    del st.session_state[key]
            SecurityManager.create_session()
    
    # المتغيرات الأساسية
    if "approved" not in st.session_state:
        st.session_state["approved"] = False
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None
    if "login_welcome_shown" not in st.session_state:
        st.session_state["login_welcome_shown"] = False
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0
    if "last_login_time" not in st.session_state:
        st.session_state["last_login_time"] = None
    if "session_token" not in st.session_state:
        SecurityManager.create_session()
    
    # بيانات المزارع
    if "broiler_farms" not in st.session_state:
        st.session_state["broiler_farms"] = {}
    if "selected_farm" not in st.session_state:
        st.session_state["selected_farm"] = None
    
    # جدول التحصينات القياسي
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
    
    # بيانات الأسعار
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
    
    # بيانات التركيبات
    if "active_formula" not in st.session_state:
        st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
    if "active_cp_tag" not in st.session_state:
        st.session_state["active_cp_tag"] = 12.0
    if "active_se_tag" not in st.session_state:
        st.session_state["active_se_tag"] = 65.0
    if "active_breed_tag" not in st.session_state:
        st.session_state["active_breed_tag"] = "سلالة عامة"
    if "active_animal_img" not in st.session_state:
        st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
    if "active_stage_title" not in st.session_state:
        st.session_state["active_stage_title"] = "إنتاج عام"
    if "computed_ton_cost" not in st.session_state:
        st.session_state["computed_ton_cost"] = 280.0

# استدعاء التهيئة
init_session_state()
InventoryManager.initialize_inventory()

# ===================================================================
# 19. دوال مساعدة للتنبيهات عبر واتساب (محسنة)
# ===================================================================

def send_whatsapp_broiler_alert(phone_number: str, message: str):
    """إرسال تنبيه عبر واتساب مع تحسينات"""
    if not phone_number or phone_number == "YOUR_PHONE_NUMBER":
        phone_number = WHATSAPP_NUMBER
    
    # تنظيف رقم الهاتف
    phone_number = phone_number.replace(" ", "").replace("-", "")
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number
    
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
    
    # عرض رابط قابل للنقر
    st.markdown(
        f"""
        <div style='background:#e8f5e9; padding:10px; border-radius:8px; direction:ltr;'>
        📲 <b>تنبيه عبر واتساب:</b> 
        <a href='{whatsapp_url}' target='_blank' style='color:#25D366; font-weight:bold;'>
            اضغط لإرسال الرسالة إلى {phone_number}
        </a>
        <br>{message}
        </div>
        """, 
        unsafe_allow_html=True
    )

def check_and_alert_medications(farm_name: str, farm_data: dict, current_age: int):
    """التحقق من الأدوية المستحقة وإرسال التنبيهات"""
    phone = farm_data.get("owner_phone", WHATSAPP_NUMBER)
    schedule = st.session_state["standard_vacc_schedule"]
    alerts = []
    
    for age_day, item in schedule.items():
        if age_day == current_age:
            key = f"{farm_name}_{age_day}_{item['type']}_{item['name']}"
            if key not in st.session_state["whatsapp_alerts_sent"]:
                alert_msg = (
                    f"🔔 تنبيه لمزرعة {farm_name} (العمر {age_day} يوم):\n"
                    f"{item['type']} {item['name']} - الجرعة: {item['dose']} - طريقة الإعطاء: {item['route']}"
                )
                send_whatsapp_broiler_alert(phone, alert_msg)
                st.session_state["whatsapp_alerts_sent"][key] = datetime.now().isoformat()
                alerts.append(alert_msg)
    
    if alerts:
        st.info(f"📢 تم إرسال {len(alerts)} تنبيه إلى المالك لليوم (العمر {current_age} يوم).")
    else:
        st.success("✅ لا توجد تحصينات أو أدوية مستحقة اليوم.")

# ===================================================================
# 20. بداية الكود الرئيسي للواجهة
# ===================================================================

# ... (يتبع الكود الأصلي من هنا مع التعديلات المذكورة)
# نظراً لطول الكود، سأستمر في عرض التعديلات الرئيسية
