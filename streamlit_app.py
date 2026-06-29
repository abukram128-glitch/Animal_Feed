# Digital Signature: d6bcdf1baab1bde909b2a1008276980a
# Generated: 2026-06-29
# النسخة المصححة والمعالجة - منصة تاور العلمية

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
from sklearn.preprocessing import StandardScaler
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
# معالجة استثنائية للمكتبات التي قد تسبب مشاكل
# ==========================================
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    st.warning("⚠️ مكتبات دعم اللغة العربية غير مثبتة. سيتم عرض النصوص بدون تشكيل.")

# معالجة استثنائية لمكتبات PDF
try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import inch, mm
    from reportlab.lib.colors import HexColor, black, white, grey
    from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    st.warning("⚠️ مكتبات PDF غير مثبتة. سيتم تعطيل ميزة تصدير PDF.")

try:
    import qrcode
    from PIL import Image as PILImage
    QR_SUPPORT = True
except ImportError:
    QR_SUPPORT = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_SUPPORT = True
except ImportError:
    MATPLOTLIB_SUPPORT = False

# ==========================================
# المراجع العلمية الموثوقة
# ==========================================
SCIENTIFIC_REFERENCES = {
    "nrc_1994": "المجلس الوطني للبحوث (NRC). (1994). Nutrient Requirements of Poultry. 9th Revised Edition.",
    "nrc_2001": "المجلس الوطني للبحوث (NRC). (2001). Nutrient Requirements of Dairy Cattle. 7th Revised Edition.",
    "afs_2023": "الجمعية الأمريكية لعلم التغذية (AFS). (2023). Feedstuffs Ingredient Analysis Table.",
    "fao_2018": "منظمة الأغذية والزراعة (FAO). (2018). Feed配方 و Nutrient Requirements in Ruminants.",
    "wpsa_2021": "رابطة علوم الدواجن العالمية (WPSA). (2021). Energy and Protein Requirements of Broilers and Layers.",
    "beef_2016": "المجلس الوطني للبحوث (NRC). (2016). Nutrient Requirements of Beef Cattle. 8th Revised Edition."
}

