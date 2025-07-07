from compliance.rules import get_compliance_rules

def check_compliance(row: dict):
    results = []
    rules = get_compliance_rules()

    for rule in rules:
        field = rule["field"]
        if rule["condition"](row):
            value = row.get(field)
            passed = rule["check"](value)
            results.append({
                "field": field,
                "value": value,
                "status": "✅" if passed else "❌",
                "message": None if passed else rule["message"],
                "reg": rule["reg"] if not passed else None
            })
    return results
