"""Explicit, auditable mappings from uploaded numeric columns to model inputs."""

from __future__ import annotations

from math import isfinite
from statistics import median
from typing import Any


DEFAULT_SIMULATION_PARAMS: dict[str, dict[str, int | float | None]] = {
    "Recruitment & Talent Acquisition": {
        "vacancies": 50, "applicants": 500, "recruiters": 3, "interviewers": 5,
        "screen_capacity": 200, "interview_capacity": 50, "budget": 75000, "screen_rate": .8,
        "shortlist_rate": .35, "dropout_rate": .1, "offer_rate": .9,
        "acceptance_rate": .75, "joining_rate": .9, "screen_days": .5,
        "interview_days": 1, "cost_per_applicant": 100,
    },
    "Employee Attrition & Retention": {
        "workforce": 500, "months": 12, "voluntary": .02, "involuntary": .005,
        "retirement": .002, "hires": 15, "replacement_cost": 12000,
    },
    "Learning & Development": {
        "employees": 500, "eligibility_rate": 1, "budget": 50000, "cost_per_person": 500,
        "participation": .7, "completion": .82, "pass_rate": .75, "learning_gain": 1.2,
        "pre_training_score": 60, "value_per_gain": 150,
    },
    "Performance Management": {
        "employees": 500, "mean_rating": 3.2, "rating_spread": .8,
        "training_effect": .2, "reward_budget": 50000,
    },
    "Workforce Planning": {
        "workforce": 500, "demand": 540, "months": 12, "growth": .01,
        "turnover": .015, "productivity": 1, "monthly_cost": 5000,
    },
    "Compensation & Benefits": {
        "employees": 500, "salary": 60000, "spread": 15000,
        "increment": .04, "bonus": .05, "benefits": .12,
    },
    "Employee Relations": {
        "employees": 500, "grievance_rate": .025, "capacity": 8,
        "resolution_days": 12, "period_days": 30, "sla_days": 30,
        "total_grievances": None,
    },
}

AGGREGATIONS = ("mean", "median", "sum", "minimum", "maximum", "count", "unique count")


def _cell_value(row: list[Any], column_index: int) -> Any:
    return row[column_index] if column_index < len(row) else None


