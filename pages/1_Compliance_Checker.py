import streamlit as st
import pandas as pd

st.title("📋 Compliance Checker")

st.markdown("Upload your compliance-formatted ESG disclosure file (e.g., CSRD, SFDR format).")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    try:
        
        else:
            st.warning("⚠️ Missing expected columns like `Entity` or `Compliant`")

    except Exception as e:
        st.error(f"Error loading file: {e}")

