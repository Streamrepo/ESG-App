import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="CSRD/ESRS Compliance Checker", layout="wide")
st.title("📋 CSRD/ESRS Compliance Checker")

# Step 1: Upload Client CSV
st.header("1️⃣ Upload Client Sustainability Data (.csv)")
uploaded_file = st.file_uploader("Upload your completed CSRD_ESRS_Client_Template.csv", type=["csv"])

# Step 2: Load Rule Sets
@st.cache_data
def load_json_rules(file_name):
    try:
        rules_path = os.path.join("rules", file_name)
        with open(rules_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"⚠️ Could not load {file_name}: {e}")
        return []

presence_rules = load_json_rules("presence_rules.json")
compliance_rules = load_json_rules("compliance_rules.json")

if presence_rules and compliance_rules:
    st.success(f"✅ {len(presence_rules)} presence rules and {len(compliance_rules)} compliance rules loaded.")
    if st.checkbox("Show rule sets"):
        with st.expander("📘 Presence Rules"):
            st.json(presence_rules)
        with st.expander("📗 Compliance Rules"):
            st.json(compliance_rules)

# Step 3: Parse Uploaded CSV
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = ["Metric_Name", "Metric_Value", "Unit", "Date", "ESRS_Reference", "Notes"]
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        else:
            st.success("✅ File successfully uploaded and parsed!")
            st.dataframe(df)

            # Placeholder for next steps:
            st.info("🔧 Ready to apply presence & compliance checks...")

    except Exception as e:
        st.error(f"⚠️ Error reading CSV: {e}")
