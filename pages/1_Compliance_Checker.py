import streamlit as st
import pandas as pd

st.title("CSRD Compliance Checker")

uploaded_file = st.file_uploader("Upload CSRD Compliance CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Compliance Data (Top 10 Required Rows)")
    df_subset = df.iloc[:10]  # Only rows 0–9 are required

    st.dataframe(df_subset)

    # Check for missing values in 'Response Type' (col 3) or 'Evidence Reference' (col 5)
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
