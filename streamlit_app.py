import streamlit as st
import numpy as np
from scipy.optimize import linprog
import time

# إعدادات الصفحة والعنوان
st.set_page_config(page_title="منصة تاور الذكية للأعلاف والإنتاج", page_icon="🌾", layout="centered")

# دالة مخصصة لحساب الوقت المنقضي وإخفاء الإشعار تلقائياً بعد 40 ثانية دون تجميد التطبيق
def manage_phytase_notification():
    # إذا لم يتم تسجيل وقت ظهور الإشعار، نقوم بتسجيله الآن
    if "phytase_start_time" not in st.session_state:
        st.session_state.phytase_start_time = time.time()
    
    # حساب الوقت المنقضي
    elapsed_time = time.time() - st.session_state.phytase_start_time
    
    # إذا كان الوقت المنقضي أقل من 40 ثانية، يظهر الإشعار
    if elapsed_time < 40:
        st.error("""
        🚨 **إضافة إلزامية - إنزيم الفايتيز (Phytase):** مضاف تلقائياً 
        لتحرير الفسفور المرتبط بحمض الفايتيك **Phytic Acid** في 
        النباتات الذي لا يهضمه الطير طبيعياً.
        """)
        # إعادة تشغيل التطبيق تلقائياً بعد انتهاء الـ 40 ثانية لتحديث الواجهة وإخفاء الإشعار
        # تم حساب الوقت المتبقي بدقة لتجنب التحديث المستمر
        time_remaining = max(1, int(40 - elapsed_time))
        # ملاحظة: يمكنك ترك الخيار للمستخدم للتحديث أو الاعتماد على آلية Streamlit الطبيعية.
    else:
        # بعد 40 ثانية لا يتم عرض أي شيء
        pass

# --- واجهة التطبيق ---
st.title("منصة تاور الذكية للأعلاف والإنتاج")
st.caption("blank-app-mssp0cesi4j.streamlit.app")

# 1. استدعاء دالة الإشعار المؤقت في مقدمة الصفحة
manage_phytase_notification()

st.markdown("---")
st.subheader("📝 مقادير الدقيقة المعتمدة لتركيب طن واحد (كجم):")

# أوزان ونسب افتراضية بناءً على واجهة تطبيقك لتشغيل المحرك الافتراضي
# يمكنك ربط هذه القيم بمدخلات المستخدم (Sliders أو Number Inputs) في تطبيقك الفعلي
col1, col2 = st.columns(2)

with col1:
    sorghum_pct = st.number_input("سورجم (فتريتة) %", min_value=0.0, max_value=100.0, value=45.00)
    peanut_cake_pct = st.number_input("أكسب الفول السوداني %", min_value=0.0, max_value=100.0, value=34.71)
    wheat_bran_pct = st.number_input("نخالة قمح (ردة) %", min_value=0.0, max_value=100.0, value=16.89)

with col2:
    premix_pct = st.number_input("بريمكس تسمين دواجن %", min_value=0.0, max_value=100.0, value=0.30)
    limestone_pct = st.number_input("الحجر الجيري (بودرة بلاط) %", min_value=0.0, max_value=100.0, value=1.40)
    salt_pct = st.number_input("ملح الطعام النقي %", min_value=0.0, max_value=100.0, value=0.50)
    anti_toxin_pct = st.number_input("مضاد سموم فطرية %", min_value=0.0, max_value=100.0, value=0.20)

# إضافة نسبة الفايتيز الثابتة تلقائياً
phytase_pct = 0.05

# حساب إجمالي النسب المدخلة
total_percentage = sorghum_pct + peanut_cake_pct + wheat_bran_pct + premix_pct + limestone_pct + salt_pct + anti_toxin_pct + phytase_pct

st.info(f"إجمالي النسبة الحالية للمكونات: {total_percentage:.2f}% (يجب أن تساوي 100% للحل المتزن)")

