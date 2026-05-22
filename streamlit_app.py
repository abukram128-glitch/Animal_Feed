import streamlit as st
import pandas as pd
import pulp

# ==========================================
# 1. إعدادات الصفحة وتحسين المظهر (CSS) لمنع التداخل
# ==========================================
st.set_page_config(page_title="منصة تاور الذكية للأعلاف", layout="wide")

st.markdown(
    """
    <style>
    /* تحسين عرض المقاييس ومنع تداخل النصوص */
    .stMetric {
        padding: 15px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    
    /* تنسيق شريط الحقوق السفلي الاحترافي */
    .footer-text {
        font-family: 'Cairo', sans-serif;
        font-size: 14px;
        color: #ffffff;
        text-align: center;
        background-color: #1e4620;
        padding: 15px;
        border-radius: 8px;
        margin-top: 40px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        direction: rtl;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. قواعد البيانات (المكتبة الجغرافية والغذائية)
# ==========================================

# قاعدة بيانات الجغرافيا المحدثة بفرع دارفور والمدن الأخرى
sudan_geography = {
    "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
    "ولاية الجزيرة": ["ود مدني", "المناقل", "الحصاحيصا"],
    "ولاية شمال دارفور": ["الفاشر", "كبكابية", "مليط"],
    "ولاية جنوب دارفور": ["نيالا", "كاس", "عد الفرسان"],
    "ولاية غرب دارفور": ["الجنينة", "كلبس"],
    "ولاية شرق دارفور": ["الضعين", "عسلاية"],
    "ولاية وسط دارفور": ["زالنجي", "روكرو"],
    "ولاية البحر الأحمر": ["بورتسودان", "سواكن"],
    "ولاية القضارف": ["القضارف", "الفاو"],
    "ولاية كسلا": ["كسلا", "حلفا الجديدة"]
}

# مكتبة الإنزيمات المتخصصة
enzymes_db = {
    "Protease (البروتياز المتخصص)": {"default_pct": 0.04, "cost": 2500},
    "Phytase (الفايتيز)": {"default_pct": 0.015, "cost": 1800},
    "Xylanase (الزيلانيز)": {"default_pct": 0.02, "cost": 2000}
}

# مكتبة الأحماض الأمينية النقية
amino_acids_db = {
    "DL-Methionine": {"CP_eq": 58.1, "Methionine": 99.0, "Lysine": 0.0, "max_pct": 0.5, "cost": 3200},
    "L-Lysine HCl": {"CP_eq": 94.0, "Methionine": 0.0, "Lysine": 78.4, "max_pct": 0.8, "cost": 2800},
    "L-Threonine": {"CP_eq": 72.0, "Methionine": 0.0, "Lysine": 0.0, "max_pct": 0.4, "cost": 3000}
}

# ==========================================
# 3. واجهة المستخدم (Streamlit Sidebar & Inputs)
# ==========================================
st.title("🌾 منصة تاور الذكية للمكونات والأعلاف المتكاملة")

# قوائم اختيار الموقع الجغرافي
st.sidebar.header("📍 النطاق الجغرافي والتسعير")
selected_state = st.sidebar.selectbox("اختر الولاية:", list(sudan_geography.keys()))
selected_city = st.sidebar.selectbox("اختر المدينة أو أقرب سوق:", sudan_geography[selected_state])

# احتياجات العليقة المستهدفة (مثال مبسط)
st.sidebar.header("📊 المواصفات المستهدفة للعليقة")
target_protein = st.sidebar.slider("البروتين الخام المستهدف (%)", 14.0, 24.0, 18.0)

# ==========================================
# 4. محرك البرمجة الخطية ومعالجة قيد الصويا المتنافي
# ==========================================

def optimize_feed(target_cp):
    # إنشاء مسألة تقليل التكلفة
    prob = pulp.LpProblem("Least_Cost_Feed", pulp.LpMinimize)
    
    # تعريف متغيرات المكونات الأساسية (النسب المئوية)
    corn = pulp.LpVariable("ذرة صفراء", lowBound=0, upBound=100)
    soya_44 = pulp.LpVariable("كسب فول صويا 44%", lowBound=0, upBound=100)
    soya_48 = pulp.LpVariable("كسب فول صويا 48%", lowBound=0, upBound=100)
    concentrates = pulp.LpVariable("مركزات خيول ومجترات", lowBound=0, upBound=10)
    
    # --- الحل البرمجي لمنع خلط صنفي الصويا معاً ---
    # متغيرات ثنائية (0 أو 1)
    y_soya_44 = pulp.LpVariable("use_soya_44", cat="Binary")
    y_soya_48 = pulp.LpVariable("use_soya_48", cat="Binary")
    
    # ربط النسبة بالمتغير الثنائي (M هو الحد الأقصى المسموح به للصويا في العليقة، مثلاً 40%)
    M = 40
    prob += soya_44 <= y_soya_44 * M
    prob += soya_48 <= y_soya_48 * M
    
    # قيد التنافي التام: مجموع الاختيارات لا يتعدى 1 (إما 44%، أو 48%، أو لا أحد منهما)
    prob += y_soya_44 + y_soya_48 <= 1
    
    # دالة الهدف: تقليل التكلفة (أسعار افتراضية للطن)
    prob += (corn * 280) + (soya_44 * 550) + (soya_48 * 600) + (concentrates * 1200)
    
    # القيود الغذائية الأساسية
    prob += corn + soya_44 + soya_48 + concentrates == 98.5 # ترك مساحة للأملاح والإضافات والأنزيمات
    
    # قيد البروتين (الذرة 8.5%، صويا 44%، صويا 48%، المركزات 40%)
    prob += (corn * 0.085) + (soya_44 * 0.44) + (soya_48 * 0.48) + (concentrates * 0.40) == target_cp
    
    # حل المسألة
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if pulp.LpStatus[status] == "Optimal":
        return {
            "ذرة صفراء": corn.varValue,
            "كسب فول صويا 44%": soya_44.varValue,
            "كسب فول صويا 48%": soya_48.varValue,
            "مركزات خيول ومجترات": concentrates.varValue,
            "التكلفة المحسوبة": pulp.value(prob.objective)
        }
    else:
        return None

# تشغيل محرك التحسين
results = optimize_feed(target_protein)

# ==========================================
# 5. عرض النتائج والتركيب النهائي للعليقة
# ==========================================

st.subheader(r"📋 المكونات المحسوبة للعليقة وسلسلة الإضافات المتكاملة")

if results:
    # عرض النتائج في أعمدة متناسقة لمنع التداخل
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔹 المكونات الأساسية (الخوارزمية الذكية)")
        for key, value in results.items():
            if key != "التكلفة المحسوبة" and value > 0:
                st.info(f"**{key}:** {value:.2f}% ➡️ ({value*10:.1f} كجم / طن)")
                
    with col2:
        st.markdown("### 🧪 الإنزيمات والأحماض الأمينية المضافة")
        # استدعاء وعرض الإنزيمات من المكتبة الجديدة
        for enz, data in enzymes_db.items():
            st.success(f"**{enz}:** {data['default_pct']}% ➡️ ({data['default_pct']*10:.2f} كجم / طن)")
            
        # استدعاء وعرض الأحماض الأمينية كمثال إضافي ثابت للتوليفة
        st.success(f"**DL-Methionine:** 0.15% ➡️ (1.50 كجم / طن)")

    # قسم التكلفة والموقع لمنع تداخل أسفل الشاشة
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="📍 سوق التسعير الفعلي الحالي", value=f"{selected_city} - {selected_state}")
    with c2:
        total_cost = results["التكلفة المحسوبة"]
        st.metric(label="💰 التكلفة الفعلية لإنتاج العلف (تقديرية للطن)", value=f"${total_cost:.2f}")

else:
    st.error("لم يتم العثور على حل رياضي يطابق نسب البروتين المطلوبة، يرجى تعديل المدخلات.")

# ==========================================
# 6. شريط التوقيع والحقوق المعالج مسبقاً
# ==========================================
st.markdown(
    '<div class="footer-text">👨‍💻 م. عبد القادر إسماعيل تاور © 2026 | الخبرة الذكية للثروة والبرمجيات المتكاملة</div>', 
    unsafe_allow_html=True
)
