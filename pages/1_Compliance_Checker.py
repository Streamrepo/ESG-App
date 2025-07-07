import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSRD/ESRS Compliance Checker", layout="wide")

st.title("📋 CSRD/ESRS Compliance Checker")

# Step 1: Upload CSV
st.header("1️⃣ Upload Client Sustainability Data (.csv)")
uploaded_file = st.file_uploader("Upload your completed CSRD_ESRS_Client_Template.csv", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "Metric_Name", "Metric_Value", "Unit",
            "Date", "ESRS_Reference", "Notes"
        ]
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        else:
            st.success("✅ File successfully uploaded and parsed!")
            st.dataframe(df)

    except Exception as e:
        st.error(f"⚠️ Error reading CSV: {e}")

