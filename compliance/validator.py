import json
import pandas as pd
from jsonschema import validate, ValidationError

def load_schema(schema_path: str) -> dict:
    with open(schema_path, "r") as f:
        return json.load(f)

def validate_csv_row(row: dict, schema: dict) -> list:
    """Validate a single row against the JSON schema."""
    errors = []
    try:
        validate(instance=row, schema=schema)
    except ValidationError as e:
        errors.append(str(e.message))
    return errors

def validate_csv_against_schema(csv_file: pd.DataFrame, schema: dict) -> list:
    """Validate each row of the DataFrame and return list of results."""
    results = []
    for index, row in csv_file.iterrows():
        row_dict = row.to_dict()
        errors = validate_csv_row(row_dict, schema)
        results.append({"row": index + 1, "valid": not errors, "errors": errors})
    return results

