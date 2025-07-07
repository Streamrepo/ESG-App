import streamlit as st
import pandas as pd

st.title("🧾 CSRD/ESRS Compliance Checker - Upload Client File")

# Step 1: Upload section
uploaded_file = st.file_uploader("📤 Upload filled-in CSRD/ESRS template (.csv)", type=["csv"])

# Step 2: Read & display file
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Preview of uploaded data
        st.success("✅ File uploaded successfully!")
        st.subheader("📄 Uploaded Data Preview")
        st.dataframe(df)

        # Optional: check if required columns exist
        required_cols = ['Company_Name', 'Metric_Name', 'Metric_Value', 'Unit', 'Date', 'ESRS_Reference']
        if not all(col in df.columns for col in required_cols):
            st.error("❌ One or more required columns are missing in the CSV.")
        else:
            st.info("🧠 File structure is valid. Ready for compliance checking...")

    except Exception as e:
        st.error(f"❌ Error reading the file: {e}")
else:
    st.warning("👆 Please upload a completed client CSV to begin.")

