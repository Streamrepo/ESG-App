import streamlit as st
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import beta
from scipy.optimize import curve_fit
from PIL import Image

# ✅ Streamlit config
st.set_page_config(page_title="GREEYN Investment Tracker", layout="wide")

# --- Load logo ---
ey_logo = Image.open("assets/ey_logo.png")
col1, col2 = st.columns([3, 1])
with col1:
    st.title("GREEYN Investment Tracker")
with col2:
    st.image(ey_logo, width=250)

# --- Helpers ---
def classify_company_size(revenue, employees):
    if revenue >= 1_000_000_000 or employees >= 2500:
        return "L"
    elif 250_000_000 <= revenue < 1_000_000_000 or 500 <= employees < 2500:
        return "UM"
    elif 50_000_000 <= revenue < 250_000_000 or 100 <= employees < 500:
        return "LM"
    else:
        return "S"

def load_benchmark(metric, industry, size):
    file = metric.lower().replace(" ", "_").replace("%", "").replace("’", "").replace("'", "")
    path = f"data/benchmarks/{industry.lower().replace(' ', '_')}/{size}/{file}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    st.warning(f"⚠️ Benchmark for '{metric}' not found at: {path}")
    return None

# --- Upload Section ---
st.header("Upload Portfolio ESG & Compliance Data")
uploaded_file = st.file_uploader("Upload your ESG data", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "Company", "Industry", "Number of employees", "GHG Emissions (tCO₂e)",
            "Renewable Energy %", "Water usage (m³)", "Waste Recycled %",
            "Biodiversity Risk %", "Gender Pay Gap %", "Board Diversity %",
            "ESG KPI's in Exec Pay", "Transition Plan", "Revenue", "Expected Return (%)"
        ]

        if not all(col in df.columns for col in required_columns):
            st.error("❌ Missing required columns.")
            st.write("Expected columns:", required_columns)
        else:
            df["Size"] = df.apply(lambda r: classify_company_size(r["Revenue"], r["Number of employees"]), axis=1)
            st.success("✅ File uploaded and company size classified!")
            st.dataframe(df)

            selected_company = st.selectbox("Select a company to analyze:", df["Company"].unique())
            company = df[df["Company"] == selected_company].iloc[0]
            industry = company["Industry"]
            size = company["Size"]
            num_employees = company["Number of employees"]

            # --- Section 1: SLR Scatterplots ---
            for metric in ["GHG Emissions (tCO₂e)", "Water usage (m³)"]:
                st.subheader(f"📊 {metric} vs Number of Employees")
                short = "GHG Emissions" if "GHG" in metric else "Water usage"
                benchmark = load_benchmark(short, industry, size)
                if benchmark is None or "Number of employees" not in benchmark.columns:
                    continue

                X = benchmark["Number of employees"].values
                y = benchmark[metric].values
                slope, intercept, *_ = stats.linregress(X, y)
                predicted = slope * num_employees + intercept
                actual = company[metric]
                residual = actual - predicted
                std_res = residual / np.std(y - (slope * X + intercept))
                percentile = stats.norm.cdf(std_res) * 100
                company[f"{metric} Percentile"] = percentile

                fig, ax = plt.subplots()
                fig.patch.set_facecolor('#999999')
                ax.set_facecolor('#cccccc')
                ax.scatter(X, y, label="Benchmark data", alpha=0.6)
                ax.plot(X, slope * X + intercept, color="#ffe600", label="Regression line")
                ax.scatter([num_employees], [actual], color="red", s=80, label="Your Company")
                ax.set_xlabel("Number of employees")
                ax.set_ylabel(metric)
                ax.legend()
                st.pyplot(fig)

            # --- Section 2: Beta Distributions ---
            st.header("2. Beta Distribution Percentile Analysis")
            for metric in ["Renewable Energy %", "Waste Recycled %", "Biodiversity Risk %", "Gender Pay Gap %", "Board Diversity %"]:
                st.subheader(f"📈 {metric} Distribution")
                bench = load_benchmark(metric, industry, size)
                if bench is None or metric not in bench.columns:
                    continue
                try:
                    vals = bench[metric].dropna() / 100
                    mean, var = vals.mean(), vals.var()
                    alpha = ((1 - mean) / var - 1 / mean) * mean ** 2
                    beta_param = alpha * (1 / mean - 1)
                    sample_val = company[metric] / 100
                    percentile = beta.cdf(sample_val, alpha, beta_param) * 100
                    company[f"{metric} Percentile"] = percentile

                    x = np.linspace(0, 1, 500)
                    y = beta.pdf(x, alpha, beta_param)
                    fig, ax = plt.subplots()
                    fig.patch.set_facecolor('#999999')
                    ax.set_facecolor('#cccccc')
                    ax.plot(x * 100, y)
                    ax.axvline(sample_val * 100, color="#ffe600", linestyle="--", label=f"Your Value")
                    ax.set_title(metric)
                    ax.set_xlabel("%")
                    ax.set_ylabel("Density")
                    ax.legend()
                    st.pyplot(fig)
                except:
                    st.warning(f"Error processing {metric}.")

            # --- Section 3: Disclosure Benchmarks ---
            st.header("3. Disclosure Benchmarks")
            qualitative = ["ESG KPI's in Exec Pay", "Transition Plan"]
            score_map = {
                "SBTi 2030": 100, "Net Zero 2030": 100, "SBTi 2040": 80,
                "Net Zero 2040": 80, "SBTi 2050": 60, "Net Zero 2050": 60,
                "Carbon Neutral": 40
            }
            for metric in qualitative:
                st.subheader(f"📋 {metric} Disclosure")
                bench = load_benchmark(metric, industry, size)
                if bench is None or metric not in bench.columns:
                    continue
                values = bench[metric].dropna().astype(str).str.strip()
                val = str(company[metric]).strip()

                if metric == "Transition Plan":
                    company["Transition Plan Score"] = score_map.get(val, 0)
                else:
                    pass  # handled later in G-score

            # --- Section 4: ESG Peer Score ---
            st.header("4. ESG Peer Score")
            E_metrics = {
                "GHG Emissions (tCO₂e)": True,
                "Water usage (m³)": True,
                "Renewable Energy %": False,
                "Waste Recycled %": False,
                "Biodiversity Risk %": True,
                "Transition Plan Score": None
            }
            S_metrics = {
                "Gender Pay Gap %": True,
                "Board Diversity %": False
            }
            E_raw = sum(100 - company.get(f"{m} Percentile", 0) if inv else company.get(f"{m} Percentile", 0)
                        for m, inv in E_metrics.items() if m != "Transition Plan Score")
            E_raw += company.get("Transition Plan Score", 0)
            E_score = E_raw * (60 / (len(E_metrics) * 100))

            S_raw = sum(100 - company.get(f"{m} Percentile", 0) if inv else company.get(f"{m} Percentile", 0)
                        for m, inv in S_metrics.items())
            S_score = S_raw * (30 / (len(S_metrics) * 100))

            G_score = 10 if str(company.get("ESG KPI's in Exec Pay", "")).lower() == "yes" else 0
            total_score = E_score + S_score + G_score

            st.markdown(f"**Environmental Score:** {E_score:.2f} / 60")
            st.markdown(f"**Social Score:** {S_score:.2f} / 30")
            st.markdown(f"**Governance Score:** {G_score:.2f} / 10")
            st.markdown(f"**🔵 Total ESG Peer Score:** {total_score:.2f} / 100")

            # --- Section 5: ESG vs Expected Return ---
            st.header("5. ESG Score vs Expected Return")
            esg_return_path = f"data/benchmarks/{industry.lower().replace(' ', '_')}/{size}/esg_return_benchmark.csv"
            if os.path.exists(esg_return_path):
                try:
                    bench = pd.read_csv(esg_return_path)
                    def logistic(x, a, b, c): return a / (1 + np.exp(-b * (x - c)))
                    X = bench["Expected Return (%)"].values
                    y = bench["ESG Score"].values
                    popt, _ = curve_fit(logistic, X, y, bounds=(0, [120, 2, 20]))
                    x_fit = np.linspace(min(X), max(X), 200)
                    y_fit = logistic(x_fit, *popt)

                    fig, ax = plt.subplots()
                    fig.patch.set_facecolor('#999999')
                    ax.set_facecolor('#cccccc')
                    ax.scatter(X, y, label="Benchmark", alpha=0.6)
                    ax.plot(x_fit, y_fit, color="#ffe600", label="Logistic Fit")
                    ax.scatter([company["Expected Return (%)"]], [total_score], color="red", s=80, label="Your Company")
                    ax.set_xlabel("Expected Return (%)")
                    ax.set_ylabel("ESG Score")
                    ax.set_title("ESG Score vs Expected Return")
                    ax.legend()
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error in ESG vs Return plot: {e}")
            else:
                st.warning(f"Benchmark file not found: {esg_return_path}")

    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")
