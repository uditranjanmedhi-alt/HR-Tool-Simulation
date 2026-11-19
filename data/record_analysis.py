"""Descriptive analysis that preserves supported uploaded HR records."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from math import isfinite
from statistics import mean, median, pstdev
from typing import Any

from .schema import VALUE_RANGES


RECORD_LEVEL_SCHEMAS = {
    "Employee Attrition & Retention": {
        "schema": "attrition_records",
        "required": (
            "employee_id", "hire_date", "exit_date", "exit_category", "department",
            "tenure_months", "employment_status",
        ),
        "numeric": (("tenure_months", "Tenure (months)"),),
        "categorical": ("employment_status", "exit_category"),
        "notes": (
            "Status and exit-category counts describe the uploaded snapshot; no period attrition rate is inferred "
            "without an explicitly defined risk period and person-time denominator.",
        ),
    },
    "Learning & Development": {
        "schema": "training_records",
        "required": (
            "employee_id", "training_programme", "enrolment_date", "completion_status",
            "assessment_pass", "pre_training_score", "post_training_score",
        ),
        "numeric": (
            ("pre_training_score", "Pre-training score"),
            ("post_training_score", "Post-training score"),
        ),
        "categorical": ("completion_status", "assessment_pass", "training_programme"),
        "notes": (
            "Pre/post score change uses only records with both scores; it is descriptive and does not establish "
            "a causal training effect.",
        ),
    },
    "Performance Management": {
        "schema": "performance_records",
        "required": (
            "employee_id", "department", "appraisal_period", "performance_rating",
            "goal_achievement",
        ),
        "numeric": (
            ("performance_rating", "Performance rating"),
            ("goal_achievement", "Goal achievement"),
        ),
        "categorical": ("department", "appraisal_period"),
        "notes": (
            "Rating distributions and period comparisons are descriptive. A difference in group changes is not "
            "a causal estimate or an employment recommendation.",
        ),
    },
    "Compensation & Benefits": {
        "schema": "compensation_records",
        "required": (
            "employee_id", "department", "base_salary", "allowances",
            "variable_pay", "benefits",
        ),
        "numeric": (
            ("base_salary", "Base salary"),
            ("allowances", "Allowances"),
            ("variable_pay", "Variable pay"),
            ("benefits", "Benefits"),
            ("total_compensation", "Total compensation"),
        ),
        "categorical": ("department",),
        "notes": (
            "Total compensation is computed per record as base salary + allowances + variable pay + benefits. "
            "Distribution summaries are not a pay-equity analysis.",
        ),
    },
}

def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _number(value: Any) -> float | None:
    if _is_missing(value) or isinstance(value, bool):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if isfinite(numeric) else None


def _bounded_number(module: str, column: str, value: Any) -> float | None:
    numeric = _number(value)
    if numeric is None:
        return None
    schema = RECORD_LEVEL_SCHEMAS[module]["schema"]
    bounds = VALUE_RANGES.get(schema, {}).get(column)
    if bounds is None:
        return numeric
    lower, upper = bounds
    if numeric < lower or (upper is not None and numeric > upper):
        return None
    return numeric


def _parse_date(value: Any) -> date | None:
    if _is_missing(value):
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _summary(values: list[float]) -> dict[str, int | float | None]:
    if not values:
        return {
            "Records with value": 0, "Mean": None, "Median": None,
            "Standard deviation": None, "Minimum": None, "Maximum": None,
        }
    return {
        "Records with value": len(values),
        "Mean": round(mean(values), 4),
        "Median": round(median(values), 4),
        "Standard deviation": round(pstdev(values), 4),
        "Minimum": round(min(values), 4),
        "Maximum": round(max(values), 4),
    }


def _paired_performance_comparison(
    records: list[dict[str, Any]],
    pre_period: str,
    post_period: str,
    group_column: str | None,
    group_a: str | None,
    group_b: str | None,
) -> tuple[dict | None, dict | None, int]:
    by_employee_period: dict[tuple[str, str], list[float]] = defaultdict(list)
    employee_groups: dict[tuple[str, str], set[str]] = defaultdict(set)
    all_period_counts: Counter[tuple[str, str]] = Counter()
    for record in records:
        employee_id = record.get("employee_id")
        period = record.get("appraisal_period")
        if not _is_missing(employee_id) and not _is_missing(period):
            all_period_counts[(str(employee_id).strip(), str(period).strip())] += 1
        rating = _bounded_number(
            "Performance Management", "performance_rating",
            record.get("performance_rating"),
        )
        if _is_missing(employee_id) or _is_missing(period) or rating is None:
            continue
        employee_key = str(employee_id).strip()
        period_key = str(period).strip()
        by_employee_period[(employee_key, period_key)].append(rating)
        if group_column is not None and not _is_missing(record.get(group_column)):
            employee_groups[(employee_key, period_key)].add(str(record[group_column]))

    duplicate_period_keys = {
        key for key, count in all_period_counts.items() if count > 1
    }
    valid_periods = {
        key: values[0] for key, values in by_employee_period.items()
        if len(values) == 1 and key not in duplicate_period_keys
    }
    changes: list[tuple[str, float]] = []
    paired_values: list[tuple[float, float]] = []
    for employee_id in {key[0] for key in by_employee_period}:
        pre_value = valid_periods.get((employee_id, pre_period))
        post_value = valid_periods.get((employee_id, post_period))
        if pre_value is not None and post_value is not None:
            pre_mean = pre_value
            post_mean = post_value
            paired_values.append((pre_mean, post_mean))
            changes.append((employee_id, post_mean - pre_mean))

    if not changes:
        return None, None, len(duplicate_period_keys)
    all_changes = [change for _, change in changes]
    paired = {
        "Baseline period": pre_period,
        "Follow-up period": post_period,
        "Matched employees": len(paired_values),
        "Ambiguous employee-period groups excluded": len(duplicate_period_keys),
        "Baseline mean rating": round(mean(pre for pre, _ in paired_values), 4),
        "Follow-up mean rating": round(mean(post for _, post in paired_values), 4),
        "Mean paired rating change (points)": round(mean(all_changes), 4),
    }
    group_comparison = None
    if group_column and group_a and group_b and group_a != group_b:
        grouped_changes: dict[str, list[float]] = {group_a: [], group_b: []}
        for employee_id, change in changes:
            pre_groups = employee_groups.get((employee_id, pre_period), set())
            post_groups = employee_groups.get((employee_id, post_period), set())
            if len(pre_groups) != 1 or pre_groups != post_groups:
                continue
            group = next(iter(pre_groups))
            if group in grouped_changes:
                grouped_changes[group].append(change)
        if grouped_changes[group_a] and grouped_changes[group_b]:
            mean_a = mean(grouped_changes[group_a])
            mean_b = mean(grouped_changes[group_b])
            group_comparison = {
                "Group column": group_column,
                "Group A": group_a,
                "Group A matched employees": len(grouped_changes[group_a]),
                "Group A mean change (points)": round(mean_a, 4),
                "Group B": group_b,
                "Group B matched employees": len(grouped_changes[group_b]),
                "Group B mean change (points)": round(mean_b, 4),
                "Difference in mean change (A − B, points)": round(mean_a - mean_b, 4),
            }
    return paired, group_comparison, len(duplicate_period_keys)


def analyze_record_level_data(
    module: str,
    columns: list[str],
    rows: list[list[Any]],
    *,
    exclude_duplicate_rows: bool = False,
    pre_period: str | None = None,
    post_period: str | None = None,
    comparison_group_column: str | None = None,
    group_a: str | None = None,
    group_b: str | None = None,
) -> dict:
    """Summarize record-level distributions without converting records to simulation inputs."""
    if module not in RECORD_LEVEL_SCHEMAS:
        raise ValueError(f"Record-Level Analysis Mode is not supported for {module}.")
    spec = RECORD_LEVEL_SCHEMAS[module]
    missing_columns = [column for column in spec["required"] if column not in columns]
    if missing_columns:
        raise ValueError(
            "Record-level analysis requires these columns: " + ", ".join(missing_columns) + "."
        )
    if not rows:
        raise ValueError("The dataset has no records to analyze.")
    if (pre_period is None) != (post_period is None):
        raise ValueError("Select both a baseline and follow-up period for a paired comparison.")
    if pre_period is not None and pre_period == post_period:
        raise ValueError("Baseline and follow-up periods must be different.")
    if comparison_group_column is not None and comparison_group_column not in columns:
        raise ValueError(f"Comparison group column {comparison_group_column!r} is not present.")
    if comparison_group_column is not None and (pre_period is None or group_a is None or group_b is None):
        raise ValueError("Group evaluation requires selected baseline/follow-up periods and two groups.")
    if (group_a is None) != (group_b is None):
        raise ValueError("Select both groups for a comparison.")
    if group_a is not None and group_a == group_b:
        raise ValueError("Choose two different comparison groups.")

    column_indexes = {column: index for index, column in enumerate(columns)}
    seen: set[tuple[str, ...]] = set()
    records: list[dict[str, Any]] = []
    duplicate_count = 0
    for row in rows:
        key = tuple(repr(value) for value in row)
        if key in seen:
            duplicate_count += 1
            if exclude_duplicate_rows:
                continue
        seen.add(key)
        records.append({
            column: row[index] if index < len(row) else None
            for column, index in column_indexes.items()
        })
    if not records:
        raise ValueError("No records remain after duplicate exclusion.")

    employee_ids = [
        str(record["employee_id"]).strip() for record in records
        if not _is_missing(record.get("employee_id"))
    ]
    employee_id_counts = Counter(employee_ids)
    duplicated_employee_ids = {
        employee_id for employee_id, count in employee_id_counts.items() if count > 1
    }
    analysis_records = records
    duplicate_employee_records_excluded = 0
    if module in {"Employee Attrition & Retention", "Compensation & Benefits"}:
        analysis_records = [
            record for record in records
            if _is_missing(record.get("employee_id"))
            or str(record["employee_id"]).strip() not in duplicated_employee_ids
        ]
        duplicate_employee_records_excluded = len(records) - len(analysis_records)
    employee_period_counts = Counter(
        (str(record.get("employee_id")).strip(), str(record.get("appraisal_period")).strip())
        for record in records
        if module == "Performance Management"
        and not _is_missing(record.get("employee_id"))
        and not _is_missing(record.get("appraisal_period"))
    )
    duplicate_employee_periods = sum(
        count > 1 for count in employee_period_counts.values()
    )
    duplicate_employee_period_records = sum(
        count - 1 for count in employee_period_counts.values() if count > 1
    )
    invalid_dates: dict[str, int] = {}
    chronology_errors: dict[str, int] = {}
    date_columns = {
        "Employee Attrition & Retention": ("hire_date", "exit_date"),
        "Learning & Development": ("enrolment_date",),
    }.get(module, ())
    for column in date_columns:
        invalid_dates[column] = sum(
            not _is_missing(record.get(column)) and _parse_date(record.get(column)) is None
            for record in records
        )
    if module == "Employee Attrition & Retention":
        chronology_errors["exit_before_hire"] = sum(
            hire_date is not None and exit_date is not None and exit_date < hire_date
            for hire_date, exit_date in (
                (_parse_date(record.get("hire_date")), _parse_date(record.get("exit_date")))
                for record in records
            )
        )

    if module == "Compensation & Benefits":
        total_values = []
        for record in analysis_records:
            components = [_bounded_number(module, column, record.get(column))
                          for column in ("base_salary", "allowances", "variable_pay", "benefits")]
            if all(value is not None for value in components):
                total_values.append(sum(value for value in components if value is not None))
            else:
                total_values.append(None)
        for record, total in zip(analysis_records, total_values):
            record["total_compensation"] = total

    invalid_or_missing: dict[str, int] = {}
    invalid_numeric_values: dict[str, int] = {}
    summaries = []
    distributions: dict[str, list[float]] = {}
    for column, label in spec["numeric"]:
        values = []
        missing_or_invalid = 0
        for record in analysis_records:
            raw_value = record.get(column)
            value = _bounded_number(module, column, raw_value)
            if value is None:
                missing_or_invalid += 1
                if not _is_missing(raw_value) and _number(raw_value) is not None:
                    invalid_numeric_values[label] = invalid_numeric_values.get(label, 0) + 1
            else:
                values.append(value)
        invalid_or_missing[label] = missing_or_invalid
        summaries.append({"Measure": label, **_summary(values)})
        if values:
            distributions[label] = values

    paired_score = None
    if module == "Learning & Development":
        gains = []
        for record in analysis_records:
            pre = _bounded_number(module, "pre_training_score", record.get("pre_training_score"))
            post = _bounded_number(module, "post_training_score", record.get("post_training_score"))
            if pre is not None and post is not None:
                gains.append(post - pre)
        if gains:
            summaries.append({"Measure": "Paired score change", **_summary(gains)})
            distributions["Paired score change"] = gains
            paired_score = {
                "Matched records": len(gains),
                "Records excluded without complete valid scores": len(analysis_records) - len(gains),
                "Mean pre/post score change (points)": round(mean(gains), 4),
            }

    category_counts = []
    for column in spec["categorical"]:
        counts = Counter(str(record[column]).strip() for record in analysis_records
                         if not _is_missing(record.get(column)))
        category_counts.extend(
            {"Field": column, "Category": category, "Records": count}
            for category, count in sorted(counts.items())
        )

    paired_period = group_comparison = None
    ambiguous_employee_periods = 0
    if module == "Performance Management" and pre_period is not None:
        available_periods = {
            str(record["appraisal_period"]) for record in analysis_records
            if not _is_missing(record.get("appraisal_period"))
        }
        if pre_period not in available_periods or post_period not in available_periods:
            raise ValueError("Selected appraisal periods are not present in the retained records.")
        if comparison_group_column is not None and (group_a is None or group_b is None):
            raise ValueError("Select two groups or disable comparison-group evaluation.")
        paired_period, group_comparison, ambiguous_employee_periods = _paired_performance_comparison(
            analysis_records, pre_period, post_period, comparison_group_column, group_a, group_b,
        )

    missing_employee_ids = sum(_is_missing(record.get("employee_id")) for record in records)
    data_quality = {
        "Missing employee IDs": missing_employee_ids,
        "Duplicate employee IDs": (
            len(duplicated_employee_ids)
            if module in {"Employee Attrition & Retention", "Compensation & Benefits"}
            else 0
        ),
        "Extra records for duplicate employee IDs": (
            sum(employee_id_counts[employee_id] - 1 for employee_id in duplicated_employee_ids)
            if module in {"Employee Attrition & Retention", "Compensation & Benefits"}
            else 0
        ),
        "Duplicate employee-period groups": duplicate_employee_periods,
        "Extra records in duplicate employee-period groups": duplicate_employee_period_records,
        "Invalid dates": sum(invalid_dates.values()),
        "Chronology errors": sum(chronology_errors.values()),
        "Out-of-range numeric values": sum(invalid_numeric_values.values()),
    }
    return {
        "module": module,
        "mode": "Record-Level Analysis Mode",
        "schema": spec["schema"],
        "input_records": len(rows),
        "retained_records": len(analysis_records),
        "duplicate_records": duplicate_count,
        "excluded_duplicate_records": duplicate_count if exclude_duplicate_rows else 0,
        "excluded_duplicate_employee_records": duplicate_employee_records_excluded,
        "summaries": summaries,
        "distributions": distributions,
        "invalid_or_missing_numeric_values": invalid_or_missing,
        "out_of_range_numeric_values": invalid_numeric_values,
        "invalid_dates": invalid_dates,
        "chronology_errors": chronology_errors,
        "data_quality": data_quality,
        "ambiguous_employee_periods_excluded_from_comparison": ambiguous_employee_periods,
        "category_counts": category_counts,
        "paired_score_comparison": paired_score,
        "paired_period_comparison": paired_period,
        "comparison_group_evaluation": group_comparison,
        "notes": list(spec["notes"]),
    }
