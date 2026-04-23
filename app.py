# ======================================================
# 🔍 SCANNER TAB (FIXED VERSION)
# ======================================================
with tab1:

    st.subheader("Scan Barcode")

    barcode_input = st.text_input("Scan Barcode", key="barcode_input")

    # ---------- SCAN BUTTON ----------
    if st.button("Submit Barcode"):

        if barcode_input.strip() == "":
            st.warning("Please scan a barcode")
        else:
            barcode = barcode_input.strip()
            st.session_state.pending_barcode = barcode  # ALWAYS store

            # Check master
            match = master_df[master_df['Barcode'] == barcode]

            if not match.empty:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # duplicate check
                cursor.execute("SELECT COUNT(*) FROM scans WHERE barcode=?", (barcode,))
                is_duplicate = cursor.fetchone()[0] > 0

                row = match.iloc[0]
                remark = "Duplicate Scan" if is_duplicate else ""

                cursor.execute("""
                INSERT INTO scans (item_number, description, barcode, remark, timestamp, user)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(row['ItemNumber']),
                    row['Description'],
                    barcode,
                    remark,
                    timestamp,
                    user
                ))
                conn.commit()

                st.success("✅ Item recorded")
                play_sound(True)

                # clear state AFTER insert
                st.session_state.pending_barcode = None
                st.rerun()

            else:
                st.warning("⚠️ Barcode not found. Enter details below.")

    # ---------- MANUAL ENTRY ----------
    if st.session_state.pending_barcode:

        with st.form("manual_form", clear_on_submit=True):

            st.info(f"Barcode: {st.session_state.pending_barcode}")

            item = st.text_input("Temporary Item Number")
            desc = st.text_input("Description")
            remark = st.text_input("Remark", value="New Item")

            save_btn = st.form_submit_button("Save Item")

            if save_btn:

                if item.strip() and desc.strip():

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    cursor.execute("""
                    INSERT INTO scans (item_number, description, barcode, remark, timestamp, user)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        item.strip(),
                        desc.strip(),
                        st.session_state.pending_barcode,
                        remark.strip(),
                        timestamp,
                        user
                    ))
                    conn.commit()

                    st.success("✅ New item saved")
                    play_sound(True)

                    # 🔥 CRITICAL FIX
                    st.session_state.pending_barcode = None
                    st.rerun()

                else:
                    st.error("Please fill all fields")
                    play_sound(False)

    # ---------- ALWAYS RELOAD DATA ----------
    st.subheader("📋 Recent Scans")

    df = pd.read_sql_query("SELECT * FROM scans ORDER BY id DESC", conn)

    st.dataframe(df, use_container_width=True)

    # ---------- DOWNLOAD ----------
    if not df.empty:
        excel_file = "scanned_items.xlsx"
        df.to_excel(excel_file, index=False)

        with open(excel_file, "rb") as f:
            st.download_button(
                "⬇ Download Excel",
                f,
                file_name="scanned_items.xlsx"
            )