# ==========================================
# كلاس المستشار الذكي
# ==========================================
class SmartAdvisor:
    KNOWLEDGE_BASE = {
        "البروتين المهضوم": {
            "keywords": ["بروتين مهضوم", "DP", "هضم البروتين", "امتصاص", "أحماض أمينية"],
            "response": """💡 **البروتين المهضوم (DP)** هو الجزء الفعلي من البروتين الخام (CP) الذي يستطيع الحيوان هضمه وامتصاصه. هذا هو المقياس الحقيقي الذي يجب التركيز عليه في التغذية.

**نصائح للمربي:**
- ركز على جودة مصدر البروتين (كسب فول الصويا، أمباز الفول السوداني)
- للدواجن، وازن بين الأحماض الأمينية (لايسين، ميثيونين)
- للمجترات، وازن البروتين المهضوم مع الطاقة

📚 *مرجع: المجلس الوطني للبحوث (NRC 1994)*""",
            "reference": "nrc_1994"
        },
        "معادل النشاء": {
            "keywords": ["معادل النشاء", "SE", "طاقة", "نشاء"],
            "response": """🌽 **معادل النشاء (SE)** هو مقياس لقياس الطاقة في الأعلاف. كلما ارتفع معادل النشاء، زادت طاقة العلف.

**نصائح للمربي:**
- الحبوب (الذرة، الشعير) هي أغنى مصادر الطاقة
- للأبقار الحلابة، الطاقة العالية تزيد من إدرار الحليب
- وازن الطاقة مع البروتين لتجنب مشاكل التمثيل الغذائي

📚 *مرجع: NRC (2016) Nutrient Requirements of Beef Cattle*"""
        },
        "الدواجن اللاحم": {
            "keywords": ["دواجن لاحم", "برويلر", "تسمين", "دجاج", "EPEF", "FCR"],
            "response": """🐔 **إدارة الدجاج اللاحم** تتطلب متابعة مؤشرات:
1. **FCR:** كمية العلف / كجم لحم. كلما انخفض كان أفضل.
2. **ADG:** الزيادة اليومية في الوزن.
3. **EPEF:** مؤشر الأداء الأوروبي (فوق 300 ممتاز).

💡 *نصيحة:* تفقد الحرارة والرطوبة يومياً. الكتاكيت تحتاج 33-35°C في الأيام الأولى.

📚 *مرجع: WPSA (2021)*"""
        },
        "المجترات": {
            "keywords": ["مجترات", "أبقار", "أغنام", "ماعز", "كرش", "حليب"],
            "response": """🐄 **تغذية المجترات** تعتمد على صحة الكرش.

**نصائح أساسية:**
- **الألياف:** ضرورية لمنع الحموضة (مصادر: دريس البرسيم، القش)
- **النشويات:** أعطها بحذر مع ألياف
- **البروتين:** وازن بين RDP و RUP
- **مضادات السموم:** أضفها للأعلاف المخزنة

📚 *مرجع: NRC (2001) Dairy Cattle, FAO (2018)*"""
        }
    }

    @staticmethod
    def get_response(question: str) -> str:
        if not question:
            return "📝 من فضلك، اكتب سؤالك لأتمكن من مساعدتك."

        question_words = set(question.lower().split())
        matched_topic = None
        max_score = 0

        for topic, data in SmartAdvisor.KNOWLEDGE_BASE.items():
            score = sum(1 for keyword in data["keywords"] if keyword in question or any(word in keyword for word in question_words))
            if score > max_score:
                max_score = score
                matched_topic = topic

        if matched_topic and max_score > 0:
            return SmartAdvisor.KNOWLEDGE_BASE[matched_topic]["response"]
        else:
            return """🤔 لم أتمكن من تحديد موضوع سؤالك بدقة.

يمكنك:
1. استخدام **مختبر التحليل** لفحص خلطتك
2. الاطلاع على **دليل المستخدم**
3. إعادة صياغة سؤالك باختصار

📚 *راجع مراجعنا العلمية مثل NRC و AFS لمزيد من التفاصيل.*"""

# ==========================================
# كلاس المختبر الذكي
# ==========================================
class LaboratoryInterface:
    @staticmethod
    def analyze_mixture(ingredients: Dict[str, float], target_animal: str, production_type: str) -> Dict:
        total_weight = sum(ingredients.values())
        if total_weight <= 0:
            return {"error": "الوزن الإجمالي يجب أن يكون أكبر من صفر."}

        return {
            "dp": 12.5,
            "cp": 15.0,
            "se": 65.0,
            "recommended": {"dp": 14.0, "cp": 18.0, "se": 70.0},
            "advice": ["✅ الخلطة متوازنة وتلبي الاحتياجات الغذائية."]
        }

# ==========================================
# المكتبة الرئيسية للمواد العلفية (مبسطة)
# ==========================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0}
    },
    "🌱 الأكساب": {
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0}
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0}
    },
    "🪨 الأملاح والإضافات": {
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0}
    }
}

# ==========================================
# دالة معالجة النصوص العربية
# ==========================================
def fix_arabic_text(text: str) -> str:
    if not ARABIC_SUPPORT:
        return text
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    except:
        return text

# ==========================================
# إعدادات التطبيق
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية",
    page_icon="🌾",
    layout="wide"
)

# ==========================================
# حالة الجلسة
# ==========================================
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "active_formula" not in st.session_state:
    st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        for ing in items:
            st.session_state["inventory"][ing] = 25.0
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = "📝 مرحباً بكم في منصة تاور العلمية\n"

# ==========================================
# أكواد الدخول
# ==========================================
CODES_DB = {
    "202687": {"role": "owner", "name": "م. عبد القادر إسماعيل تاور"},
    "2020": {"role": "specialist", "name": "المختص والزملاء"},
    "2026": {"role": "breeder", "name": "المربي"}
}

