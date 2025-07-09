import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.compliance_checker import check_compliance
from utils.csrd_summary_generator import generate_csrd_summary
from PIL import Image


# Load EY logo
ey_logo = Image.open("assets/ey_logo.png")  # Adjust path if needed

# Create horizontal layout
col1, col2 = st.columns([3, 1])  # Wider left column for title

with col1:
    st.title("CSRD Compliance Checker")

with col2:
    st.image(ey_logo, width=250)  # Adjust width to fit nicely


uploaded_file = st.file_uploader("Upload CSRD Compliance CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # ✅ Limit to top 10 rows (0–9), drop blank/empty rows
    df_subset = df.iloc[:10].copy()
    df_subset.dropna(how="all", inplace=True)

    st.subheader("📊 Compliance Data (Top 10 Required Rows)")
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

    # ✅ Compliance check (only top 10)
    df_compliance = check_compliance(df_subset)

    # 🚨 Show non-compliant rows with notes
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

    # 📋 Final compliance table
    st.subheader("📋 Full Compliance Table")
    st.dataframe(df_compliance)

    # 📝 Summary paragraph + chart side by side
    st.subheader("📘 Compliance Summary")
    col1, col2 = st.columns([2, 1])

    with col1:
        summary = generate_csrd_summary(df_subset)
        st.text_area("Narrative Summary", summary, height=300)

    with col2:
        compliant_count = (df_compliance["Compliance"] == "✔️").sum()
        non_compliant_count = (df_compliance["Compliance"] == "❌").sum()

        fig, ax = plt.subplots(figsize=(4, 2))
        ax.barh(["Compliant", "Non-Compliant"], [compliant_count, non_compliant_count], color=["#cccccc", "#ffe600"])
        ax.set_xlim(0, 10)
        ax.set_xlabel("Count")
        ax.set_title("Disclosures Compliance")
        for i, v in enumerate([compliant_count, non_compliant_count]):
            ax.text(v + 0.2, i, str(v), va='center')
        st.pyplot(fig)
