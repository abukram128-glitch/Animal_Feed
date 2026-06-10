import streamlit as st

# تهيئة الحالة
if "pending_lab_requests" not in st.session_state:
    st.session_state["pending_lab_requests"] = []
if "next_request_id" not in st.session_state:
    st.session_state["next_request_id"] = 1

st.title("تجربة ربط التركيب بالمختبر")

# تبويب التركيب (محاكاة)
with st.expander("تبويب التركيب (محاكاة)"):
    if st.button("محاكاة إرسال خلطة للتحليل"):
        new_request = {
            "request_id": st.session_state["next_request_id"],
            "target_species": "دواجن لاحم",
            "formula": {"ذرة": 60, "صويا": 30},
            "status": "pending"
        }
        st.session_state["pending_lab_requests"].append(new_request)
        st.session_state["next_request_id"] += 1
        st.success(f"تم إرسال الطلب رقم {new_request['request_id']}")
        st.rerun()

# تبويب المختبر
with st.expander("تبويب المختبر"):
    st.write("### طلبات التحليل الواردة")
    pending = [r for r in st.session_state["pending_lab_requests"] if r["status"] == "pending"]
    if not pending:
        st.info("لا توجد طلبات")
    else:
        for req in pending:
            with st.expander(f"طلب {req['request_id']}"):
                st.write(req)
                if st.button(f"إكمال الطلب {req['request_id']}"):
                    req["status"] = "completed"
                    st.rerun()
