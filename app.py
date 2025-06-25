import streamlit as st
import pandas as pd

st.set_page_config(page_title="ESG Analyser", layout="centered")

st.title("🌿 ESG Analyser - Upload Your Company Data")

# Section: File Upload
st.header("1. Upload ESG Data CSV")
uploaded_file = st.file_uploader("Upload your ESG data (.csv)", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        required_columns = [
            "Company", "Industry", "Size", "GHG Emissions (tCO₂e)", "Renewable Energy %",
            "Water Usage (m³)", "Waste Recycled %", "Biodiversity Risk %",
            "Gender Pay Gap %", "Board Diversity %", "ESG KPIs in Exec Pay", "Transition Plan"
        ]

        # Check if all required columns are present
        if all(col in df.columns for col in required_columns):
            st.success("✅ File uploaded and validated successfully!")
            st.dataframe(df)
        else:
            st.error("❌ The uploaded file is missing one or more required columns.")
            st.markdown("### Expected Columns:")
            st.write(required_columns)

    except Exception as e:
        st.error(f"⚠️ An error occurred while reading the file: {e}")
else:
    st.info("Please upload a `.csv` file containing your ESG data.")

