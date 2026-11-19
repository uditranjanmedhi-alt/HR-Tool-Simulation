"""Schema checks for uploaded or generated HR records."""

from __future__ import annotations

from math import isfinite
from typing import Any

from .schema import NUMERIC_COLUMNS, SCHEMA


def _records(data: Any) -> list[dict]:
    if hasattr(data, "to_dict"):
        return data.to_dict(orient="records")
    if isinstance(data, list) and all(isinstance(row, dict) for row in data):
        return data
    raise TypeError("Validation expects a list of record dictionaries or a tabular object with to_dict().")


def validate_dataframe(data: Any, entity: str) -> dict:
    """Validate schema columns, missing cells, duplicate IDs and numeric values."""
    if entity not in SCHEMA:
        raise ValueError(f"Unknown HR dataset schema: {entity}")
    records = _records(data)
    columns = list(records[0]) if records else []
    required = SCHEMA[entity]
    missing_columns = [column for column in required if column not in columns]
    missing_cells = sum(
        value is None or (isinstance(value, str) and not value.strip())
        for row in records for key, value in row.items() if key in required
    )
    id_column = next(
        (column for column in required if column.lower().endswith("id") and column in columns),
        None,
    )
    duplicate_ids = 0
    if id_column:
        ids = [row.get(id_column) for row in records if row.get(id_column) not in (None, "")]
        duplicate_ids = len(ids) - len(set(map(str, ids)))

    invalid_numeric: dict[str, int] = {}
    for column in NUMERIC_COLUMNS.get(entity, set()).intersection(columns):
        invalid = 0
        for row in records:
            value = row.get(column)
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            try:
                number = float(value)
            except (TypeError, ValueError):
                invalid += 1
                continue
            if not isfinite(number):
                invalid += 1
        if invalid:
            invalid_numeric[column] = invalid
    valid = not missing_columns and missing_cells == 0 and duplicate_ids == 0 and not invalid_numeric
    issues = []
    if missing_columns:
        issues.append(f"Missing columns: {', '.join(missing_columns)}")
    if missing_cells:
        issues.append(f"Missing cells: {missing_cells}")
    if duplicate_ids:
        issues.append(f"Duplicate IDs ({id_column}): {duplicate_ids}")
    if invalid_numeric:
        issues.append("Invalid numeric values: " + ", ".join(
            f"{column} ({count})" for column, count in invalid_numeric.items()
        ))
    return {
        "valid": valid,
        "summary": "; ".join(issues) if issues else "Data looks valid.",
        "missing_columns": missing_columns,
        "missing_values": missing_cells,
        "duplicate_ids": duplicate_ids,
        "invalid_numeric_values": invalid_numeric,
        "record_count": len(records),
    }
