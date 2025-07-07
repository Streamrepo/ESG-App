import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="CSRD/ESRS Compliance Checker")
st.title("✅ CSRD/ESRS Compliance Checker")

# --- Load Compliance Rules ---
rules_path = os.path.join("compliance", "rules.json")
try:
    with open(rules_path, "r") as f:
        rules = json.load(f)
except FileNotFoundError:
    st.error("rules.json file not found in /compliance folder.")
    st.stop()

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your ESG disclosure CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Data")
    st.dataframe(df)

    # Select company (assumes a Company_Name column exists)
    if "Company_Name" not in df.columns:
        st.error("Missing 'Company_Name' column in CSV.")
        st.stop()

    company_names = df["Company_Name"].dropna().unique().tolist()
    selected_company = st.selectbox("Select a company to check compliance", company_names)

    selected_row = df[df["Company_Name"] == selected_company].iloc[0].to_dict()

    # --- Compliance Check ---
    st.subheader(f"📋 Validation Results for: {selected_company}")
    compliant = []
    non_compliant = []

    for metric, rule in rules.items():
        value = selected_row.get(metric, "")
        status = "✅"
        message = "Valid"

        # Presence check
        if rule.get("required", False) and (pd.isna(value) or value == ""):
            status = "❌"
            message = "Missing required value"

        # Type check
        elif rule["type"] == "numeric":
            try:
                num = float(value)
                if "min" in rule and num < rule["min"]:
                    status = "❌"
                    message = f"Value {num} is below minimum {rule['min']}"
            except:
                status = "❌"
                message = "Expected numeric value"

        elif rule["type"] == "boolean":
            if str(value).strip().lower() not in ["yes", "no"]:
                status = "❌"
                message = "Expected 'Yes' or 'No'"

        result = {
            "field": metric,
            "value": value,
            "status": status,
            "message": message,
            "reg": rule.get("esrs", "N/A")
        }

        if status == "✅":
            compliant.append(result)
        else:
            non_compliant.append(result)

    # --- Show Results ---
    st.success(f"{len(compliant)} metrics compliant.")
    st.error(f"{len(non_compliant)} metrics non-compliant.")

    with st.expander("✅ Compliant Metrics"):
        st.dataframe(pd.DataFrame(compliant))

    with st.expander("❌ Non-Compliant Metrics"):
        st.dataframe(pd.DataFrame(non_compliant))
