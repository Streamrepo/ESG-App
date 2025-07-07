import streamlit as st
import pandas as pd
import json
import os

# Page setup
st.set_page_config(page_title="CSRD/ESRS Compliance Checker", layout="wide")
st.title("📋 CSRD/ESRS Compliance Checker")

# Step 1: Upload CSV
st.header("1️⃣ Upload Client Sustainability Data (.csv)")
uploaded_file = st.file_uploader("Upload your completed CSRD_ESRS_Client_Template.csv", type=["csv"])

# Step 2: Load compliance rules from JSON
@st.cache_data
def load_compliance_rules():
    try:
        rules_path = os.path.join("rules", "compliance_rules.json")
        with open(rules_path, "r") as f:
            rules = json.load(f)
        return rules
    except Exception as e:
        st.error(f"⚠️ Could not load compliance rules: {e}")
        return []

rules = load_compliance_rules()

if rules:
    st.success(f"✅ {len(rules)} compliance rules loaded from JSON.")
    if st.checkbox("Show compliance rule preview"):
        st.json(rules)

# Step 3: Display uploaded data
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
