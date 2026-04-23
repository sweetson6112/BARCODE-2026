import streamlit as st
import pandas as pd
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Barcode Scanner", layout="centered")

st.title("📦 Barcode Scanner System")

REQUIRED_COLUMNS = ["Item Number", "Description", "Barcode"]

# ---------------- SESSION INIT ----------------
if "output_df" not in st.session_state:
    st.session_state.output_df = pd.DataFrame(
        columns=["Item Number", "Description", "Barcode", "Remark"]
    )

# ---------------- FILE UPLOAD ----------------
st.subheader("📂 Upload Master File")

uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

if not uploaded_file:
    st.info("Upload a master file to start scanning.")
    st.stop()

try:
    master_df = pd.read_excel(uploaded_file)
except Exception:
    st.error("❌ Failed to read Excel file.")
    st.stop()

# Validate columns
if not all(col in master_df.columns for col in REQUIRED_COLUMNS):
    st.error(f"❌ File must contain columns: {REQUIRED_COLUMNS}")
    st.stop()

st.success("✅ Master data loaded")

# ---------------- BARCODE FUNCTION ----------------
def process_barcode():
    barcode = st.session_state.barcode_input.strip()

    if barcode == "":
        return

    match = master_df[master_df["Barcode"] == barcode]

    if not match.empty:
        row = match.iloc[0]
        new_data = {
            "Item Number": row["Item Number"],
            "Description": row["Description"],
            "Barcode": barcode,
            "Remark": "Barcode same as in system"
        }
        st.success("✅ Match Found")
    else:
        new_data = {
            "Item Number": "Unknown",
            "Description": "Unknown",
            "Barcode": barcode,
            "Remark": "New Item"
        }
        st.warning("⚠️ New Item")

    st.session_state.output_df = pd.concat(
        [st.session_state.output_df, pd.DataFrame([new_data])],
        ignore_index=True
    )

    # Clear input safely
    st.session_state.barcode_input = ""

# ---------------- BARCODE INPUT ----------------
st.subheader("🔍 Scan Barcode")

st.text_input(
    "Scan or type barcode and press Enter",
    key="barcode_input",
    on_change=process_barcode
)

# ---------------- DISPLAY TABLE ----------------
st.subheader("📋 Scanned Items")
st.dataframe(st.session_state.output_df, use_container_width=True)

# ---------------- DOWNLOAD FUNCTION ----------------
def convert_to_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return buffer.getvalue()

# ---------------- ACTION BUTTONS ----------------
col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "⬇️ Download Excel",
        data=convert_to_excel(st.session_state.output_df),
        file_name="scanned_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    if st.button("🗑️ Clear Data"):
        st.session_state.output_df = pd.DataFrame(
            columns=["Item Number", "Description", "Barcode", "Remark"]
        )
        st.success("Data cleared")