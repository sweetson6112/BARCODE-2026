import streamlit as st
import pandas as pd
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Barcode Scanner", layout="centered")
st.title("📦 Barcode Scanner System")

REQUIRED_COLUMNS = ["Item Number", "Description", "Barcode"]

# ---------------- SESSION STATE ----------------
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
    st.info("Please upload the master file.")
    st.stop()

try:
    master_df = pd.read_excel(uploaded_file)
except:
    st.error("Unable to read file.")
    st.stop()

if not all(col in master_df.columns for col in REQUIRED_COLUMNS):
    st.error(f"Excel must contain columns: {REQUIRED_COLUMNS}")
    st.stop()

st.success("Master file loaded successfully")

# ---------------- PROCESS BARCODE ----------------
def process_barcode():
    barcode = st.session_state.barcode_input.strip()

    if barcode == "":
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

        st.success("✅ Barcode matched")
        st.session_state.barcode_input = ""

    else:
        st.session_state.pending_barcode = barcode
        st.session_state.barcode_input = ""

# ---------------- SCAN INPUT ----------------
st.subheader("🔍 Scan Barcode")

st.text_input(
    "Scan barcode and press Enter",
    key="barcode_input",
    on_change=process_barcode
)

# ---------------- NEW ITEM ENTRY ----------------
if st.session_state.pending_barcode:
    st.warning(f"⚠ Barcode not found: {st.session_state.pending_barcode}")

    temp_item = st.text_input("Temp Item Code", key="temp_item")
    temp_desc = st.text_input("Temp Description", key="temp_desc")
    temp_remark = st.text_input("Remark", value="New Item", key="temp_remark")

    if st.button("Save New Item"):
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

            st.success("New item saved")

            st.session_state.pending_barcode = None
            st.session_state.temp_item = ""
            st.session_state.temp_desc = ""
            st.session_state.temp_remark = "New Item"

# ---------------- DISPLAY ----------------
st.subheader("📋 Scanned Items")
st.dataframe(st.session_state.output_df, use_container_width=True)

# ---------------- EXPORT ----------------
def convert_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.download_button(
    "⬇ Download Excel",
    data=convert_excel(st.session_state.output_df),
    file_name="scanned_output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---------------- CLEAR ----------------
if st.button("🗑 Clear All"):
    st.session_state.output_df = pd.DataFrame(
        columns=["Item Number", "Description", "Barcode", "Remark"]
    )
    st.session_state.pending_barcode = None
    st.success("All data cleared")