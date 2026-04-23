import streamlit as st
import pandas as pd

st.set_page_config(page_title="Barcode Checker", layout="centered")

st.title("📦 Barcode Verification System")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Master Excel File", type=["xlsx"])

if uploaded_file:
    try:
        master_df = pd.read_excel(uploaded_file)
        master_df['Barcode'] = master_df['Barcode'].astype(str)

        st.success("Master data loaded successfully!")

        if "mismatches" not in st.session_state:
            st.session_state.mismatches = []

        st.subheader("🔍 Scan Item")

        item_number = st.text_input("Enter Item Number")
        scanned_barcode = st.text_input("Scan Barcode")

        if st.button("Check Barcode"):
            item_row = master_df[master_df['ItemNumber'] == item_number]

            if item_row.empty:
                st.error("Item not found in master data.")
            else:
                system_barcode = str(item_row.iloc[0]['Barcode'])
                description = item_row.iloc[0]['Description']

                if scanned_barcode == system_barcode:
                    st.success("✅ Barcode same as in system")
                else:
                    st.warning("⚠️ Barcode mismatch recorded")

                    st.session_state.mismatches.append({
                        'ItemNumber': item_number,
                        'Description': description,
                        'ScannedBarcode': scanned_barcode,
                        'SystemBarcode': system_barcode
                    })

        st.subheader("📊 Mismatch Records")

        if st.session_state.mismatches:
            mismatch_df = pd.DataFrame(st.session_state.mismatches)
            st.dataframe(mismatch_df)

            csv = mismatch_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Report",
                data=csv,
                file_name="mismatch_report.csv",
                mime="text/csv"
            )
        else:
            st.info("No mismatches recorded yet.")

    except Exception as e:
        st.error(f"Error processing file: {e}")