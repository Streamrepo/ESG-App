import streamlit as st
import pandas as pd
import os
st.write("Files in current directory:", os.listdir())

# --- Normalization Functions ---
def scale(value, high, low):
    return max(0, min(100, 100 * (high - value) / (high - low)))

def normalize_ghg_emissions(value): return scale(value, high=10_000_000, low=100_000)
def normalize_renewable_energy(value): return scale(value, low=10, high=100)
def normalize_water_usage(value): return scale(value, high=1_000_000, low=100_000)
def normalize_waste_recycled(value): return scale(value, low=10, high=80)
def normalize_biodiversity(value): return scale(value, high=10, low=1)
def normalize_gender_pay_gap(value): return scale(value, high=20, low=3)
def normalize_board_diversity(value): return scale(value, low=10, high=40)

def normalize_taxonomy_alignment(value):
    if value >= 30: return 100
    elif value >= 15: return 50
    elif value < 5: return 0
    return 25

def normalize_exec_remuneration(value):
    return 100 if str(value).lower() == "yes" else 0

def normalize_transition_plan(value):
    scores = {
        "SBTi 2030": 100, "Net Zero 2030": 100,
        "SBTi 2040": 80, "Net Zero 2040": 80,
        "SBTi 2050": 60, "Net Zero 2050": 60,
        "Carbon Neutral": 40, "None": 0
    }
    return scores.get(str(value), 0)

# --- Streamlit Setup ---
st.set_page_config(page_title="ESG Analyser", layout="centered")
st.title("\U0001F33F ESG Analyser - Upload Your Company Data")

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

            # --- ESG Scoring ---
            st.header("3. ESG Scoring (CSRD/SFDR-Aligned)")

            e_score = (
                0.4 * normalize_ghg_emissions(company["GHG Emissions (tCO₂e)"]) +
                0.2 * normalize_renewable_energy(company["Renewable Energy %"]) +
                0.2 * normalize_water_usage(company["Water Usage (m³)"]) +
                0.2 * normalize_waste_recycled(company["Waste Recycled %"])
            )

            s_score = (
                0.3 * normalize_biodiversity(company["Biodiversity Risk %"]) +
                0.3 * normalize_gender_pay_gap(company["Gender Pay Gap %"]) +
                0.4 * normalize_board_diversity(company["Board Diversity %"])
            )

            g_score = (
                0.5 * normalize_exec_remuneration(company["ESG KPIs in Exec Pay"]) +
                0.5 * normalize_transition_plan(company["Transition Plan"])
            )

            esg_score = (0.5 * e_score) + (0.3 * s_score) + (0.2 * g_score)

            st.write(f"\U0001F331 Environmental Score: {e_score:.1f}/100")
            st.write(f"\U0001F91D Social Score: {s_score:.1f}/100")
            st.write(f"\U0001F3DB️ Governance Score: {g_score:.1f}/100")
            st.subheader(f"\U0001F3AF **Total ESG Score: {esg_score:.2f}/100**")

            # --- CSRD/ESRS Compliance ---
            st.header("4. CSRD/ESRS Compliance Mapping")

            try:
                esrs_ref = pd.read_csv("esrs_reference.csv", encoding="utf-8")
            except:
                st.error("⚠️ Could not load ESRS reference data.")
                esrs_ref = None

            if esrs_ref is not None:
                compliance_results = []

                for _, row in esrs_ref.iterrows():
                    metric = row["Metric Name"]
                    esrs_code = row["ESRS Standard"]
                    benchmark = row["Benchmark"]
                    disclosure_type = row["Type"]

                    if metric in company:
                        value = company[metric]
                        status = "✅ Compliant"
                        recommendation = "Maintain performance or document disclosure."

                        try:
                            if benchmark == "Yes":
                                if str(value).strip().lower() != "yes":
                                    status = "❌ Not Compliant"
                                    recommendation = "Disclose plan to integrate ESG KPIs."
                            elif "–" in benchmark:
                                if "2050" in str(value):
                                    status = "✅ Compliant"
                                elif "2040" in str(value):
                                    status = "⚠️ Acceptable"
                                else:
                                    status = "❌ Not Compliant"
                                    recommendation = "Adopt a validated transition plan by 2050."
                            elif "<" in benchmark:
                                limit = float(benchmark.replace("<", "").replace(",", ""))
                                if float(value) >= limit:
                                    status = "❌ Not Compliant"
                                    recommendation = f"Value exceeds threshold of {benchmark}."
                            elif ">" in benchmark:
                                limit = float(benchmark.replace(">", "").replace(",", ""))
                                if float(value) <= limit:
                                    status = "❌ Not Compliant"
                                    recommendation = f"Target is to exceed {limit}%."
                        except:
                            status = "⚠️ Check Format"
                            recommendation = "Unable to evaluate due to formatting."

                        compliance_results.append([
                            metric, value, benchmark, esrs_code, disclosure_type, status, recommendation
                        ])

                compliance_df = pd.DataFrame(compliance_results, columns=[
                    "Metric", "Company Value", "ESRS Benchmark", "ESRS Ref",
                    "Disclosure Type", "Compliance Status", "Recommendation"
                ])

                st.dataframe(compliance_df)

        else:
            st.error("❌ The uploaded file is missing one or more required columns.")
            st.markdown("### Expected Columns:")
            st.write(required_columns)

    except Exception as e:
        st.error(f"⚠️ An error occurred while reading the file: {e}")
else:
    st.info("Please upload a `.csv` file containing your ESG data.")
