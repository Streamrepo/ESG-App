import streamlit as st
import pandas as pd

st.title("CSRD Compliance Checker")

uploaded_file = st.file_uploader("Upload CSRD Compliance CSV", type=["csv"])

# Init session state
if "show_fill_form" not in st.session_state:
    st.session_state.show_fill_form = False
if "df" not in st.session_state:
    st.session_state.df = None

if uploaded_file is not None:
    if st.session_state.df is None:
        st.session_state.df = pd.read_csv(uploaded_file)

    df = st.session_state.df
    df_subset = df.iloc[:10]

    response_col = df.columns[3]
    evidence_col = df.columns[5]

    # Treat NaN or empty string as missing
    def is_missing(val):
        return pd.isna(val) or str(val).strip() == ""

    missing_rows = df_subset[
        df_subset[response_col].apply(is_missing) | df_subset[evidence_col].apply(is_missing)
    ]

    if not missing_rows.empty:
        st.markdown("### 🔍 Missing Data Issues")
        for _, row in missing_rows.iterrows():
            st.markdown(
                f"<span style='color:red; font-weight:bold;'>⚠️ {row['Section']} {row['Disclosure ID']} is missing data</span>",
                unsafe_allow_html=True
            )

        # Toggle form
        toggle_label = "Close Fill Missing Data" if st.session_state.show_fill_form else "Fill Missing Data"
        if st.button(toggle_label):
            st.session_state.show_fill_form = not st.session_state.show_fill_form

        if st.session_state.show_fill_form:
            st.markdown("### 📝 Fill in the missing values below:")

            for idx in missing_rows.index:
                section = df.at[idx, 'Section']
                disc_id = df.at[idx, 'Disclosure ID']

                with st.form(key=f"form_{idx}", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        response_input = st.text_input(
                            f"Response Type for {section} {disc_id}", key=f"resp_{idx}"
                        )
                    with col2:
                        evidence_input = st.text_input(
                            f"Evidence Reference for {section} {disc_id}", key=f"evid_{idx}"
                        )
                    submitted = st.form_submit_button("Save")
                    if submitted:
                        if response_input:
                            df.at[idx, response_col] = response_input
                        if evidence_input:
                            df.at[idx, evidence_col] = evidence_input
                        st.experimental_rerun()  # Force rerun to refresh missing rows
    else:
        st.success("✅ All mandatory fields (rows 0–9) have been filled!")

    # Show only one live-updating table
    st.subheader("📊 Compliance Table (Live)")
    st.dataframe(df.iloc[:10])
