import streamlit as st
import pandas as pd

st.title("CSRD Compliance Checker")

# File uploader
uploaded_file = st.file_uploader("Upload CSRD Compliance CSV", type=["csv"])

# Initialize session state
if "show_fill_form" not in st.session_state:
    st.session_state.show_fill_form = False
if "df" not in st.session_state:
    st.session_state.df = None

if uploaded_file is not None:
    if st.session_state.df is None:
        st.session_state.df = pd.read_csv(uploaded_file)

    df = st.session_state.df
    df_subset = df.iloc[:10]  # Only check first 10 rows

    # Detect missing values
    missing_mask = df_subset.iloc[:, 3].isna() | df_subset.iloc[:, 5].isna()
    missing_rows = df_subset[missing_mask]

    # Flag missing data
    if not missing_rows.empty:
        st.markdown("### 🔍 Missing Data Issues")
        for _, row in missing_rows.iterrows():
            st.markdown(
                f"<span style='color:red; font-weight:bold;'>⚠️ {row['Section']} {row['Disclosure ID']} is missing data</span>",
                unsafe_allow_html=True
            )

        # Toggle fill-in form
        label = "Close Fill Missing Data" if st.session_state.show_fill_form else "Fill Missing Data"
        if st.button(label):
            st.session_state.show_fill_form = not st.session_state.show_fill_form

        # Show fill-in form
        if st.session_state.show_fill_form:
            st.markdown("### 📝 Fill in the missing values below:")
            for idx in missing_rows.index:
                section = df.at[idx, 'Section']
                disc_id = df.at[idx, 'Disclosure ID']

                new_response = st.text_input(f"Response Type for {section} {disc_id}", key=f"response_{idx}")
                new_evidence = st.text_input(f"Evidence Reference for {section} {disc_id}", key=f"evidence_{idx}")

                if new_response:
                    df.at[idx, df.columns[3]] = new_response
                if new_evidence:
                    df.at[idx, df.columns[5]] = new_evidence

    else:
        st.success("✅ All mandatory fields (rows 0–9) have been filled!")

    # Show the live-updating single table
    st.subheader("📊 Compliance Table (Live)")
    st.dataframe(df.iloc[:10])
