import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Barcode System", layout="wide")

# ------------------ DATABASE ------------------
conn = sqlite3.connect("barcode.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_number TEXT,
    description TEXT,
    barcode TEXT,
    remark TEXT,
    timestamp TEXT,
    user TEXT
)
""")
conn.commit()

# ------------------ SOUND ------------------
def play_sound(success=True):
    if success:
        st.audio("https://www.soundjay.com/buttons/sounds/beep-07.mp3")
    else:
        st.audio("https://www.soundjay.com/buttons/sounds/beep-10.mp3")

# ------------------ LOGIN ------------------
st.title("🔐 Barcode System Login")

if "user" not in st.session_state:
    username = st.text_input("Enter Username")

    if st.button("Login"):
        if username.strip():
            st.session_state.user = username.strip()
            st.success(f"Welcome {username}")
            st.rerun()
        else:
            st.error("Please enter a valid username")

    st.stop()

user = st.session_state.user

# ------------------ MAIN APP ------------------
st.title("📦 Barcode Intake & Dashboard")

# Upload master file
uploaded_file = st.file_uploader("Upload Master Excel", type=["xlsx"])

if uploaded_file:
    master_df = pd.read_excel(uploaded_file)
    master_df['Barcode'] = master_df['Barcode'].astype(str)

    st.success("✅ Master data loaded")

    # ------------------ TABS ------------------
    tab1, tab2 = st.tabs(["🔍 Scanner", "📊 Dashboard"])

    # =========================================================
    # 🔍 SCANNER TAB
    # =========================================================
    with tab1:

        st.subheader("Scan Barcode")
        barcode = st.text_input("Scan Barcode", key="barcode_input")

        if st.button("Submit Barcode"):

            if not barcode:
                st.warning("Please scan a barcode")
            else:
                barcode = barcode.strip()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Check duplicate (DO NOT BLOCK)
                cursor.execute("SELECT * FROM scans WHERE barcode=?", (barcode,))
                is_duplicate = cursor.fetchone() is not None

                match = master_df[master_df['Barcode'] == barcode]

                # ✅ FOUND IN MASTER
                if not match.empty:
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

                    if is_duplicate:
                        st.warning("⚠️ Duplicate scan recorded")
                    else:
                        st.success("✅ Item recorded")

                    play_sound(True)

                # ❌ NOT FOUND → MANUAL ENTRY
                else:
                    st.warning("⚠️ Barcode not found. Enter details below:")

                    with st.form("manual_form"):
                        item = st.text_input("Temporary Item Number")
                        desc = st.text_input("Description")
                        remark = st.text_input("Remark", value="New Item")

                        submit_new = st.form_submit_button("Save Item")

                        if submit_new:
                            if item and desc:
                                cursor.execute("""
                                INSERT INTO scans (item_number, description, barcode, remark, timestamp, user)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                                    item,
                                    desc,
                                    barcode,
                                    remark,
                                    timestamp,
                                    user
                                ))
                                conn.commit()

                                st.success("✅ New item saved")
                                play_sound(True)
                            else:
                                st.error("Please fill all fields")
                                play_sound(False)

        # ------------------ LIVE TABLE ------------------
        st.subheader("📋 Recent Scans")
        df = pd.read_sql_query("SELECT * FROM scans ORDER BY id DESC", conn)
        st.dataframe(df, use_container_width=True)

        # ------------------ DOWNLOAD ------------------
        if not df.empty:
            excel_file = "scanned_items.xlsx"
            df.to_excel(excel_file, index=False)

            with open(excel_file, "rb") as f:
                st.download_button(
                    "⬇ Download Excel",
                    f,
                    file_name="scanned_items.xlsx"
                )

    # =========================================================
    # 📊 DASHBOARD TAB
    # =========================================================
    with tab2:

        st.subheader("📊 Dashboard")

        df = pd.read_sql_query("SELECT * FROM scans", conn)

        if not df.empty:

            # KPIs
            total_scans = len(df)
            unique_barcodes = df['barcode'].nunique()
            duplicate_scans = len(df[df['remark'] == "Duplicate Scan"])
            new_items = len(df[df['remark'] == "New Item"])

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Scans", total_scans)
            col2.metric("Unique Barcodes", unique_barcodes)
            col3.metric("Duplicate Scans", duplicate_scans)
            col4.metric("New Items", new_items)

            st.divider()

            # ---------------- USER ANALYTICS ----------------
            st.subheader("👤 Scans by User")

            user_counts = df['user'].value_counts().reset_index()
            user_counts.columns = ['User', 'Scans']
            st.bar_chart(user_counts.set_index('User'))

            # ---------------- TIME ANALYTICS ----------------
            st.subheader("📅 Scans Over Time")

            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date

            time_counts = df.groupby('date').size()
            st.line_chart(time_counts)

        else:
            st.info("No data available yet. Start scanning.")