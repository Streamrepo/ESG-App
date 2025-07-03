import streamlit as st
import pandas as pd

st.title("📋 Compliance Checker")
st.markdown("Upload your compliance-formatted ESG disclosure file (e.g., Entity, Code, Disclosure...)")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Check expected columns
        if "Entity" in df.columns and "Disclosure" in df.columns:
            st.success("✅ File loaded successfully!")
            st.dataframe(df)
        else:
            st.warning("⚠️ Missing expected columns like `Entity` or `Disclosure`.")

    except Exception as e:
        st.error(f"Error loading file: {e}")
