# --- Compliance Checker: Core Section 1 ---
# Company Profile Setup

import streamlit as st
import pandas as pd

st.title("🏢 Company Profile Setup")
st.markdown("""
Define company-level metadata that influences disclosure requirements.
- Upload or input: Name, Sector (NACE code), Size, CSRD Scope
- Used to filter relevant disclosure requirements (ESRS applicability)
""")

# --- Option 1: Upload Metadata CSV ---
metadata_file = st.file_uploader("Upload company metadata file (optional)", type=["csv"])

if metadata_file:
    try:
        metadata_df = pd.read_csv(metadata_file)
        st.success("Company metadata loaded successfully.")
        selected_company = st.selectbox("Select company to analyze", metadata_df["Company"])
        company_profile = metadata_df[metadata_df["Company"] == selected_company].iloc[0]
        st.write("### Selected Company Metadata:")
        st.json(company_profile.to_dict())
    except Exception as e:
        st.error(f"Error reading file: {e}")

# --- Option 2: Manual Input ---
st.markdown("---")
st.subheader("Or enter company info manually")

company_name = st.text_input("Company Name")
sector_nace = st.text_input("Sector (NACE Code)")
company_size = st.selectbox("Company Size", ["S", "LM", "UM", "L"])
csrd_scope = st.selectbox("CSRD Applicability", ["In Scope", "Out of Scope"])

if company_name:
    st.success("Company metadata saved in session.")
    company_metadata = {
        "Company": company_name,
        "Sector": sector_nace,
        "Size": company_size,
        "CSRD Scope": csrd_scope
    }
    st.json(company_metadata)
