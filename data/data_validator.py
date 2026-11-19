"""Schema checks for uploaded or generated HR records."""

from __future__ import annotations

from datetime import date
from math import isfinite
from typing import Any

from .schema import (
    DATE_COLUMNS, DATE_ORDERING, NULLABLE_COLUMNS, NUMERIC_COLUMNS, SCHEMA, VALUE_RANGES,
)


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
    nullable = NULLABLE_COLUMNS.get(entity, set())
    missing_columns = [column for column in required if column not in columns]
    missing_cells = sum(
        value is None or (isinstance(value, str) and not value.strip())
        for row in records for key, value in row.items()
        if key in required and key not in nullable
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
    out_of_range: dict[str, int] = {}
    for column in NUMERIC_COLUMNS.get(entity, set()).intersection(columns):
        invalid = 0
        out_of_bounds = 0
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
                continue
            lower, upper = VALUE_RANGES.get(entity, {}).get(column, (None, None))
            if ((lower is not None and number < lower)
                    or (upper is not None and number > upper)):
                out_of_bounds += 1
        if invalid:
            invalid_numeric[column] = invalid
        if out_of_bounds:
            out_of_range[column] = out_of_bounds

    invalid_dates: dict[str, int] = {}
    parsed_dates: list[dict[str, date | None]] = []
    for row in records:
        parsed_row: dict[str, date | None] = {}
        for column in DATE_COLUMNS.get(entity, set()).intersection(columns):
            value = row.get(column)
            if value is None or (isinstance(value, str) and not value.strip()):
                parsed_row[column] = None
                continue
            try:
                parsed_row[column] = date.fromisoformat(str(value)[:10])
            except (TypeError, ValueError):
                parsed_row[column] = None
                invalid_dates[column] = invalid_dates.get(column, 0) + 1
        parsed_dates.append(parsed_row)

    chronology_errors: dict[str, int] = {}
    for earlier, later in DATE_ORDERING.get(entity, ()):
        if earlier not in columns or later not in columns:
            continue
        chronology_errors[f"{later} before {earlier}"] = sum(
            dates[earlier] is not None and dates[later] is not None
            and dates[later] < dates[earlier]
            for dates in parsed_dates
        )
    chronology_errors = {
        issue: count for issue, count in chronology_errors.items() if count
    }

    valid = (
        not missing_columns and missing_cells == 0 and duplicate_ids == 0
        and not invalid_numeric and not out_of_range and not invalid_dates
        and not chronology_errors
    )
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
    if out_of_range:
        issues.append("Out-of-range numeric values: " + ", ".join(
            f"{column} ({count})" for column, count in out_of_range.items()
        ))
    if invalid_dates:
        issues.append("Invalid dates: " + ", ".join(
            f"{column} ({count})" for column, count in invalid_dates.items()
        ))
    if chronology_errors:
        issues.append("Date ordering errors: " + ", ".join(
            f"{issue} ({count})" for issue, count in chronology_errors.items()
        ))
    return {
        "valid": valid,
        "summary": "; ".join(issues) if issues else "Data looks valid.",
        "missing_columns": missing_columns,
        "missing_values": missing_cells,
        "duplicate_ids": duplicate_ids,
        "invalid_numeric_values": invalid_numeric,
        "out_of_range_values": out_of_range,
        "invalid_dates": invalid_dates,
        "chronology_errors": chronology_errors,
        "record_count": len(records),
    }
