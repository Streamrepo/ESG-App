import pandas as pd

def check_compliance(df):
    # Define logic
    compliance_rules = {
        "ESRS 2-GOV-1": {"type": "Yes/No", "valid": ["Yes"], "note": "Must explicitly confirm a governing body with sustainability oversight."},
        "ESRS 2-GOV-2": {"type": "Drop-down", "valid": ["Monthly", "Quarterly", "Annually"], "note": "Any frequency above “None” is acceptable."},
        "ESRS 2-SBM-3": {"type": "Yes/No", "valid": ["Yes"], "note": "Required under ESRS 2 to identify IROs."},
        "ESRS 2-SBM-3a": {"type": "Drop-down", "valid": ["Annually", "Biennially"], "note": "“Not yet conducted” is non-compliant unless company is in transition period."},
        "ESRS E1-6": {"type": "Numeric", "valid": "numeric_non_blank", "note": "Can be 0 only if explained as immaterial and justified elsewhere."},
        "ESRS E1-4": {"type": "Yes/No", "valid": ["Yes"], "note": "Required if climate is material; must be time-bound and specific."},
        "ESRS E2-3": {"type": "Yes/No", "valid": ["Yes"], "note": "Required if pollution is material; “No” is non-compliant unless well-justified."},
        "ESRS S1-6": {"type": "Numeric", "valid": "numeric_0_100", "note": "Even low numbers are compliant if disclosed; must be numeric."},
        "ESRS G1-1": {"type": "Yes/No", "valid": ["Yes"], "note": "Mandatory under ESRS G1; “No” is always non-compliant."},
        "ESRS 2-IRO-1": {"type": "Yes/No", "valid": ["Yes"], "note": "Required to identify sustainability risks, impacts, and opportunities."},
    }

    compliance_results = []
    for _, row in df.iterrows():
        disclosure_id = str(row.get("Disclosure ID", "")).strip()
        response = str(row.get("Response Type", "")).strip()
        note = ""
        compliant = ""

        if disclosure_id in compliance_rules:
            rule = compliance_rules[disclosure_id]
            expected = rule["valid"]
            note = rule["note"]

            if rule["type"] == "Yes/No":
                compliant = "✔️" if response in expected else "❌"
            elif rule["type"] == "Drop-down":
                compliant = "✔️" if response in expected else "❌"
            elif rule["type"] == "Numeric":
                try:
                    val = float(response)
                    if expected == "numeric_non_blank":
                        compliant = "✔️" if response != "" and val >= 0 else "❌"
                    elif expected == "numeric_0_100":
                        compliant = "✔️" if 0 <= val <= 100 else "❌"
                except:
                    compliant = "❌"
        else:
            compliant = "N/A"

        compliance_results.append((compliant, note))

    df["Compliance"] = [res[0] for res in compliance_results]
    df["Notes"] = [res[1] for res in compliance_results]
    return df

