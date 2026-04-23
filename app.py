import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Barcode Scanner", layout="centered")

st.title("📦 Barcode Scanner System")

# ---- Upload Master File ----
st.subheader("📂 Upload Master Data")

uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

required_cols = ["Item Number", "Description", "Barcode"]

if uploaded_file:
    try:
        master_df = pd.read_excel(uploaded_file)

        # Validate columns
        if not all(col in master_df.columns for col in required_cols):
            st.error(f"File must contain columns: {required_cols}")
            st.stop()

        st.success("✅ Master data loaded successfully")

    except Exception as e:
        st.error("Error reading file")
        st.stop()
else:
    st.info("Please upload a master Excel file to begin")
    st.stop()

# ---- Initialize Output ----
if "output_df" not in st.session_state:
    st.session_state.output_df = pd.DataFrame(
        columns=["Item Number", "Description", "Barcode", "Remark"]
    )

# ---- Barcode Input ----
st.subheader("🔍 Scan Barcode")

barcode = st.text_input("Scan or enter barcode", key="barcode_input")

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
        st.warning("⚠️ New Item")

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

    # Clear input for next scan
    st.session_state.barcode_input = ""

# ---- Display Table ----
st.subheader("📋 Scanned Items")
st.dataframe(st.session_state.output_df, use_container_width=True)

# ---- Convert to Excel ----
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# ---- Download Button ----
st.download_button(
    label="⬇️ Download Excel",
    data=to_excel(st.session_state.output_df),
    file_name="scanned_output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---- Clear Data ----
if st.button("🗑️ Clear All"):
    st.session_state.output_df = pd.DataFrame(
        columns=["Item Number", "Description", "Barcode", "Remark"]
    )
    st.success("Data cleared")