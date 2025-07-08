import streamlit as st
import pandas as pd

st.title("CSRD Compliance Checker")

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSRD Compliance CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("CSRD Template Preview (Top 10 Required Rows)")
    df_subset = df.iloc[:10].copy()  # Only rows 0-9 are required checks
    st.dataframe(df_subset)

    # Identify rows with missing Response Type or Evidence Reference
    missing_mask = df_subset.iloc[:, 3].isna() | df_subset.iloc[:, 5].isna()
    missing_rows = df_subset[missing_mask]

    if not missing_rows.empty:
        st.markdown("### 🔍 Missing Data Issues")
        for _, row in missing_rows.iterrows():
            st.markdown(
                f"<span style='color:red; font-weight:bold;'>⚠️ {row['Section']} {row['Disclosure ID']} is missing data</span>",
                unsafe_allow_html=True
            )

        # Toggle input form with a button
        if st.button("Fill Missing Data"):
            st.markdown("### 📝 Fill in the missing values below:")
            for idx in missing_rows.index:
                current_section = df.at[idx, 'Section']
                current_id = df.at[idx, 'Disclosure ID']

                new_response = st.text_input(
                    f"Response Type for {current_section} {current_id}",
                    key=f"response_{idx}"
                )
                new_evidence = st.text_input(
                    f"Evidence Reference for {current_section} {current_id}",
                    key=f"evidence_{idx}"
                )

                # Update only if user fills the value
                if new_response:
                    df.at[idx, df.columns[3]] = new_response
                if new_evidence:
                    df.at[idx, df.columns[5]] = new_evidence

            st.success("Missing data filled in. You can now download the updated file.")

            # Offer download
            csv_updated = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Updated CSV",
                data=csv_updated,
                file_name="updated_compliance.csv",
                mime="text/csv"
            )
    else:
        st.success("✅ All mandatory fields (rows 0–9) have been filled!")
