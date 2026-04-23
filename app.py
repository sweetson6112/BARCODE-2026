import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Barcode Intake System", layout="centered")

# ------------------ DATABASE SETUP ------------------
conn = sqlite3.connect("barcode.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_number TEXT,
    description TEXT,
    barcode TEXT UNIQUE,
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
st.title("🔐 Login")

if "user" not in st.session_state:
    username = st.text_input("Enter Username")
    if st.button("Login"):
        if username.strip():
            st.session_state.user = username
            st.success(f"Welcome {username}")
        else:
            st.error("Enter valid username")
    st.stop()

user = st.session_state.user

# ------------------ MAIN APP ------------------
st.title("📦 Barcode Intake System")

uploaded_file = st.file_uploader("Upload Master Excel", type=["xlsx"])

if uploaded_file:
    master_df = pd.read_excel(uploaded_file)
    master_df['Barcode'] = master_df['Barcode'].astype(str)

    st.success("Master loaded!")

    st.subheader("🔍 Scan Barcode")
    barcode = st.text_input("Scan Barcode")

    if st.button("Submit"):

        if not barcode:
            st.warning("Scan a barcode")
        else:
            barcode = barcode.strip()

            # 🔁 DUPLICATE CHECK
            cursor.execute("SELECT * FROM scans WHERE barcode=?", (barcode,))
            if cursor.fetchone():
                st.error("❌ Duplicate barcode already scanned")
                play_sound(False)
            else:
                match = master_df[master_df['Barcode'] == barcode]

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # ✅ MATCH FOUND
                if not match.empty:
                    row = match.iloc[0]

                    cursor.execute("""
                    INSERT INTO scans (item_number, description, barcode, remark, timestamp, user)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        row['ItemNumber'],
                        row['Description'],
                        barcode,
                        "",
                        timestamp,
                        user
                    ))
                    conn.commit()

                    st.success("✅ Item recorded")
                    play_sound(True)

                # ❌ NOT FOUND
                else:
                    st.warning("⚠️ Not found. Enter details:")

                    with st.form("manual_form"):
                        item = st.text_input("Temporary Item Number")
                        desc = st.text_input("Description")
                        remark = st.text_input("Remark", value="New Item")

                        submit_new = st.form_submit_button("Save")

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
                                st.error("Fill all fields")
                                play_sound(False)

    # ------------------ DISPLAY ------------------
    st.subheader("📊 Scanned Data")

    df = pd.read_sql_query("SELECT * FROM scans", conn)
    st.dataframe(df)

    # DOWNLOAD
    excel_file = "scanned_items.xlsx"
    df.to_excel(excel_file, index=False)

    with open(excel_file, "rb") as f:
        st.download_button(
            "⬇ Download Excel",
            f,
            file_name="scanned_items.xlsx"
        )

    st.info("👉 Use Ctrl+P to print")