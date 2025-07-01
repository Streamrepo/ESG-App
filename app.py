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
            import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# --- Function to load benchmark file based on industry & size ---
def load_benchmark(metric_name, industry, size):
    file_name = metric_name.lower().replace(" ", "_").replace("%", "").replace("’", "").replace("'", "")
    path = f"data/benchmarks/{industry.lower().replace(' ', '_')}/{size}/{file_name}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        st.warning(f"⚠️ Benchmark for '{metric_name}' not found at: {path}")
        return None

# --- Extract company info ---
company = df.iloc[0]
industry = company["Industry"]
size = company["Size"]
num_employees = company["Number of employees"]

# --- Analyze and Plot for GHG & Water ---
for metric in ["GHG Emissions", "Water usage"]:
    st.subheader(f"📊 {metric} vs Number of Employees")

    # Load benchmark dataset
    benchmark_df = load_benchmark(metric, industry, size)
    if benchmark_df is None or "Number of employees" not in benchmark_df.columns:
        continue

    # Fit linear regression
    X = benchmark_df["Number of employees"].values.reshape(-1, 1)
    y = benchmark_df[metric].values
    model = stats.linregress(benchmark_df["Number of employees"], y)

    # Predicted value
    predicted = model.slope * num_employees + model.intercept
    residual = company[metric + " (tCO₂e)"] - predicted if "GHG" in metric else company[metric] - predicted
    residual_std = np.std(y - (model.slope * benchmark_df["Number of employees"] + model.intercept))
    standardized_residual = residual / residual_std
    percentile = stats.norm.cdf(standardized_residual) * 100

    # Plot
    fig, ax = plt.subplots()
    ax.scatter(benchmark_df["Number of employees"], benchmark_df[metric], label="Benchmark data", alpha=0.6)
    ax.plot(benchmark_df["Number of employees"], model.slope * benchmark_df["Number of employees"] + model.intercept, color="orange", label="Regression line")
    ax.scatter([num_employees], [company[metric + " (tCO₂e)"] if "GHG" in metric else company[metric]], color="red", s=80, label="Your Company", zorder=5)

    ax.set_xlabel("Number of employees")
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} vs Employees with Linear Fit")
    ax.legend()
    st.pyplot(fig)

    # Output
    st.markdown(f"**Residual:** {residual:.2f}")
    st.markdown(f"**Standardized Residual:** {standardized_residual:.2f}")
    st.markdown(f"**Percentile vs Peer Group:** {percentile:.1f}%")

            
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


