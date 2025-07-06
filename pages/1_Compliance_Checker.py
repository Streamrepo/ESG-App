import streamlit as st
import pandas as pd

st.title("ESG Compliance Checker")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your ESG CSV file", type=["csv"])

if uploaded_file:
    # Read uploaded CSV into DataFrame
    df_input = pd.read_csv(uploaded_file)
    st.subheader("📥 Uploaded Data")
    st.dataframe(df_input)

    # Optional: Convert to dictionary for later logic
    input_dict = dict(zip(df_input['field_id'], df_input['value']))
    st.write("Parsed Input Dictionary:")
    st.json(input_dict)
