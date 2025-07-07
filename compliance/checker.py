import pandas as pd

REQUIRED_COLUMNS = [
    "Metric_Name", "Metric_Value", "Unit", "Date", "ESRS_Reference"
]

NUMERIC_METRICS = {
    "GHG_Scope1_Emissions",
    "GHG_Scope2_Emissions",
    "GHG_Scope3_Emissions",
    "Energy_Consumption_Total",
    "Water_Consumption",
    "Employees_Total",
    "Gender_Diversity_Management",
    "Board_Diversity_Female",
    "Anti_Corruption_Training",
    "Incidents_Discrimination"
}

def check_csv_compliance(df: pd.DataFrame):
    compliant = []
    non_compliant = []

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    for _, row in df.iterrows():
        metric = row["Metric_Name"]
        value = row["Metric_Value"]
        unit = row["Unit"]
        date = row["Date"]
        esrs = row["ESRS_Reference"]
        notes = row.get("Notes", "")

        status = "✅"
        reason = ""

        if pd.isna(value) or value == "":
            status = "❌"
            reason = "Missing value"
        elif metric in NUMERIC_METRICS:
            try:
                float(value)
            except ValueError:
                status = "❌"
                reason = "Value must be numeric"

        record = {
            "Metric Name": metric,
            "Value": value,
            "Unit": unit,
            "Date": date,
            "ESRS Ref": esrs,
            "Status": status,
            "Reason": reason if status == "❌" else ""
        }

        if status == "✅":
            compliant.append(record)
        else:
            non_compliant.append(record)

    return pd.DataFrame(compliant), pd.DataFrame(non_compliant)

