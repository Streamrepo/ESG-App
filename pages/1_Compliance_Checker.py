import streamlit as st
import pandas as pd
import os
from compliance.validator import load_schema, validate_csv_against_schema

st.title("🔍 ESG Compliance Checker")

# Upload CSV
uploaded_file = st.file_uploader("Upload your ESG disclosure file (.csv)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Data")
    st.dataframe(df)

    # Load JSON Schema
    schema_path = os.path.join("compliance", "sustainable_finance_schema.json")
    schema = load_schema(schema_path)

    # Validate against schema
    validation_results = validate_csv_against_schema(df, schema)

    st.subheader("✅ Schema Validation Results")
    for result in validation_results:
        if result["valid"]:
            st.success(f"Row {result['row']}: Valid")
        else:
            st.error(f"Row {result['row']} - Errors:")
            for err in result["errors"]:
                st.write(f"• {err}")
