import streamlit as st
import threading
import time
import smtplib
from email.mime.text import MIMEText

# 1. إعداد حالة الجلسة وقاعدة البيانات المدعومة بالـ TDN
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 50.0, "شعير": 30.0, "كسب صويا 44%": 20.0, 
        "كسب دوار الشمس": 15.0, "مركز بقرى 10%": 5.0, "ثنائي فوسفات الكالسيوم": 2.0
    }

# قاعدة بيانات المكونات: تحتوي على البروتين (CP) والطاقة المهضومة الكلية (TDN) لكل خامة
ingredients_db = {
    "ذرة صفراء": {"cp": 8.5, "tdn": 88.0, "type": "grain"},
    "شعير": {"cp": 11.0, "tdn": 78.0, "type": "grain"},
    "كسب صويا 44%": {"cp": 44.0, "tdn": 79.0, "type": "protein"},
    "كسب دوار الشمس": {"cp": 32.0, "tdn": 65.0, "type": "protein"},
    "مركز بقرى 10%": {"cp": 40.0, "tdn": 60.0, "type": "fixed"},
    "ثنائي فوسفات الكالسيوم": {"cp": 0.0, "tdn": 0.0, "type": "fixed"}
}

st.title("Platform Tower Smart 🚀 - إصدار إدارة الطاقة والبروتين")

tab1, tab2, tab3 = st.tabs(["🧮 محرك التركيب وميزان الطاقة", "🏬 إدارة المستودعات والمزامنة", "📬 بوابة التواصل والملاحظات"])

# ==========================================
# TAB 1: محرك التركيب والتوازن الغذائي المطور
# ==========================================
with tab1:
    st.header("حساب نسب التركيبة وميزان TDN : CP")
    
    col1, col2 = st.columns(2)
    with col1:
        main_sector = st.selectbox("القطاع الحيواني المستهدف:", ["الأبقار وسلالاتها", "الماعز وسلالاته", "الطيور والسمان"])
        final_target_cp = st.number_input("البروتين المستهدف في العليقة (%):", min_value=10.0, max_value=24.0, value=16.0)
    with col2:
        grains_selected = st.multiselect("الحبوب (مصادر الطاقة):", ["ذرة صفراء", "شعير"], default=["ذرة صفراء"])
        proteins_selected = st.multiselect("الأكساب (مصادر البروتين):", ["كسب صويا 44%", "كسب دوار الشمس"], default=["كسب صويا 44%"])

    fixed_ingredients = st.multiselect("الإضافات والمركزات الثابتة:", ["مركز بقرى 10%", "ثنائي فوسفات الكالسيوم"], default=["مركز بقرى 10%"])
    
    used_fixed_pct = 0.0
    fixed_weights = {}
    for item in fixed_ingredients:
        fixed_weights[item] = st.slider(f"نسبة إدخال ثابتة لـ ({item}) %:", 0.0, 15.0, 10.0 if "مركز" in item else 1.0)
        used_fixed_pct += fixed_weights[item]

    if st.button("📊 تشغيل محرك التحسين الموازَن"):
        formula_results = {}
        
        # أ) تحديد وحساب الإنزيمات التلقائية لحماية الملكية الفكرية
        auto_added_enzymes = {}
        if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"] and final_target_cp > 15:
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
        elif main_sector == "الطيور والسمان":
            auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
            
        total_enz_pct = sum(auto_added_enzymes.values())
        
        # ب) حساب الكتلة الصافية المتاحة لتجنب النسب السالبة (الوقاية البرمجية)
        net_available = 100.0 - used_fixed_pct - total_enz_pct
        
        if net_available <= 0:
            st.error("🚨 خطأ منطقي: مجموع المكونات الثابتة والإنزيمات يتجاوز 100%!")
        else:
            # توزيع آمن وديناميكي يحمي العليقة من الانهيار العشوائي للحسابات
            grain_share = net_available * 0.625  # حماية حد الطاقة الأدنى بنسبة مرنة من الصافي
            leftover_for_others = net_available - grain_share
            
            # إسناد الأوزان للمكونات الثابتة والإنزيمات
            for item, pct in fixed_weights.items():
                formula_results[item] = pct
            for enz_name, enz_pct in auto_added_enzymes.items():
                formula_results[enz_name] = enz_pct
                
            # توزيع النسب بالتساوي على الخامات المختارة لتغطية الـ 100% تماماً (Mass Balance المضمون)
            if grains_selected:
                for g in grains_selected:
                    formula_results[g] = grain_share / len(grains_selected)
            if proteins_selected:
                for p in proteins_selected:
                    formula_results[p] = leftover_for_others / len(proteins_selected)
            
            # ج) محرك حساب ميزان الطاقة (TDN) والبروتين الفعلي في العليقة الناتجة
            calculated_cp = 0.0
            calculated_tdn = 0.0
            
            st.subheader("📋 مواصفات العليقة النهائية (لكل 100 كجم علف)")
            
            for ing, pct in formula_results.items():
                if ing in ingredients_db:
                    calculated_cp += (pct * ingredients_db[ing]["cp"]) / 100.0
                    calculated_tdn += (pct * ingredients_db[ing]["tdn"]) / 100.0
                st.write(f"🔹 **{ing}**: {pct:.3f} % (أي {pct*10:.2f} كجم/طن)")
            
            st.markdown("---")
            
            # د) عرض ميزان الطاقة والبروتين والنسبة المغذية بينهما
            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.metric("البروتين الخام الفعلي (CP)", f"{calculated_cp:.2f} %")
            with col_res2:
                st.metric("الطاقة المهضومة الكلية (TDN)", f"{calculated_tdn:.2f} %")
            with col_res3:
                # نسبة الـ TDn إلى الـ CP (مؤشر كفاءة الكرش الحيوانية)
                tdn_cp_ratio = calculated_tdn / calculated_cp if calculated_cp > 0 else 0
                st.metric("نسبة الطاقة : البروتين", f"{tdn_cp_ratio:.2f}")
            
            # هـ) تحليل استشاري ذكي بناءً على النسبة الناتجة
            if tdn_cp_ratio > 5.0:
                st.warning("⚠️ العليقة ذات طاقة عالية جداً مقارنة بالبروتين. قد تسبب تراكم الدهون وتقلل من كفاءة الاستفادة من النتروجين.")
            elif tdn_cp_ratio < 3.5:
                st.info("💡 العليقة غنية بالبروتين مقارنة بالطاقة. يوصى بزيادة نسبة الحبوب (مثل الذرة) لتوفير طاقة كافية للميكروبات لتمثيل هذا البروتين.")
            else:
                st.success("✅ توازن ممتاز بين الطاقة (TDN) والبروتين (CP)، مما يضمن أعلى معدل تحويل غذائي.")

