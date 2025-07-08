import pandas as pd

def generate_csrd_summary(df):
    compliance_map = {
        "ESRS 2-GOV-1": {"label": "dedicated governance body", "expected": ["Yes"]},
        "ESRS 2-GOV-2": {"label": "governance meeting frequency", "expected": ["Monthly", "Quarterly", "Annually"]},
        "ESRS 2-SBM-3": {"label": "double materiality assessment", "expected": ["Yes"]},
        "ESRS 2-SBM-3a": {"label": "materiality update frequency", "expected": ["Annually", "Biennially"]},
        "ESRS E1-6": {"label": "Scope 1 emissions disclosure", "expected": "numeric"},
        "ESRS E1-4": {"label": "climate target-setting", "expected": ["Yes"]},
        "ESRS E2-3": {"label": "pollutant monitoring", "expected": ["Yes"]},
        "ESRS S1-6": {"label": "gender diversity disclosure", "expected": "numeric_0_100"},
        "ESRS G1-1": {"label": "anti-corruption policy", "expected": ["Yes"]},
        "ESRS 2-IRO-1": {"label": "risk & opportunity disclosure", "expected": ["Yes"]},
    }

    compliant_labels = []
    non_compliant_items = []

    for _, row in df.iterrows():
        disclosure_id = str(row.get("Disclosure ID", "")).strip()
        response = str(row.get("Response Type", "")).strip()

        if disclosure_id not in compliance_map:
            continue

        rule = compliance_map[disclosure_id]
        expected = rule["expected"]
        label = rule["label"]

        if isinstance(expected, list):
            if response in expected:
                compliant_labels.append(label)
            else:
                non_compliant_items.append({
                    "disclosure_id": disclosure_id,
                    "summary_label": label,
                    "reported": response,
                    "expected": expected
                })
        elif expected == "numeric":
            try:
                float_val = float(response)
                if float_val >= 0:
                    compliant_labels.append(label)
                else:
                    raise ValueError
            except:
                non_compliant_items.append({
                    "disclosure_id": disclosure_id,
                    "summary_label": label,
                    "reported": response,
                    "expected": "numeric ≥ 0"
                })
        elif expected == "numeric_0_100":
            try:
                val = float(response)
                if 0 <= val <= 100:
                    compliant_labels.append(label)
                else:
                    raise ValueError
            except:
                non_compliant_items.append({
                    "disclosure_id": disclosure_id,
                    "summary_label": label,
                    "reported": response,
                    "expected": "numeric 0–100"
                })

    total_checks = len(compliance_map)
    compliant_count = len(compliant_labels)
    non_compliant_count = len(non_compliant_items)
    compliance_level = (
        "strong" if compliant_count >= 9 else
        "moderate" if compliant_count >= 6 else
        "poor"
    )
    overall_status = (
        "largely compliant" if compliant_count >= 9 else
        "partially compliant" if compliant_count >= 6 else
        "non-compliant"
    )

    compliant_sections = sorted(set(df[df["Disclosure ID"].isin(compliance_map.keys())]["Section"]))
    compliant_highlights = ", ".join(compliant_labels)

    non_compliant_areas = ", ".join([f"**{item['summary_label']}**" for item in non_compliant_items])
    reported_vals = [item["reported"] for item in non_compliant_items]
    formatted_reported = set([r if r.lower() != "nan" else "missing data" for r in reported_vals])
    expected_vals = [
        ", ".join(e) if isinstance(e, list) else e for e in [item["expected"] for item in non_compliant_items]
    ]
    formatted_expected = set(expected_vals)

    reported_str = ", ".join(sorted(formatted_reported))
    expected_str = ", ".join(sorted(formatted_expected))

    recommendations = "review and update missing disclosures, and align with expected ESRS reporting standards."

    paragraph = f"""
    Compliance Summary: The company demonstrates {compliance_level} alignment with CSRD and ESRS requirements, achieving {compliant_count} out of {total_checks} compliant disclosures across the core areas of {', '.join(compliant_sections)}.
    Key strengths include {compliant_highlights}, all of which meet disclosure expectations under ESRS.
    However, the company is non-compliant in {non_compliant_count} disclosure(s), notably in {non_compliant_areas}. 
    Reported values include: {reported_str}, where the expected values were {expected_str}.
    To close these compliance gaps, the company should {recommendations}
    Overall, the company is {overall_status} in terms of readiness for CSRD-aligned sustainability reporting.
    """

    return paragraph.strip()

# Example usage (in Streamlit or script):
# df = pd.read_csv("your_data.csv")
# summary = generate_csrd_summary(df)
# st.text_area("Compliance Summary", summary, height=300)
