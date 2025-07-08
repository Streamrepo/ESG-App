import streamlit as st
import pandas as pd

st.title("CSRD Compliance Checker")

# Upload CSV file only
uploaded_file = st.file_uploader("Upload CSRD Compliance CSV (no Option/Format column)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Current Data")
    st.dataframe(df)

    # Check for missing values in 'Response Type' column (column D or index 3)
    missing_mask = df.iloc[:, 3].isna()
    if missing_mask.any():
        st.warning("Missing values detected in 'Response Type':")
        for _, row in df[missing_mask].iterrows():
            st.text(f"{row['Section']} {row['Disclosure ID']} is missing data")

        st.subheader("Fill Missing 'Response Type' Values")
        for i in df[missing_mask].index:
            suggestion = st.text_input(
                f"Enter value for {df.at[i, 'Section']} {df.at[i, 'Disclosure ID']}:", key=f"input_{i}"
            )
            if suggestion:
                df.at[i, df.columns[3]] = suggestion

        # Show updated table
        st.subheader("Updated Data")
        st.dataframe(df)

        # Download button for corrected data
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Updated CSV", csv, "updated_compliance.csv", "text/csv")
    else:
        st.success("All 'Response Type' values are filled.")
