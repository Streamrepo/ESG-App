import streamlit as st
import pandas as pd

st.title("CSRD Compliance Checker")

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSRD Compliance CSV", type=["csv"])

# Session state for toggling fill-in form
if "show_fill_form" not in st.session_state:
    st.session_state.show_fill_form = False

# Store the updated DataFrame persistently across reruns
if "df" not in st.session_state:
    st.session_state.df = None

if uploaded_file is not None:
    if st.session_state.df is None:
        st.session_state.df = pd.read_csv(uploaded_file)

    df = st.session_state.df

    st.subheader("CSRD Template Preview (Top 10 Required Rows)")
    df_subset = df.iloc[:10].copy()
    st.dataframe(df_subset)

    # Check for missing values in Response Type or Evidence Reference
    missing_mask = df_subset.iloc[:, 3].isna() | df_subset.iloc[:, 5].isna()
    missing_rows = df_subset[missing_mask]

    if not missing_rows.empty:
        st.markdown("### 🔍 Missing Data Issues")
        for _, row in missing_rows.iterrows():
            st.markdown(
                f"<span style='color:red; font-weight:bold;'>⚠️ {row['Section']} {row['Disclosure ID']} is missing data</span>",
                unsafe_allow_html=True
            )

        # Toggle button
        toggle_label = "Close Fill Missing Data" if st.session_state.show_fill_form else "Fill Missing Data"
        if st.button(toggle_label):
            st.session_state.show_fill_form = not st.session_state.show_fill_form

        if st.session_state.show_fill_form:
            st.markdown("### 📝 Fill in the missing values below:")
            for idx in missing_rows.index:
                section = df.at[idx, 'Section']
                disc_id = df.at[idx, 'Disclosure ID']

                response = st.text_input(f"Response Type for {section} {disc_id}", key=f"resp_{idx}")
                evidence = st.text_input(f"Evidence Reference for {section} {disc_id}", key=f"evid_{idx}")

                if response:
                    df.at[idx, df.columns[3]] = response
                if evidence:
                    df.at[idx, df.columns[5]] = evidence

            st.success("✅ Missing data updated below.")

            # Show updated table live
            st.subheader("🔄 Updated Data (Top 10 Rows)")
            st.dataframe(df.iloc[:10])
    else:
        st.success("✅ All mandatory fields (rows 0–9) have been filled!")
