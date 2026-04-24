import streamlit as st
import pandas as pd
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Barcode Scanner", layout="centered")

st.title("📦 Barcode Scanner System")

# ---------------- ANIMATION ----------------
# Make sure this file exists in your repo
VIDEO_PATH = "watermarked_preview.mp4"

try:
    with open(VIDEO_PATH, "rb") as f:
        st.video(f.read())
except FileNotFoundError:
    st.info("Animation file not found. Add 'watermarked_preview.mp4' to your repo.")

REQUIRED_COLUMNS = ["Item Number", "Description", "Barcode"]

# ---------------- SESSION INIT ----------------
if "output_df" not in st.session_state:
    st.session_state.output_df = pd.DataFrame(
        columns=["Item Number", "Description", "Barcode", "Remark"]
    )

if "pending_barcode" not in st.session_state:
    st.session_state.pending_barcode = None

# ---------------- MASTER FILE ----------------
st.subheader("📂 Upload Master File")
uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

if not uploaded_file:
    st.info("Upload a master file to begin.")
    st.stop()

try:
    master_df = pd.read_excel(uploaded_file)
except Exception:
    st.error("❌ Failed to read Excel file.")
    st.stop()

# Validate required columns
if not all(col in master_df.columns for col in REQUIRED_COLUMNS):
    st.error(f"❌ File must contain columns: {REQUIRED_COLUMNS}")
    st.stop()

st.success("✅ Master data loaded")

# ---------------- PROCESS BARCODE ----------------
def process_barcode():
    barcode = st.session_state.barcode_input.strip()
    if not barcode:
        return

    match = master_df[master_df["Barcode"] == barcode]

    if not match.empty:
        row = match.iloc[0]
        new_row = {
            "Item Number": row["Item Number"],
            "Description": row["Description"],
            "Barcode": barcode,
            "Remark": "Barcode same as in system"
        }
        st.session_state.output_df = pd.concat(
            [st.session_state.output_df, pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success("✅ Match Found")
    else:
        st.session_state.pending_barcode = barcode
        st.warning(f"⚠️ New Barcode: {barcode}")

    # Safe clear (inside callback)
    st.session_state.barcode_input = ""

# ---------------- BARCODE INPUT ----------------
st.subheader("🔍 Scan Barcode")

st.text_input(
    "Scan or type barcode and press Enter",
    key="barcode_input",
    on_change=process_barcode
)

# ---------------- NEW ITEM FORM ----------------
if st.session_state.pending_barcode:
    st.markdown("### ➕ Enter New Item Details")

    with st.form("new_item_form", clear_on_submit=True):
        temp_item = st.text_input("Temp Item Code")
        temp_desc = st.text_input("Temp Description")
        temp_remark = st.text_input("Remark", value="New Item")

        submitted = st.form_submit_button("Save New Item")

        if submitted:
            if temp_item and temp_desc:
                new_row = {
                    "Item Number": temp_item,
                    "Description": temp_desc,
                    "Barcode": st.session_state.pending_barcode,
                    "Remark": temp_remark
                }

                st.session_state.output_df = pd.concat(
                    [st.session_state.output_df, pd.DataFrame([new_row])],
                    ignore_index=True
                )

                st.success("✅ New item saved")
                st.session_state.pending_barcode = None
            else:
                st.error("❌ Please fill all fields")

# ---------------- DISPLAY TABLE ----------------
st.subheader("📋 Scanned Items")
st.dataframe(st.session_state.output_df, use_container_width=True)

# ---------------- DOWNLOAD ----------------
def to_excel_bytes(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return buffer.getvalue()

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "⬇️ Download Excel",
        data=to_excel_bytes(st.session_state.output_df),
        file_name="scanned_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    if st.button("🗑️ Clear All"):
        st.session_state.output_df = pd.DataFrame(
            columns=["Item Number", "Description", "Barcode", "Remark"]
        )
        st.session_state.pending_barcode = None
        st.success("Data cleared")