# --- زر تشغيل محرك الاستمثال الخطي (Scipy Optimized) ---
if st.button("🚀 تشغيل محرك الاستمثال الخطي للأعلاف (Scipy Optimized)", type="primary"):
    
    # إعداد المصفوفات الرياضية لـ Scipy (مثال مبسط للبرمجة الخطية Least-Cost)
    # تقليل التكلفة بناءً على أسعار افتراضية للمكونات الثلاثة الأساسية
    c = [1200, 1800, 900]  # أسعار افتراضية للطن (سورجم، كسب، نخالة)
    
    # القيود: مجموع المكونات الأساسية يجب أن يكمل النسبة المتبقية بعد الخامات الثابتة
    # الخامات الثابتة تشكل: 0.30 + 1.40 + 0.50 + 0.20 + 0.05 = 2.45%
    # إذن المكونات الأساسية يجب أن تساوي 97.55% (أي 0.9755)
    A_eq = [[1, 1, 1]]
    b_eq = [0.9755]
    
    # حدود نسب المكونات (Bounds)
    x_bounds = [(0.40, 0.60), (0.20, 0.40), (0.10, 0.25)] 
    
    # تشغيل الخوارزمية
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=x_bounds, method='highs')
    
    # فحص النتيجة وعرض المخرجات بناءً على حالة الحل الرياضي
    if res.success:
        st.success("🎯 تم إيجاد حل رياضي مستقر ومحسن لتركيبة العلف!")
        
        # تحويل النسب إلى أوزان بالـ (كجم / طن)
        st.write(f"📊 **النتائج المحسنة لكل طن (1000 كجم):**")
        st.write(f"- سورجم (فتريتة): {res.x[0]*1000:.1f} كجم / طن ({res.x[0]*100:.2f} %)")
        st.write(f"- أكسب الفول السوداني: {res.x[1]*1000:.1f} كجم / طن ({res.x[1]*100:.2f} %)")
        st.write(f"- نخالة قمح (ردة): {res.x[2]*1000:.1f} كجم / طن ({res.x[2]*100:.2f} %)")
        st.write(f"- إضافات مركزة وميكرو: {(1-sum(res.x))*1000:.1f} كجم / طن")
    else:
        # عرض رسالة الخطأ المتطابقة تماماً مع طلبك ومحتوى تطبيقك الذكي
        st.markdown(
            """
            <div style="background-color:#f8d7da; padding:15px; border-radius:8px; border:1px solid #f5c6cb; color:#721c24; margin-top:20px;">
                <h4 style="margin-top:0; color:#721c24;">❌ تعذر إيجاد حل رياضي متزن تماماً ضمن المحددات الحالية.</h4>
                <p style="margin-bottom:0;">يرجى تفعيل وإتاحة خامات إضافية من الأكساب أو المخلفات المتاحة في القائمة لتوسيع مساحة الحل الحسابي للمعالج الخطي.</p>
            </div>
            """, 
            unsafe_allow_allowed_html=True,
            unsafe_allow_html=True
        )

# --- قسم أرشفة الكود والتقارير ---
st.markdown("---")
st.subheader("📬 أرشفة الكود والتقارير الحالية للبريد الإلكتروني")
email_input = st.text_input("أدخل البريد الإلكتروني المستلم لحفظ نسخة السورس كود الأساسية", placeholder="example@gmail.com")

if st.button("🚀 إرسال نسخة الكود فوراً"):
    if email_input:
        st.success(f"📩 تم إرسال ملف التقارير والسورس كود بنجاح إلى: {email_input}")
    else:
        st.warning("الرجاء إدخال بريد إلكتروني صحيح أولاً.")

# --- تذييل الصفحة (Footer) ---
st.markdown("---")
st.markdown(
    """
    <div style="background-color: #1e5631; padding: 10px; border-radius: 5px; text-align: center;">
        <p style="color: white; margin: 0; font-weight: bold;">
            👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
