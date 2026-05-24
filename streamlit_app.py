# --- بداية منطقة المالك فقط ---
if st.session_state["user_role"] == "admin":
    st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1565C0; text-align:right;'>📨 أرشفت الكود والتقارير للمالك فقط</h3>", unsafe_allow_html=True)

    col_mail, col_btn = st.columns([0.7, 0.3])
    with col_mail:
        target_email = st.text_input("أدخل البريد الإلكتروني المستلم:", placeholder="example@gmail.com")
    with col_btn:
        st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("إرسال نسخة الكود للمالك 🚀", use_container_width=True):
            if target_email:
                with st.spinner("جاري المعالجة..."):
                    if send_code_to_mail(target_email):
                        st.success("تم الإرسال.")
            else: st.warning("اكتب البريد أولاً.")
# --- نهاية منطقة المالك فقط ---