def map_uploaded_data(
    columns: list[str],
    rows: list[list[Any]],
    mappings: dict[str, str],
    aggregations: dict[str, str],
    defaults: dict[str, int | float | None],
    *,
    missing_treatment: str,
    invalid_treatment: str,
    duplicate_treatment: str,
    invalid_replacements: dict[str, float] | None = None,
    random_seed: int,
    dataset_name: str,
    dataset_source: str = "Uploaded company data",
) -> tuple[dict[str, int | float], dict, dict]:
    """Apply user-selected column mappings and return params, provenance and validation."""
    unknown_params = set(mappings) - set(defaults)
    if unknown_params:
        raise ValueError(f"Unknown simulation input mappings: {', '.join(sorted(unknown_params))}.")
    if not mappings:
        raise ValueError("Map at least one uploaded column to a simulation input.")
    if missing_treatment not in {"exclude affected rows", "median-fill numeric columns"}:
        raise ValueError("Choose an explicit missing-value treatment.")
    if invalid_treatment not in {
        "stop if invalid values exist", "exclude rows with invalid values",
        "replace invalid values with explicit number",
    }:
        raise ValueError("Choose an explicit invalid-value treatment.")
    invalid_replacements = invalid_replacements or {}
    for parameter, replacement in invalid_replacements.items():
        if not isfinite(float(replacement)):
            raise ValueError(f"Replacement for {parameter} must be finite.")
    if duplicate_treatment not in {"keep duplicates", "exclude duplicate rows"}:
        raise ValueError("Choose an explicit duplicate-row treatment.")

    column_indexes: dict[str, int] = {}
    for parameter, column_name in mappings.items():
        if column_name not in columns:
            raise ValueError(f"Mapped column {column_name!r} for {parameter} is not present.")
        aggregation = aggregations.get(parameter)
        if aggregation not in AGGREGATIONS:
            raise ValueError(f"Choose a supported aggregation for {parameter}.")
        column_indexes[parameter] = columns.index(column_name)

    duplicate_keys: set[tuple[str, ...]] = set()
    duplicate_rows: set[int] = set()
    for row_index, row in enumerate(rows):
        key = tuple(repr(value) for value in row)
        if key in duplicate_keys:
            duplicate_rows.add(row_index)
        duplicate_keys.add(key)

    complete_rows: list[dict[str, float | None]] = []
    missing_cells = invalid_cells = 0
    for row_index, row in enumerate(rows):
        mapped: dict[str, float | None] = {}
        row_missing = row_invalid = False
        for parameter, column_index in column_indexes.items():
            raw = _cell_value(row, column_index)
            if raw is None or (isinstance(raw, str) and not raw.strip()):
                missing_cells += 1
                mapped[parameter] = None
                row_missing = True
                continue
            aggregation = aggregations[parameter]
            if aggregation in {"count", "unique count"}:
                mapped[parameter] = 1.0
                continue
            try:
                if isinstance(raw, bool):
                    raise ValueError
                numeric_value = float(raw)
            except (TypeError, ValueError):
                invalid_cells += 1
                if invalid_treatment == "replace invalid values with explicit number" and parameter in invalid_replacements:
                    numeric_value = float(invalid_replacements[parameter])
                    mapped[parameter] = numeric_value
                else:
                    mapped[parameter] = None
                    row_invalid = True
                continue
            if not (numeric_value == numeric_value and abs(numeric_value) != float("inf")):
                invalid_cells += 1
                if invalid_treatment == "replace invalid values with explicit number" and parameter in invalid_replacements:
                    numeric_value = float(invalid_replacements[parameter])
                    mapped[parameter] = numeric_value
                else:
                    mapped[parameter] = None
                    row_invalid = True
                continue
            mapped[parameter] = numeric_value
        complete_rows.append({
            "row_index": float(row_index),
            "duplicate": 1.0 if row_index in duplicate_rows else 0.0,
            "missing": 1.0 if row_missing else 0.0,
            "invalid": 1.0 if row_invalid else 0.0,
            **mapped,
        })

    if invalid_cells and invalid_treatment == "stop if invalid values exist":
        raise ValueError(
            f"Found {invalid_cells} non-numeric or non-finite value(s) in mapped numeric columns. "
            "Choose whether to exclude the affected records."
        )
    if (invalid_cells and invalid_treatment == "replace invalid values with explicit number"
            and any(row["invalid"] for row in complete_rows)):
        raise ValueError(
            "Provide an explicit numeric replacement for every mapped input containing invalid values, "
            "or choose to exclude the affected records."
        )
    if missing_cells and missing_treatment == "exclude affected rows":
        retained = [row for row in complete_rows if row["missing"] == 0]
    else:
        retained = list(complete_rows)
    if invalid_cells:
        retained = [row for row in retained if row["invalid"] == 0]
    if duplicate_treatment == "exclude duplicate rows":
        retained = [row for row in retained if row["duplicate"] == 0]
    if not retained:
        raise ValueError("No rows remain after the selected data-cleaning steps.")

    params: dict[str, int | float] = dict(defaults)
    applied_mappings: dict[str, dict[str, str]] = {}
    count_parameters = {
        "vacancies", "applicants", "recruiters", "interviewers",
        "screen_capacity", "interview_capacity", "workforce", "employees", "months", "hires",
        "capacity", "total_grievances",
    }
    for parameter, column_name in mappings.items():
        aggregation = aggregations[parameter]
        selected: list[float] = []
        seen: set[str] = set()
        for row in retained:
            value = row[parameter]
            if value is None:
                if aggregation in {"count", "unique count"}:
                    continue
                if missing_treatment != "median-fill numeric columns":
                    continue
                available = [
                    float(row[parameter]) for row in retained
                    if row[parameter] is not None
                ]
                if not available:
                    continue
                value = float(median(available))
            if aggregation == "unique count":
                raw = _cell_value(rows[int(row["row_index"])], column_indexes[parameter])
                if raw is not None and str(raw) not in seen:
                    seen.add(str(raw))
            else:
                selected.append(float(value))
        if aggregation == "count":
            aggregate = float(len(selected)) if selected else 0.0
        elif aggregation == "unique count":
            aggregate = float(len(seen))
        elif aggregation == "mean":
            aggregate = sum(selected) / len(selected) if selected else 0.0
        elif aggregation == "median":
            aggregate = float(median(selected)) if selected else 0.0
        elif aggregation == "sum":
            aggregate = sum(selected)
        elif aggregation == "minimum":
            aggregate = min(selected) if selected else 0.0
        else:
            aggregate = max(selected) if selected else 0.0
        # Count-valued simulation inputs are expected as integers.
        if parameter in count_parameters:
            if not float(aggregate).is_integer():
                raise ValueError(
                    f"Mapped count input {parameter} aggregated to {aggregate:g}; "
                    "choose an aggregation that produces a whole number."
                )
            params[parameter] = int(aggregate)
        else:
            params[parameter] = float(aggregate)
        applied_mappings[parameter] = {
            "column": column_name,
            "aggregation": aggregation,
        }

    excluded = len(rows) - len(retained)
    validation = {
        "input_records": len(rows),
        "retained_records": len(retained),
        "excluded_records": excluded,
        "duplicate_records": len(duplicate_rows),
        "missing_cells_in_mapped_columns": missing_cells,
        "invalid_cells_in_mapped_columns": invalid_cells,
        "missing_treatment": missing_treatment,
        "invalid_treatment": invalid_treatment,
        "invalid_value_replacements": {
            key: float(value) for key, value in invalid_replacements.items() if key in mappings
        },
        "duplicate_treatment": duplicate_treatment,
    }
    provenance = {
        "dataset_source": dataset_source,
        "dataset_name": dataset_name,
        "input_record_count": len(rows),
        "record_count": len(retained),
        "column_mappings": applied_mappings,
        "filters": {
            "invalid_mapped_values": invalid_treatment,
            "duplicates": duplicate_treatment,
        },
        "excluded_records": excluded,
        "missing_value_treatment": missing_treatment,
        "invalid_value_replacements": {
            key: float(value) for key, value in invalid_replacements.items() if key in mappings
        },
        "random_seed": int(random_seed),
    }
    return params, provenance, validation