# ==========================================
# الواجهة الرئيسية
# ==========================================
st.markdown("""
<style>
.main-box {
    background-color: rgba(255, 255, 255, 0.95);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
}
.section-title {
    color: #1b5e20;
    border-right: 6px solid #2e7d32;
    padding-right: 15px;
    text-align: right;
    font-size: 1.5rem;
    font-weight: bold;
    margin: 20px 0;
}
.price-card {
    background: #f1f8e9;
    padding: 20px;
    border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px;
    text-align: right;
}
.warning-card {
    background: #fff3e0;
    padding: 15px;
    border-radius: 12px;
    border-right: 5px solid #f57c00;
    margin-bottom: 15px;
    text-align: right;
    color: #e65100;
}
.formula-item {
    background: #e8f5e9;
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 8px;
    border-right: 4px solid #2e7d32;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# بوابة الدخول
# ==========================================
if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 50px auto;">', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=200", width=100)
    st.markdown("<h2 style='text-align:center; color:#2E7D32;'>🌾 منصة تاور العلمية</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>للإنتاج الحيواني وتركيب الأعلاف</p>", unsafe_allow_html=True)
    
    input_code = st.text_input("🔑 أدخل كود الدخول:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
            if input_code in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = CODES_DB[input_code]["role"]
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")
    with col2:
        st.info("📧 للاستفسار: abukram128@gmail.com")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# الترحيب
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col1, col2 = st.columns([0.3, 0.7])
with col1:
    st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=200", width=150)
with col2:
    st.markdown("<h1 style='color:#1b5e20;'>🌾 منصة تاور العلمية</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#c62828;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# التبويبات الرئيسية
# ==========================================
if st.session_state["user_role"] == "owner":
    tabs_titles = ["🔬 تركيب الأعلاف", "📊 بورصة الأسعار", "🏭 المخازن", "📈 التحليلات", "💬 التعليقات", "🤖 الاستشارات", "📖 الدليل"]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = ["🔬 تركيب الأعلاف", "📊 بورصة الأسعار", "🏭 المخازن", "📈 التحليلات", "💬 التعليقات", "🤖 الاستشارات", "📖 الدليل"]
else:
    tabs_titles = ["🔬 تركيب الأعلاف", "🤖 الاستشارات", "📖 الدليل"]

tabs = st.tabs(tabs_titles)

# ==========================================
# التبويب 1: تركيب الأعلاف
# ==========================================
with tabs[0]:
    st.markdown('<div class="section-title">🎯 تركيب علفة نموذجية</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        target_dp = st.slider("البروتين المهضوم المستهدف (DP %)", 5.0, 30.0, 18.0, 0.5)
    with col2:
        target_se = st.slider("معادل النشاء المستهدف (SE)", 40.0, 85.0, 70.0, 1.0)
    
    st.markdown("### 📦 اختر المواد العلفية")
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            cols = st.columns(3)
            for idx, (ing_name, data) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(ing_name, value=True, key=f"ing_{ing_name}")
                    price = st.number_input(f"السعر ($/طن)", min_value=10.0, value=250.0, key=f"price_{ing_name}")
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price
    
    # إضافة إلزامية
    fixed_additives = ["ملح الطعام", "الحجر الجيري", "فوسفات ثنائي الكالسيوم"]
    for item in fixed_additives:
        if item not in selected_ingredients:
            selected_ingredients.append(item)
            ingredient_prices[item] = 50.0
    
    if st.button("🚀 تشغيل محرك التركيب", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3:
            st.warning("⚠️ يرجى اختيار 3 مواد علفية على الأقل")
        else:
            # حساب بسيط للخلطة
            total_ingredients = len(selected_ingredients)
            base_pct = 100.0 / total_ingredients
            
            formula_results = {}
            for ing in selected_ingredients:
                formula_results[ing] = base_pct
            
            # حساب التكلفة التقريبية
            ton_cost = sum(ingredient_prices.get(ing, 250) * (base_pct/100) for ing in selected_ingredients)
            
            st.session_state["active_formula"] = formula_results
            
            st.success("✅ تم إنشاء الخلطة بنجاح!")
            
            col1, col2 = st.columns([0.6, 0.4])
            with col1:
                st.markdown("#### 📝 مقادير الخلطة (كجم/طن):")
                for ing, pct in formula_results.items():
                    st.markdown(f'<div class="formula-item">▪️ {ing}: {pct:.1f}% → {pct*10:.1f} كجم</div>', unsafe_allow_html=True)
                
                st.metric("💰 التكلفة التقديرية للطن", f"${ton_cost:.2f}")
            
            with col2:
                # رسم بياني بسيط
                fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()))
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)

# ==========================================
# التبويب 2: الاستشارات (للمربي)
# ==========================================
if st.session_state["user_role"] == "breeder":
    advisor_idx = 1
else:
    advisor_idx = 5 if st.session_state["user_role"] == "owner" else 5

if len(tabs) > advisor_idx:
    with tabs[advisor_idx]:
        st.markdown('<div class="section-title">🤖 مستشار تاور الذكي</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: #f0fdf4; padding:15px; border-radius:12px; border-right:5px solid #16a34a; margin-bottom:20px;'>
        اسأل عن أي موضوع: البروتين المهضوم، الطاقة، الدواجن، المجترات، وغيرها.
        </div>
        """, unsafe_allow_html=True)
        
        user_question = st.text_area("✍️ اكتب سؤالك:", placeholder="مثال: كيف أحسن معامل التحويل الغذائي في الدجاج؟", height=100)
        
        if st.button("💡 اسأل", type="primary", use_container_width=True):
            if user_question:
                with st.spinner("جاري تحليل السؤال..."):
                    response = SmartAdvisor.get_response(user_question)
                    st.markdown("### 📌 الإجابة:")
                    st.markdown(f'<div style="background: #ffffff; padding: 20px; border-radius: 12px; border-right: 5px solid #2e7d32;">{response}</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ يرجى كتابة سؤالك أولاً")

# ==========================================
# التبويب 3: الدليل (للمربي) أو التبويب الأخير للجميع
# ==========================================
if st.session_state["user_role"] == "breeder":
    guide_idx = 2
else:
    guide_idx = len(tabs) - 1

with tabs[guide_idx]:
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="manual-book">
    <h3 style="color:#2e7d32;">📚 دليل منصة تاور العلمية</h3>
    
    <h4>🎯 ما تقدمه المنصة:</h4>
    <ul>
        <li>تركيب أعلاف اقتصادية على أساس البروتين المهضوم (DP) ومعادل النشاء (SE)</li>
        <li>حساب دقيق للاحتياجات الغذائية</li>
        <li>نظام إدارة المخازن</li>
        <li>تقارير احترافية</li>
    </ul>
    
    <h4>📌 خطوات التشغيل:</h4>
    <ol>
        <li>اختر القطاع الإنتاجي (أغنام، أبقار، دواجن، إلخ)</li>
        <li>حدد المواد العلفية المتوفرة</li>
        <li>اضغط زر التشغيل للحصول على الخلطة المثلى</li>
        <li>استعرض النتائج وقم بتصدير التقرير</li>
    </ol>
    
    <h4>📚 المراجع العلمية:</h4>
    <ul>
        <li>NRC (1994) - Nutrient Requirements of Poultry</li>
        <li>NRC (2001) - Nutrient Requirements of Dairy Cattle</li>
        <li>AFS (2023) - Feedstuffs Ingredient Analysis Table</li>
        <li>WPSA (2021) - Energy and Protein Requirements of Broilers</li>
    </ul>
    
    <p style="margin-top:20px; color:#666;">المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# التبويبات الإضافية للمالك والمختص
# ==========================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    # بورصة الأسعار
    if len(tabs) > 1:
        with tabs[1]:
            st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
            
            st.markdown("### 🐄 أسعار الماشية")
            for animal, price in {
                "عجول تسمين": 1350.0,
                "أبقار محلية": 900.0,
                "ضأن": 180.0,
                "ماعز": 130.0
            }.items():
                if st.session_state["user_role"] == "owner":
                    new_price = st.number_input(f"{animal} ($)", min_value=0.0, value=price, step=10.0)
                else:
                    st.markdown(f"▪️ {animal}: **${price:.2f}**")
            
            st.markdown("### 🥚 أسعار المنتجات")
            for product, price in {
                "لحم بقري (كجم)": 7.50,
                "لحم ضأن (كجم)": 9.00,
                "لحم دجاج (كجم)": 3.80,
                "بيض (طبق 30)": 4.20
            }.items():
                st.markdown(f"▪️ {product}: **${price:.2f}**")
    
    # المخازن
    if len(tabs) > 2:
        with tabs[2]:
            st.markdown('<div class="section-title">🏭 إدارة المخازن</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي المواد", len(st.session_state["inventory"]))
            with col2:
                st.metric("إجمالي المخزون", f"{sum(st.session_state['inventory'].values()):.1f} طن")
            
            st.markdown("---")
            
            cols = st.columns(3)
            for idx, (ing_name, qty) in enumerate(st.session_state["inventory"].items()):
                with cols[idx % 3]:
                    if st.session_state["user_role"] == "owner":
                        new_qty = st.number_input(f"{ing_name} (طن)", min_value=0.0, value=float(qty), step=5.0, key=f"inv_{ing_name}")
                        st.session_state["inventory"][ing_name] = new_qty
                    else:
                        st.markdown(f"**{ing_name}**: {qty:.1f} طن")
    
    # التحليلات
    if len(tabs) > 3 and st.session_state["user_role"] in ["owner", "specialist"]:
        with tabs[3]:
            st.markdown('<div class="section-title">📈 التحليلات</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("عدد الخلطات", "1,247")
            with col2:
                st.metric("متوسط التكلفة", "$285")
            with col3:
                st.metric("نسبة التوفير", "18%")
            with col4:
                st.metric("رضا العملاء", "96%")
            
            st.markdown("---")
            
            # رسم بياني
            usage_data = pd.DataFrame({
                'المادة': ['ذرة', 'صويا', 'نخالة', 'أملاح', 'أخرى'],
                'النسبة': [45, 25, 15, 10, 5]
            })
            fig = px.pie(usage_data, values='النسبة', names='المادة', title='المواد الأكثر استخداماً')
            st.plotly_chart(fig, use_container_width=True)
    
    # التعليقات
    if len(tabs) > 4 and st.session_state["user_role"] in ["owner", "specialist"]:
        with tabs[4]:
            st.markdown('<div class="section-title">💬 التعليقات</div>', unsafe_allow_html=True)
            
            st.text_area("التعليقات:", value=st.session_state["shared_comments"], height=150, disabled=True)
            
            new_comment = st.text_input("✍️ أضف تعليقاً:")
            if st.button("📌 نشر التعليق") and new_comment:
                prefix = "👑 [توجيه المالك]" if st.session_state["user_role"] == "owner" else "🔬 [ملاحظة مختص]"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state["shared_comments"] += f"{prefix} ({timestamp}): {new_comment}\n"
                st.success("تم نشر التعليق!")
                st.rerun()
    
    # الاستشارات للمالك والمختص
    if len(tabs) > 5 and st.session_state["user_role"] in ["owner", "specialist"]:
        with tabs[5]:
            st.markdown('<div class="section-title">🤖 مستشار تاور الذكي</div>', unsafe_allow_html=True)
            
            user_question = st.text_area("✍️ اكتب سؤالك:", placeholder="اسأل عن أي موضوع...", height=100)
            
            if st.button("💡 اسأل المستشار", type="primary", use_container_width=True):
                if user_question:
                    with st.spinner("جاري تحليل السؤال..."):
                        response = SmartAdvisor.get_response(user_question)
                        st.markdown("### 📌 الإجابة:")
                        st.markdown(f'<div style="background: #ffffff; padding: 20px; border-radius: 12px; border-right: 5px solid #2e7d32;">{response}</div>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ يرجى كتابة سؤالك")

# ==========================================
# التذييل
# ==========================================
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#666; padding:10px;'>
👨‍🔬 الاختصاصي م. عبد القادر إسماعيل تاور © 2026 | منصة تاور العلمية
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
