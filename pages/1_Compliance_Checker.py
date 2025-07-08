import streamlit as st
import pandas as pd
import uuid

st.title("CSRD Compliance Checker")

uploaded_file = st.file_uploader("Upload CSRD Compliance CSV", type=["csv"])

# Session state setup
if "show_fill_form" not in st.session_state:
    st.session_state.show_fill_form = False
if "df" not in st.session_state:
    st.session_state.df = None

# Add a unique session ID to differentiate widget keys across runs
if "uid" not in st.session_state:
    st.session_state.uid = str(uuid.uuid4())[:8]

if uploaded_file is not None:
    if st.session_state.df is None:
        st.session_state.df = pd.read_csv(uploaded_file)

    df = st.session_state.df
    df_subset = df.iloc[:10]

    response_col = df.columns[3]
    evidence_col = df.columns[5]

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

        toggle_label = "Close Fill Missing Data" if st.session_state.show_fill_form else "Fill Missing Data"
        if st.button(toggle_label):
            st.session_state.show_fill_form = not st.session_state.show_fill_form

        if st.session_state.show_fill_form:
            st.markdown("### 📝 Fill in the missing values below:")

            for idx in missing_rows.index:
                section = df.at[idx, 'Section']
                disc_id = df.at[idx, 'Disclosure ID']

                unique_key = f"{disc_id}_{idx}_{st.session_state.uid}"

                with st.form(key=f"form_{unique_key}", clear_on_submit=True):
                    response_input = st.text_input(
                        f"Response Type for {section} {disc_id}",
                        key=f"resp_{unique_key}"
                    )
                    evidence_input = st.text_input(
                        f"Evidence Reference for {section} {disc_id}",
                        key=f"evid_{unique_key}"
                    )
                    submitted = st.form_submit_button("Save")

                    if submitted:
                        df.at[idx, response_col] = response_input
                        df.at[idx, evidence_col] = evidence_input
                        st.success(f"✅ Saved: {section} {disc_id}")

    else:
        st.success("✅ All mandatory fields (rows 0–9) have been filled!")

    # Live updated table
    st.subheader("📊 Compliance Table (Live)")
    st.dataframe(df.iloc[:10])
