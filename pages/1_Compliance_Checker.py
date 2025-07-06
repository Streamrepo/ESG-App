import streamlit as st
import pandas as pd
import os
from compliance.validator import load_schema, validate_csv_row

st.title("🔍 ESG Compliance Checker (Single Company Selection)")

# Upload CSV
uploaded_file = st.file_uploader("Upload your ESG disclosures (.csv)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Data")
    st.dataframe(df)

    # Company Selector Dropdown
    company_names = df["Company_Name"].tolist()
    selected_company = st.selectbox("Select a company to validate", company_names)

    # Get the selected company row as dictionary
    selected_row = df[df["Company_Name"] == selected_company].iloc[0].to_dict()

    # Load schema
    schema_path = os.path.join("compliance", "sustainable_finance_schema.json")
    schema = load_schema(schema_path)

    # Validate selected row
    errors = validate_csv_row(selected_row, schema)

    st.subheader(f"📝 Validation for: {selected_company}")
    if not errors:
        st.success("✅ This company’s data is valid against the schema!")
    else:
        st.error("❌ Validation errors found:")
        for err in errors:
            st.write(f"• {err}")
