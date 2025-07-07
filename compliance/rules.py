def get_compliance_rules():
    return [
        {
            "field": "GHG_Emissions_Scope_3",
            "condition": lambda row: row.get("Product_Type") in ["Article 8", "Article 9"],
            "check": lambda val: val not in [None, "", 0],
            "message": "Scope 3 must be disclosed for Article 8/9 products.",
            "reg": "ESRS E1 §47"
        },
        {
            "field": "Principal_Adverse_Impacts_Disclosed",
            "condition": lambda row: row.get("Product_Type") in ["Article 8", "Article 9"],
            "check": lambda val: val == "Yes",
            "message": "PAI must be disclosed for Article 8/9 products.",
            "reg": "SFDR Art. 4"
        },
        {
            "field": "Board_Climate_Oversight",
            "condition": lambda row: True,
            "check": lambda val: val == "Yes",
            "message": "Board oversight of climate issues is required.",
            "reg": "IFRS S2 – Governance"
        },
        {
            "field": "Green_Taxonomy_Alignment (%)",
            "condition": lambda row: True,
            "check": lambda val: isinstance(val, str) and val.endswith('%'),
            "message": "Green alignment must be reported as a percentage.",
            "reg": "EU Taxonomy Art. 8"
        }
    ]

