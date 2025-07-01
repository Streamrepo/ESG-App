import streamlit as st
import pandas as pd

st.set_page_config(page_title="ESG Analyzer", layout="centered")
st.title("EY-ESG Analyzer - Upload Your ESG Data")

def classify_company_size(Revenue, employees):
    if Revenue >= 1_000_000_000 or employees >= 2500:
        return "L"
    elif 250_000_000 <= Revenue < 1_000_000_000 or 500 <= employees < 2500:
        return "UM"
    elif 50_000_000 <= Revenue < 250_000_000 or 100 <= employees < 500:
        return "LM"
    else:
        return "S"

st.header("1. Upload Company's ESG CSV File")
uploaded_file = st.file_uploader("Upload your ESG data (.csv)", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "Company", "Industry", "Number of employees", "GHG Emissions (tCO₂e)",
            "Renewable Energy %", "Water usage (m³)", "Waste Recycled %",
            "Biodiversity Risk %", "Gender Pay Gap %", "Board Diversity %",
            "ESG KPI's in Exec Pay", "Transition Plan", "Revenue"
        ]

        if all(col in df.columns for col in required_columns):
            # Classify size based on revenue and employees
            df["Size"] = df.apply(lambda row: classify_company_size(row["Revenue"], row["Number of employees"]), axis=1)

            st.success("✅ File uploaded and company size classified!")
            st.dataframe(df)
            def load_benchmark(metric_name, industry, size):
    file_name = metric_name.lower().replace(" ", "_").replace("%", "").replace("’", "").replace("'", "")
    path = f"data/benchmarks/{industry.lower().replace(' ', '_')}/{size}/{file_name}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        st.warning(f"⚠️ Benchmark for '{metric_name}' not found at: {path}")
        return None


        else:
            st.error("❌ The uploaded file is missing one or more required columns.")
            st.write("Expected columns:", required_columns)

    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")
else:
    st.info("Please upload a `.csv` file to begin.")


