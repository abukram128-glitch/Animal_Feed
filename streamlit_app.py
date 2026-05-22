import streamlit as st
import time

# إعدادات الصفحة
st.set_page_config(page_title="مستشار تركيب العلائق الذكي", layout="wide")

st.title("🌾 نظام تحسين وتركيب العلائق العلفية")
st.subheader("إدخال المضافات العلفية الإلزامية")

# 1. إجبارية اختيار الإنزيمات في الواجهة
st.markdown("### 🧬 المضافات الحيوية الإلزامية")
enzymes_selected = st.checkbox("إضافة الإنزيمات المعالجة (مكون إجباري لاستكمال التركيبة)", value=True, disabled=True) 
# تم تثبيته كـ True و تعطيله ليظل إجبارياً، أو يمكنك تركه كـ selectbox إجباري:

enzyme_type = st.selectbox(
    "اختر نوع الإنزيم المعالج المستهدف:",
    ["فيتاز (Phytase)", "كاربوهيدريز (Xylanase/Beta-Glucanase)", "بروتياز (Protease)"]
)

# 2. آلية إظهار مبرر العلة من الإضافة لمدة 40 ثانية
# نستخدم st.empty لإنشاء حاوية مؤقتة تختفي بعد انتهاء الوقت
justification_placeholder = st.empty()

with justification_placeholder.container():
    st.info(f"💡 **المبرر العلمي والعلة من إضافة إنزيم ({enzyme_type}):**")
    
    if "فيتاز" in enzyme_type:
        st.write("""
        * **تحرير الفوسفور المرتبط:** يعمل على تفكيك حمض الفيتيك (Phytic acid) في الخامات النباتية (مثل كسب الصويا والذرة)، مما يحرر الفوسفور العضوي ويقلل من الحاجة لإضافة فوسفور ثنائي الكالسيوم المكلف.
        * **تحسين الهضم:** يقلل من العوامل المضادة للتغذية ويحسن كفاءة تحويل الغذاء (FCR).
        """)
    elif "كاربوهيدريز" in enzyme_type:
        st.write("""
        * **معالجة الـ NSP:** يستهدف السكريات المتعددة غير النشوية (Non-Starch Polysaccharides) في خامات مثل الشعير أو كسب دوار الشمس، مما يقلل من لزوجة الأمعاء ويزيد من طاقة العليقة الممثلة.
        """)
    else:
        st.write("""
        * **هضم البروتينات المعقدة:** يعزز من الاستفادة القصوى من الأحماض الأمينية في الخامات البروتينية البديلة، ويقلل من النيتروجين المخفوض في الزرق.
        """)
    
    # شريط تقدم مرئي للمستخدم يبين الـ 40 ثانية
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for percent_complete in range(100):
        time.sleep(0.4) # 0.4 * 100 = 40 ثانية تماماً
        progress_bar.progress(percent_complete + 1)
        status_text.text(f"سيتخفى هذا التبرير العلمي تلقائياً بعد: {40 - int(percent_complete * 0.4)} ثانية")

# بعد انتهاء الـ 40 ثانية يتم مسح المحتوى تماماً من الواجهة
justification_placeholder.empty()
status_text.empty()

st.success("✅ تم تأكيد إدراج الإنزيمات المعالجة في حسابات العليقة بنجاح. يمكنك الانتقال الآن لخطوة التحسين الخطي (Linear Programming).")

# بقية كود الحسابات والمصفوفات الخاص بك...