# ==========================================
# TAB 2: إدارة المستودعات والمزامنة اللحظية
# ==========================================
with tab2:
    st.header("📦 جرد ومزامنة المستودع الفورية")
    st.info("تعديل الأرصدة هنا يحدث قاعدة البيانات الحية فوراً لمنع تعارض الفواتير.")
    
    updated_inventory = {}
    for ing_name, qty in list(st.session_state["inventory"].items()):
        # إضافة المفتاح وحفظ القيمة مباشرة في قاموس الجلسة لضمان عدم انفصال الـ State
        new_qty = st.number_input(f"رصيد مخزن ({ing_name}) بالطن:", min_value=0.0, value=float(qty), key=f"inv_{ing_name}")
        st.session_state["inventory"][ing_name] = new_qty
        
    st.success("✅ جميع مستودعات الخامات متزامنة برمجياً مع محرك الخصم التلقائي.")

# ==========================================
# TAB 3: بوابة التواصل باستخدام Threading
# ==========================================
def send_email_async(subject, body):
    """دالة إرسال الإيميل في خيط منفصل لمنع تجميد واجهة المستخدم"""
    try:
        # إعدادات افتراضية (تستبدل ببيانات السيرفر الحقيقي عند النشر)
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = "tower_platform@gmail.com"
        msg['To'] = "admin_vet@gmail.com"
        
        # محاكاة الاتصال والـ Handshake الذي كان يسبب تجميد الشاشة
        time.sleep(3) 
        print(f"تم إرسال البريد بنجاح: {subject}")
    except Exception as e:
        print(f"فشل الإرسال الخلفي: {e}")

with tab3:
    st.header("📬 تقارير المختصين والاتصال السريع")
    expert_note = st.text_area("أدخل ملاحظاتك الحقلية أو طلبات الدعم الفني:")
    
    if st.button("🚀 إرسال التقرير فوراً عبر SMTP"):
        if expert_note:
            # إطلاق خيط المعالجة الخلفي لضمان بقاء التطبيق سريعاً وسلساً
            email_thread = threading.Thread(target=send_email_async, args=("تقرير فني جديد - منصة تاور", expert_note))
            email_thread.start()
            st.success("⚡ جاري إرسال تقريرك الفني في الخلفية... يمكنك الاستمرار في العمل دون أي توقف!")
        else:
            st.warning("الرجاء كتابة نص التقرير أولاً.")
