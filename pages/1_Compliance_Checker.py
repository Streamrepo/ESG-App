import streamlit as st
import pandas as pd
from utils.compliance_checker import check_compliance  # External compliance logic

st.title("CSRD Compliance Checker")

uploaded_file = st.file_uploader("Upload CSRD Compliance CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Compliance Data (Top 10 Required Rows)")
    df_subset = df.iloc[:10].copy()  # Only rows 0–9 are required
    df_subset.dropna(how="all", inplace=True)  # Remove empty rows if any
    st.dataframe(df_subset)

    # 🔍 Missing value check
    response_col = df.columns[3]
    evidence_col = df.columns[5]

    def is_missing(val):
        return pd.isna(val) or str(val).strip() == ""

    missing_mask = df_subset[response_col].apply(is_missing) | df_subset[evidence_col].apply(is_missing)
    missing_rows = df_subset[missing_mask]

    if not missing_rows.empty:
        st.markdown("### ❌ Missing Data Alerts")
        for _, row in missing_rows.iterrows():
            section = row['Section']
            disclosure = row['Disclosure ID']
            st.markdown(
                f"<span style='color:red; font-weight:bold;'>⚠️ {section} {disclosure} is missing data</span>",
                unsafe_allow_html=True
            )
    else:
        st.success("✅ All required disclosures (rows 0–9) have valid responses and evidence.")

    # ✅ Compliance check (only top 10 rows)
    df_compliance = check_compliance(df_subset)

    # 🚨 Flag non-compliant metrics
    non_compliant = df_compliance[df_compliance["Compliance"] == "❌"]

    if not non_compliant.empty:
        st.markdown("### 🚨 Non-Compliant Metrics")
        for _, row in non_compliant.iterrows():
            section = row['Section']
            disclosure = row['Disclosure ID']
            note = row['Notes']
            st.markdown(
                f"<span style='color:red; font-weight:bold;'>❌ {section} {disclosure} is not compliant</span><br>"
                f"<span style='color:#666;'>📝 {note}</span><br><br>",
                unsafe_allow_html=True
            )
    else:
        st.success("✅ All metrics are compliant.")

    # 📋 Show final table
    st.subheader("📋 Full Compliance Table")
    st.dataframe(df_compliance)
