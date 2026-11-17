# hr_simulate/data/data_validator.py
"""Simple data validation utilities.
Checks that a DataFrame conforms to the expected schema, reports missing values, duplicates, and column type issues.
"""
import pandas as pd
from .schema import SCHEMA

def validate_dataframe(df: pd.DataFrame, entity: str) -> dict:
    """Validate a DataFrame against the schema for a given entity.

    Returns a dict with keys:
    - valid (bool)
    - summary (str) – short human‑readable report
    - missing_columns (list)
    - missing_values (int)
    - duplicate_ids (int)
    """
    required = SCHEMA.get(entity, [])
    missing_cols = [c for c in required if c not in df.columns]
    missing_vals = df.isnull().sum().sum()
    dup = 0
    id_col = None
    # Try to infer an ID column (first required column ending with 'id')
    for col in required:
        if col.lower().endswith("id") and col in df.columns:
            id_col = col            break
    if id_col:
        dup = df[id_col].duplicated().sum()
    valid = not missing_cols and missing_vals == 0 and dup == 0
    summary_parts = []
    if missing_cols:
        summary_parts.append(f"Missing columns: {', '.join(missing_cols)}")
    if missing_vals:
        summary_parts.append(f"Missing values: {missing_vals}")
    if dup:
        summary_parts.append(f"Duplicate IDs ({id_col}): {dup}")
    if not summary_parts:
        summary_parts.append("Data looks valid.")
    summary = "; ".join(summary_parts)
    return {
        "valid": valid,
        "summary": summary,
        "missing_columns": missing_cols,
        "missing_values": missing_vals,
        "duplicate_ids": dup,
    }
