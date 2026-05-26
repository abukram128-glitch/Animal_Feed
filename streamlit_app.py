import streamlit as st
import pandas as pd
import sqlite3
from scipy.optimize import linprog

# ==========================================
# 1. تهيئة قاعدة البيانات والترقية التلقائية
# ==========================================
def init_db():
    conn = sqlite3.connect("feed_ingredients.db")
    cursor = conn.cursor()
    
    # إنشاء جدول الخامات الرئيسي إذا لم يكن موجوداً
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cp REAL DEFAULT 0.0,
            me REAL DEFAULT 0.0,
            ca REAL DEFAULT 0.0,
            p_avail REAL DEFAULT 0.0,
            price REAL DEFAULT 0.0,
            min_limit REAL DEFAULT 0.0,
            max_limit REAL DEFAULT 100.0,
            is_fixed INTEGER DEFAULT 0,
            fixed_value REAL DEFAULT 0.0
        )
    """)
    
    # فحص وتحديث الأعمدة تلقائياً في حال نقصها (Auto-Migration)
    cursor.execute("PRAGMA table_info(ingredients)")
    columns = [col[1] for col in cursor.fetchall()]
    
    migrations = {
        "ca": "ALTER TABLE ingredients ADD COLUMN ca REAL DEFAULT 0.0",
        "p_avail": "ALTER TABLE ingredients ADD COLUMN p_avail REAL DEFAULT 0.0",
        "is_fixed": "ALTER TABLE ingredients ADD COLUMN is_fixed INTEGER DEFAULT 0",
        "fixed_value": "ALTER TABLE ingredients ADD COLUMN fixed_value REAL DEFAULT 0.0"
    }
    
    for col_name, sql_command in migrations.items():
        if col_name not in columns:
            cursor.execute(sql_command)
            
    conn.commit()
    conn.close()

init_db()

# دالة مساعدة لضمان تحويل البيانات التالفة أو الفارغة إلى أرقام آمنة
def get_float(val, default=0.0):
    try:
        if val is None or pd.isna(val):
            return default
        return float(val)
    except:
        return default

# ==========================================
# 2. واجهة مستخدم التطبيق (Streamlit UI)
# ==========================================
st.set_page_config(page_title="منظومة تركيب الأعلاف الذكية", layout="wide")
st.title("🌾 منظومة استمثال وتركيب الأعلاف الأقل تكلفة (Linear Programming)")
st.write(f"مرحباً بك يا مهندس عبد القادر إسماعيل | النسخة المستقرة والمحمية رياضياً")

# الاتصال بقاعدة البيانات لجلب البيانات الحالية
conn = sqlite3.connect("feed_ingredients.db")
df_ingredients = pd.read_sql_query("SELECT * FROM ingredients", conn)
conn.close()

# علامات التبويب (Tabs) لإدارة النظام
tab1, tab2 = st.tabs(["📊 حساب العليقة (الاستمثال)", "⚙️ إدارة خامات ومكونات العلف"])

# ------------------------------------------
# علامة التبويب الأولى: حساب العليقة والأمثلية الرياضية
# ------------------------------------------
with tab1:
    st.header("🎯 تحديد الاحتياجات الغذائية المطلوبة في الطن")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        req_cp = st.number_input("البروتين الخام المطلوب (%) Min CP", min_value=0.0, max_value=100.0, value=21.0, step=0.1)
    with col2:
        req_me = st.number_input("الطاقة الممثلة المطلوبة (kcal/kg) Min ME", min_value=0.0, max_value=4000.0, value=3000.0, step=10.0)
    with col3:
        req_ca = st.number_input("الكالسيوم المطلوب (%) Min Ca", min_value=0.0, max_value=10.0, value=1.0, step=0.05)
    with col4:
        req_p = st.number_input("الفسفور المتاح المطلوب (%) Min Avail P", min_value=0.0, max_value=10.0, value=0.45, step=0.05)

    st.subheader("📋 حدد الخامات والمضافات التي ستدخل في الحساب")
    
    # عرض الجدول للمستخدم لتحديد النسب والحدود برمجياً
    updated_data = []
    
    if df_ingredients.empty:
        st.warning("⚠️ قاعدة البيانات فارغة حالياً. يرجى الانتقال إلى علامة التبويب الثانية لإضافة الخامات أولاً.")
    else:
        for idx, row in df_ingredients.iterrows():
            st.markdown(f"**{row['name']}**")
            c1, c2, c3, c4, c5 = st.columns(5)
            
            with c1:
                use_ing = st.checkbox("إدخال في الحساب", value=True, key=f"use_{row['id']}")
            with c2:
                is_fixed = st.checkbox("نسبة ثابتة؟", value=bool(row['is_fixed']), key=f"fix_{row['id']}")
            with c3:
                fixed_val = st.number_input("النسبة الثابتة (%)", min_value=0.0, max_value=100.0, value=get_float(row['fixed_value']), key=f"fixval_{row['id']}")
            with c4:
                min_lim = st.number_input("الحد الأدنى (%)", min_value=0.0, max_value=100.0, value=get_float(row['min_limit']), key=f"min_{row['id']}")
            with c5:
                max_lim = st.number_input("الحد الأقصى (%)", min_value=0.0, max_value=100.0, value=get_float(row['max_limit'], 100.0), key=f"max_{row['id']}")
            
            if use_ing:
                updated_data.append({
                    "id": row['id'],
                    "name": row['name'],
                    "cp": get_float(row['cp']),
                    "me": get_float(row['me']),
                    "ca": get_float(row['ca']),
                    "p_avail": get_float(row['p_avail']),
                    "price": get_float(row['price']),
                    "min_limit": min_lim,
                    "max_limit": max_lim,
                    "is_fixed": 1 if is_fixed else 0,
                    "fixed_value": fixed_val
                })
            st.markdown("---")

    if st.button("🚀 احسب التركيبة الأقل تكلفة الآن", type="primary"):
        if not updated_data:
            st.error("❌ يرجى اختيار خامة واحدة على الأقل لإجراء الحسابات!")
        else:
            # فصل الخامات الكبرى (المتغيرة) عن الإضافات الثابتة (Fixed Fractions)
            fixed_weight = 0.0
            fixed_cp_contrib = 0.0
            fixed_me_contrib = 0.0
            fixed_ca_contrib = 0.0
            fixed_p_contrib = 0.0
            fixed_cost = 0.0
            
            variable_ingredients = []
            fixed_ingredients_summary = []
            
            for ing in updated_data:
                if ing['is_fixed'] == 1:
                    w = ing['fixed_value'] / 100.0  # تحويل النسبة إلى كسر
                    fixed_weight += ing['fixed_value']
                    fixed_cp_contrib += (ing['cp'] * w)
                    fixed_me_contrib += (ing['me'] * w)
                    fixed_ca_contrib += (ing['ca'] * w)
                    fixed_p_contrib += (ing['p_avail'] * w)
                    fixed_cost += (ing['price'] * w)
                    fixed_ingredients_summary.append(ing)
                else:
                    variable_ingredients.append(ing)
            
            # حساب الأهداف المتبقية للخامات المتغيرة لحماية أبعاد المصفوفات
            target_weight = 100.0 - fixed_weight
            target_cp = max(0.0, req_cp - fixed_cp_contrib)
            target_me = max(0.0, req_me - fixed_me_contrib)
            target_ca = max(0.0, req_ca - fixed_ca_contrib)
            target_p = max(0.0, req_p - fixed_p_contrib)
            
            if target_weight <= 0:
                st.error("❌ خطأ رياضي: مجموع نسب المضافات الثابتة يساوي أو يتجاوز 100%!")
            elif not variable_ingredients:
                st.error("❌ خطأ: لا توجد خامات متغيرة كافية للموازنة الحسابية وإقفال الطن!")
            else:
                # بناء المصفوفات الرياضية للمحرك الخطي (Linear Programming Matrices)
                num_vars = len(variable_ingredients)
                
                # 1. مصفوفة التكاليف (Objective Function)
                c = [ing['price'] for ing in variable_ingredients]
                
                # 2. مصفوفة قيود المتراجحات (Inequality Constraints: >= المطلوب)
                # نضرب في -1 لأن linprog يعتمد افتراضياً قيود الأصغر من (<=)
                A_ub = []
                b_ub = []
                
                # قيد البروتين
                A_ub.append([-ing['cp'] for ing in variable_ingredients])
                b_ub.append(-target_cp)
                
                # قيد الطاقة
                A_ub.append([-ing['me'] for ing in variable_ingredients])
                b_ub.append(-target_me)
                
                # قيد الكالسيوم
                A_ub.append([-ing['ca'] for ing in variable_ingredients])
                b_ub.append(-target_ca)
                
                # قيد الفسفور المتاح
                A_ub.append([-ing['p_avail'] for ing in variable_ingredients])
                b_ub.append(-target_p)
                
                # 3. مصفوفة قيود التساوي (Equality Constraint: إقفال النسبة المتبقية تماماً)
                A_eq = [[1.0] * num_vars]
                b_eq = [target_weight]
                
                # 4. حدود الخامات الفردية (Bounds)
                bounds = []
                for ing in variable_ingredients:
                    low = ing['min_limit']
                    high = ing['max_limit']
                    bounds.append((low, high))
                
                # تشغيل المحرك الخطي مع ميزة الحماية والتحول الذكي (Solver Fallback Guard)
                result = None
                solvers_to_try = ['highs', 'legacy']
                
                for solver in solvers_to_try:
                    try:
                        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method=solver)
                        if result.success:
                            break
                    except Exception:
                        continue # التحول الصامت للمحرك التالي في حال انهيار السيرفر الداخلي
                
                # عرض النتائج البرمجية والغذائية للمستخدم
                if result and result.success:
                    st.success("✅ تم احتساب العليقة الأمثل بنجاح بأقل تكلفة اقتصادية ممكنة!")
                    
                    final_mix = []
                    total_calculated_cost = fixed_cost
                    
                    # تفريغ الخامات المتغيرة الناتجة
                    for i, ing in enumerate(variable_ingredients):
                        qty = result.x[i]
                        cost_contrib = qty * (ing['price'] / 100.0)
                        total_calculated_cost += cost_contrib
                        final_mix.append({
                            "الخامة": ing['name'],
                            "النسبة في العلفة (%)": round(qty, 3),
                            "الكمية في الطن (كجم)": round(qty * 10, 2),
                            "الحالة": "متغيرة (مستمثلة)"
                        })
                        
                    # دمج الإضافات الثابتة في التقرير النهائي لتطابق الأبعاد
                    for ing in fixed_ingredients_summary:
                        final_mix.append({
                            "الخامة": ing['name'],
                            "النسبة في العلفة (%)": round(ing['fixed_value'], 3),
                            "الكمية في الطن (كجم)": round(ing['fixed_value'] * 10, 2),
                            "الحالة": "ثابتة محددة مسبقاً"
                        })
                    
                    # عرض جدول التركيبة النهائي
                    df_res = pd.DataFrame(final_mix)
                    st.table(df_res)
                    
                    # حساب القيم الغذائية الإجمالية المتحققة فعلياً في العلفة
                    actual_cp = fixed_cp_contrib + sum(variable_ingredients[i]['cp'] * (result.x[i]/100.0) for i in range(num_vars))
                    actual_me = fixed_me_contrib + sum(variable_ingredients[i]['me'] * (result.x[i]/100.0) for i in range(num_vars))
                    actual_ca = fixed_ca_contrib + sum(variable_ingredients[i]['ca'] * (result.x[i]/100.0) for i in range(num_vars))
                    actual_p = fixed_p_contrib + sum(variable_ingredients[i]['p_avail'] * (result.x[i]/100.0) for i in range(num_vars))
                    
                    st.subheader("📊 التحليل الغذائي الفعلي للعليقة الناتجة:")
                    cc1, cc2, cc3, cc4 = st.columns(4)
                    cc1.metric("البروتين الخام فعلياً", f"{round(actual_cp, 2)} %")
                    cc2.metric("الطاقة الممثلة فعلياً", f"{round(actual_me, 1)} kcal/kg")
                    cc3.metric("الكالسيوم الفعلي", f"{round(actual_ca, 2)} %")
                    cc4.metric("الفسفور المتاح فعلياً", f"{round(actual_p, 2)} %")
                    
                    st.metric("💰 التكلفة الإجمالية التقديرية للطن", f"{round(total_calculated_cost * 10, 2)} وحدة نقدية / طن")
                else:
                    st.error("❌ لم يتمكن النظام من إيجاد حل رياضي يطابق هذه القيود المعقدة. يرجى مراجعة الحدود الدنيا والعليا أو تقليل المتطلبات الغذائية لتوسيع نطاق الحل الحسابي.")

# ------------------------------------------
# علامة التبويب الثانية: إدارة قاعدة بيانات الخامات
# ------------------------------------------
with tab2:
    st.header("➕ إضافة خامة أو إضافة جديدة للمخزن")
    with st.form("add_ingredient_form"):
        name = st.text_input("اسم الخامة (مثال: ذرة صفراء، كسب فول صويا، حجر جيري)")
        cp = st.number_input("البروتين الخام (%) Crude Protein", min_value=0.0, max_value=100.0, value=0.0)
        me = st.number_input("الطاقة الممثلة (kcal/kg) Metabolizable Energy", min_value=0.0, max_value=4500.0, value=0.0)
        ca = st.number_input("الكالسيوم (%) Calcium", min_value=0.0, max_value=100.0, value=0.0)
        p_avail = st.number_input("الفسفور المتاح (%) Available Phosphorus", min_value=0.0, max_value=100.0, value=0.0)
        price = st.number_input("سعر الكيلو (أو وحدة الوزن المعيارية)", min_value=0.0, value=0.0)
        
        submitted = st.form_submit_with_clicks = st.form_submit_button("حفظ الخامة في قاعدة البيانات")
        if submitted and name:
            conn = sqlite3.connect("feed_ingredients.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ingredients (name, cp, me, ca, p_avail, price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, cp, me, ca, p_avail, price))
            conn.commit()
            conn.close()
            st.success(f"✅ تم حفظ الخامة '{name}' بنجاح! يرجى إعادة تحديث الصفحة لتظهر في الحسابات.")

    st.subheader("🗑️ الخامات المسجلة حالياً (يمكنك حذف أي خامة)")
    conn = sqlite3.connect("feed_ingredients.db")
    df_current = pd.read_sql_query("SELECT id, name, cp, me, ca, p_avail, price FROM ingredients", conn)
    conn.close()
    
    if not df_current.empty:
        for idx, row in df_current.iterrows():
            c_name, c_del = st.columns([4, 1])
            c_name.write(f"**{row['name']}** -> بروتين: {row['cp']}%, طاقة: {row['me']} kcal, كالسيوم: {row['ca']}%, فسفور: {row['p_avail']}%, سعر: {row['price']}")
            if c_del.button("حذف", key=f"del_{row['id']}"):
                conn = sqlite3.connect("feed_ingredients.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ingredients WHERE id = ?", (row['id'],))
                conn.commit()
                conn.close()
                st.success("تم الحذف بنجاح!")
                st.rerun()
    else:
        st.info("لا توجد خامات مسجلة حالياً.")
