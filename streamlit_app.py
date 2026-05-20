if st.button("✅ تأكيد عملية البيع وخصم المكونات"):
    can_deduct = True
    
    # التحقق من توفر الكميات (مع استثناء الإنزيمات والإضافات التلقائية غير الموجودة بالمخزن)
    for name, pct in st.session_state["active_formula"].items():
        if name in st.session_state["inventory"]: # الخصم يتم فقط إذا كانت المادة معرفة في المخزن
            needed_qty = (pct / 100) * required_tons
            if st.session_state["inventory"][name] < needed_qty:
                can_deduct = False
                st.error(f"❌ رصيد غير كافي في المخزن لـ: {name} (المطلوب: {needed_qty:.2f} طن)")
                break
                
    if can_deduct:
        # إتمام عملية الخصم الفعلي للمكونات الأساسية المتوفرة
        for name, pct in st.session_state["active_formula"].items():
            if name in st.session_state["inventory"]:
                st.session_state["inventory"][name] -= ((pct / 100) * required_tons)
        st.success("🔥 تم الخصم التلقائي للمكونات وتحديث المخازن بنجاح!")
        st.rerun()
