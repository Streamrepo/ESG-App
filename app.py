import streamlit as st
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import beta

st.set_page_config(page_title="ESG Analyzer", layout="centered")
st.title("EY-ESG Analyzer - Upload Your ESG Data")

# --- Company Size Classification ---
def classify_company_size(Revenue, employees):
    if Revenue >= 1_000_000_000 or employees >= 2500:
        return "L"
    elif 250_000_000 <= Revenue < 1_000_000_000 or 500 <= employees < 2500:
        return "UM"
    elif 50_000_000 <= Revenue < 250_000_000 or 100 <= employees < 500:
        return "LM"
    else:
        return "S"

# --- Load benchmark based on industry/size/metric ---
def load_benchmark(metric_name, industry, size):
    file_name = metric_name.lower().replace(" ", "_").replace("%", "").replace("’", "").replace("'", "")
    path = f"data/benchmarks/{industry.lower().replace(' ', '_')}/{size}/{file_name}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        st.warning(f"\u26a0\ufe0f Benchmark for '{metric_name}' not found at: {path}")
        return None

# --- Upload Section ---
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
            df["Size"] = df.apply(lambda row: classify_company_size(row["Revenue"], row["Number of employees"]), axis=1)
            st.success("\u2705 File uploaded and company size classified!")
            st.dataframe(df)

            company = df.iloc[0]
            industry = company["Industry"]
            size = company["Size"]
            num_employees = company["Number of employees"]

            # --- Section 1: SLR Scatterplot ---
            for metric in ["GHG Emissions (tCO₂e)", "Water usage (m³)"]:
                st.subheader(f"📊 {metric} vs Number of Employees")
                short_metric = "GHG Emissions" if "GHG" in metric else "Water usage"
                benchmark_df = load_benchmark(short_metric, industry, size)

                if benchmark_df is None or "Number of employees" not in benchmark_df.columns:
                    continue

                X = benchmark_df["Number of employees"].values
                y = benchmark_df[metric].values
                slope, intercept, *_ = stats.linregress(X, y)
                predicted = slope * num_employees + intercept
                actual = company[metric]
                residual = actual - predicted
                residual_std = np.std(y - (slope * X + intercept))
                standardized_residual = residual / residual_std
                percentile = stats.norm.cdf(standardized_residual) * 100

                fig, ax = plt.subplots()
                ax.scatter(X, y, label="Benchmark data", alpha=0.6)
                ax.plot(X, slope * X + intercept, color="orange", label="Regression line")
                ax.scatter([num_employees], [actual], color="red", s=80, label="Your Company", zorder=5)
                ax.set_xlabel("Number of employees")
                ax.set_ylabel(metric)
                ax.set_title(f"{metric} vs Employees")
                ax.legend()
                st.pyplot(fig)

                st.markdown(f"**Residual:** {residual:.2f}")
                st.markdown(f"**Standardized Residual:** {standardized_residual:.2f}")
                st.markdown(f"**Percentile vs Peer Group:** {percentile:.1f}%")

        else:
            st.error("\u274c Missing required columns.")
            st.write("Expected columns:", required_columns)

    except Exception as e:
        st.error(f"\u26a0\ufe0f Error reading file: {e}")

    # --- Section 2: Beta Distribution ---
    st.header("2. Beta Distribution Percentile Analysis")

    beta_metrics = [
        "Renewable Energy %", "Waste Recycled %", "Biodiversity Risk %",
        "Gender Pay Gap %", "Board Diversity %"
    ]

    for metric in beta_metrics:
        st.subheader(f"📈 {metric} Benchmark Distribution")
        benchmark_df = load_benchmark(metric, industry, size)
        if benchmark_df is None or metric not in benchmark_df.columns:
            continue

        try:
            values = benchmark_df[metric].dropna() / 100
            mean = values.mean()
            var = values.var()

            alpha = ((1 - mean) / var - 1 / mean) * mean ** 2
            beta_param = alpha * (1 / mean - 1)

            x = np.linspace(0, 1, 500)
            y = beta.pdf(x, alpha, beta_param)

            sample_val = company[metric] / 100
            percentile = beta.cdf(sample_val, alpha, beta_param) * 100

            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(x * 100, y, label="Benchmark Distribution")
            ax.axvline(sample_val * 100, color="red", linestyle="--", label=f"Your Value: {company[metric]}%")
            ax.set_title(f"{metric} Beta Distribution")
            ax.set_xlabel("%")
            ax.set_ylabel("Density")
            ax.legend()
            st.pyplot(fig)

            st.markdown(f"**Percentile vs Peer Group:** {percentile:.1f}%")

        except Exception as e:
            st.error(f"\u26a0\ufe0f Error processing {metric}: {e}")

    # --- Section 3: Disclosure Benchmarks ---
    st.header("3. Disclosure Benchmarks: ESG KPIs & Transition Plan")

    qualitative_metrics = ["ESG KPI's in Exec Pay", "Transition Plan"]

    for metric in qualitative_metrics:
        st.subheader(f"📋 {metric} Peer Disclosure")

        benchmark_df = load_benchmark(metric, industry, size)
        if benchmark_df is None or metric not in benchmark_df.columns:
            st.warning(f"\u26a0\ufe0f Benchmark not found or missing column: {metric}")
            continue

        benchmark_vals = benchmark_df[metric].dropna().astype(str).str.strip()
        company_val = str(company[metric]).strip()

        if metric == "ESG KPI's in Exec Pay":
            disclosure_rate = (benchmark_vals.str.lower() == "yes").mean() * 100
            company_compliant = company_val.lower() == "yes"
        else:
            preferred = ["SBTi 2030", "Net Zero 2030", "SBTi 2040", "Net Zero 2040"]
            disclosure_rate = benchmark_vals.isin(preferred).mean() * 100
            company_compliant = company_val in preferred

        st.markdown(f"**Your Value:** `{company_val}`")
        st.markdown(f"**Peer Disclosure Rate:** `{disclosure_rate:.1f}%`")

        if company_compliant:
            st.success("\u2705 Your company matches peer best practices.")
        else:
            st.error("\u274c Below peer benchmark. Consider improving disclosure.")

else:
    st.info("Please upload a `.csv` file to begin.")
