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

        if all(col in df.columns for col in required_columns):
            st.success("✅ File uploaded and validated successfully!")
            st.dataframe(df)

            # --- Benchmark Comparison ---
            st.header("2. Benchmark Comparison")

            benchmarks = pd.read_csv("benchmarks.csv")
            company = df.iloc[0]
            industry = company["Industry"]
            size = company["Size"]

            match = benchmarks[
                (benchmarks["Industry"] == industry) & (benchmarks["Size"] == size)
            ]

            if not match.empty:
                benchmark = match.iloc[0]
                st.success(f"✅ Found benchmark for {industry} ({size})")
                st.write("**Comparison Results:**")

                compare_columns = [
                    "GHG Emissions (tCO₂e)", "Renewable Energy %", "Water Usage (m³)",
                    "Waste Recycled %", "Biodiversity Risk %", "Gender Pay Gap %",
                    "Board Diversity %"
                ]

                for col in compare_columns:
                    user_val = company[col]
                    benchmark_val = benchmark[col]
                    diff = user_val - benchmark_val
                    direction = "above" if diff > 0 else "below" if diff < 0 else "equal to"
                    st.write(f"**{col}**: {user_val} (You) vs {benchmark_val} (Benchmark) → {abs(diff):.2f} {direction}")

            else:
                st.error("❌ No benchmark found for this industry and size.")

        else:
            st.error("❌ The uploaded file is missing one or more required columns.")
            st.markdown("### Expected Columns:")
            st.write(required_columns)

    except Exception as e:
        st.error(f"⚠️ An error occurred while reading the file: {e}")

else:
    st.info("Please upload a `.csv` file containing your ESG data.")
