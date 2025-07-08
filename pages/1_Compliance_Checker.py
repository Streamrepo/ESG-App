import streamlit as st
import pandas as pd

st.title("CSRD Compliance Checker")

# Upload
uploaded_file = st.file_uploader("Upload CSRD Compliance CSV", type=["csv"])

# Initialize state
if "show_fill_form" not in st.session_state:
    st.session_state.show_fill_form = False
if "df" not in st.session_state:
    st.session_state.df = None

if uploaded_file is not None:
    if st.session_state.df is None:
        st.session_state.df = pd.read_csv(uploaded_file)

    df = st.session_state.df
    df_subset = df.iloc[:10]  # First 10 required disclosures

    # Define columns
    response_col = df.columns[3]
    evidence_col = df.columns[5]

    # Detect truly missing (NaN or empty string) in either column
    missing_mask = df_subset[response_col].isna() | df_subset[response_col].eq("") | \
                   df_subset[evidence_col].isna() | df_subset[evidence_col].eq("")
    missing_rows = df_subset[missing_mask]

    if not missing_rows.empty:
        st.markdown("### 🔍 Missing Data Issues")
        for _, row in missing_rows.iterrows():
            st.markdown(
                f"<span style='color:red; font-weight:bold;'>⚠️ {row['Section']} {row['Disclosure ID']} is missing data</span>",
                unsafe_allow_html=True
            )

        toggle_label = "Close Fill Missing Data" if st.session_state.show_fill_form else "Fill Missing Data"
        if st.button(toggle_label):
            st.session_state.show_fill_form = not st.session_state.show_fill_form

        if st.session_state.show_fill_form:
            st.markdown("### 📝 Fill in the missing values below:")
            for idx in missing_rows.index:
                section = df.at[idx, 'Section']
                disc_id = df.at[idx, 'Disclosure ID']

                # Only show input if value is missing
                if pd.isna(df.at[idx, response_col]) or df.at[idx, response_col] == "":
                    response_input = st.text_input(
                        f"Response Type for {section} {disc_id}", key=f"response_{idx}"
                    )
                    if response_input:
                        df.at[idx, response_col] = response_input

                if pd.isna(df.at[idx, evidence_col]) or df.at[idx, evidence_col] == "":
                    evidence_input = st.text_input(
                        f"Evidence Reference for {section} {disc_id}", key=f"evidence_{idx}"
                    )
                    if evidence_input:
                        df.at[idx, evidence_col] = evidence_input

    else:
        st.success("✅ All mandatory fields (rows 0–9) have been filled!")

    # Show live-updating table
    st.subheader("📊 Compliance Table (Live)")
    st.dataframe(df.iloc[:10])
