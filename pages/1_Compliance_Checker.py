import streamlit as st
import pandas as pd

st.title("📋 Compliance Checker")

st.markdown(
    "Upload your compliance-formatted ESG disclosure file (e.g., `Entity`, `Code`, `Disclosure`...)"
)

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        st.success("✅ File uploaded!")
        st.dataframe(df)

        if all(col in df.columns for col in ["Entity", "Code", "Disclosure"]):
            st.info("✅ Detected required columns.")
            # Add your compliance logic here...
        else:
            st.warning("⚠️ Missing expected columns like `Entity`, `Code`, or `Disclosure`.")

    except Exception as e:
        st.error(f"⚠️ Error loading file: {e}")
