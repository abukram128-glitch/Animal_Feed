
            # --- هنا تم دمج كود FCR المعدل ---
            st.markdown('<div class="section-title">📈 خامساً: حاسبة كفاءة التحويل الغذائي (FCR)</div>', unsafe_allow_html=True)
            col_fcr1, col_fcr2 = st.columns(2)
            with col_fcr1:
                total_feed_consumed = st.number_input("إجمالي كمية العلف المستهلكة (كجم):", min_value=0.0, value=100.0)
            with col_fcr2:
                total_weight_gained = st.number_input("الوزن الناتج (لحم/حليب) (كجم):", min_value=0.1, value=50.0)

            if total_weight_gained > 0:
                fcr = total_feed_consumed / total_weight_gained
                st.metric("معامل التحويل الغذائي (FCR):", f"{fcr:.2f}")
                if fcr < 2.0: st.success("🌟 كفاءة تحويل ممتازة!")
                elif fcr < 4.0: st.info("✅ كفاءة تحويل جيدة.")
                else: st.warning("⚠️ كفاءة تحويل منخفضة.")
            # -------------------------------
