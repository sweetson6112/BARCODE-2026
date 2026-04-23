import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Barcode Scanner", layout="centered")

st.title("📦 Barcode Scanner System")

MASTER_FILE = "master_data.xlsx"
OUTPUT_FILE = "scanned_output.xlsx"

# ---- Load Master Data ----
@st.cache_data
def load_master():
    return pd.read_excel(MASTER_FILE)

try:
    master_df = load_master()
except:
    st.error("Master file not found!")
    st.stop()

# ---- Initialize Output ----
if "output_df" not in st.session_state:
    if os.path.exists(OUTPUT_FILE):
        st.session_state.output_df = pd.read_excel(OUTPUT_FILE)
    else:
        st.session_state.output_df = pd.DataFrame(
            columns=["Item Number", "Description", "Barcode", "Remark"]
        )

# ---- Barcode Input ----
barcode = st.text_input("🔍 Scan Barcode", key="barcode_input")

if barcode:
    match = master_df[master_df["Barcode"] == barcode]

    if not match.empty:
        item_number = match.iloc[0]["Item Number"]
        description = match.iloc[0]["Description"]
        remark = "Barcode same as in system"
        st.success("✅ Match Found")
    else:
        item_number = "Unknown"
        description = "Unknown"
        remark = "New Item"
        st.warning("⚠️ New Item Detected")

    new_row = pd.DataFrame([{
        "Item Number": item_number,
        "Description": description,
        "Barcode": barcode,
        "Remark": remark
    }])

    st.session_state.output_df = pd.concat(
        [st.session_state.output_df, new_row],
        ignore_index=True
    )

    # Clear input
    st.session_state.barcode_input = ""

# ---- Display Table ----
st.subheader("📋 Scanned Items")
st.dataframe(st.session_state.output_df, use_container_width=True)

# ---- Save File ----
if st.button("💾 Save to Excel"):
    st.session_state.output_df.to_excel(OUTPUT_FILE, index=False)
    st.success("File saved successfully!")

# ---- Download Button ----
st.download_button(
    label="⬇️ Download Excel",
    data=st.session_state.output_df.to_excel(index=False, engine='openpyxl'),
    file_name="scanned_output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---- Clear Data ----
if st.button("🗑️ Clear All"):
    st.session_state.output_df = st.session_state.output_df.iloc[0:0]
    st.success("Data cleared!")