"""Reproducible, standard-library synthetic HR dataset generators."""

from __future__ import annotations

from datetime import date, timedelta
from io import BytesIO, StringIO
import csv
from typing import Any

import numpy as np
from openpyxl import Workbook


MODULE_DATASETS = {
    "Recruitment & Talent Acquisition": "recruitment",
    "Employee Attrition & Retention": "attrition",
    "Learning & Development": "learning",
    "Performance Management": "performance",
    "Workforce Planning": "workforce",
    "Compensation & Benefits": "compensation",
    "Employee Relations": "employee_relations",
}

_DEPARTMENTS = ("Engineering", "Operations", "Sales", "Finance", "HR")
_BASE_DATE = date(2026, 1, 1)


def _date_in_past(rng: np.random.Generator, days: int) -> date:
    return _BASE_DATE - timedelta(days=int(rng.integers(0, days + 1)))


def generate_synthetic_data(
    module: str,
    size: int = 500,
    seed: int = 42,
) -> list[dict]:
    """Generate coherent records for one module; IDs and dates are seed-reproducible."""
    if module not in MODULE_DATASETS:
        raise ValueError(f"Unknown HR simulation module: {module}")
    if not isinstance(size, int) or size < 0:
        raise ValueError("Dataset size must be a non-negative integer.")
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("Random seed must be a non-negative integer.")
    rng = np.random.default_rng(seed)
    records: list[dict] = []

    if module == "Recruitment & Talent Acquisition":
        stages = ("Applied", "Screened", "Shortlisted", "Interviewed", "Offered", "Joined")
        for index in range(size):
            final_stage = int(rng.choice(len(stages), p=[.18, .16, .18, .20, .16, .12]))
            stage = stages[final_stage]
            interview_result = (
                ("Pass" if final_stage >= 4 else str(rng.choice(["Pass", "Fail"])))
                if final_stage >= 3 else None
            )
            offer_status = ("Accepted" if final_stage == 5 else str(rng.choice(["Accepted", "Declined"]))) \
                if final_stage >= 4 else "Not offered"
            records.append({
                "candidate_id": f"CAND-{index + 1:06d}",
                "application_date": _date_in_past(rng, 180).isoformat(),
                "recruitment_stage": stage,
                "interview_result": interview_result,
                "offer_status": offer_status,
                "joining_status": "Joined" if stage == "Joined" else "Not joined",
                "department": str(rng.choice(_DEPARTMENTS)),
                "synthetic": True,
            })
    elif module == "Employee Attrition & Retention":
        for index in range(size):
            hire_date = _date_in_past(rng, 365 * 10)
            exited = bool(rng.random() < .12)
            tenure_days = (_BASE_DATE - hire_date).days
            exit_date = (
                hire_date + timedelta(days=int(rng.integers(1, max(2, tenure_days + 1))))
                if exited and tenure_days else None
            )
            exited = exit_date is not None
            records.append({
                "employee_id": f"EMP-{index + 1:06d}",
                "hire_date": hire_date.isoformat(),
                "exit_date": exit_date.isoformat() if exit_date else None,
                "exit_category": str(rng.choice(["Voluntary", "Involuntary", "Retirement"])) if exited else None,
                "department": str(rng.choice(_DEPARTMENTS)),
                "tenure_months": max(0, (_BASE_DATE - hire_date).days // 30),
                "employment_status": "Exited" if exited else "Active",
                "synthetic": True,
            })
    elif module == "Learning & Development":
        for index in range(size):
            enrolled = bool(rng.random() < .72)
            completed = enrolled and bool(rng.random() < .84)
            pre_score = round(float(rng.uniform(35, 85)), 1)
            post_score = round(min(100.0, pre_score + float(rng.normal(8, 4))), 1) if completed else None
            records.append({
                "employee_id": f"EMP-{index + 1:06d}",
                "training_programme": str(rng.choice(["Leadership", "Safety", "Analytics", "Communication"])),
                "enrolment_date": _date_in_past(rng, 365).isoformat() if enrolled else None,
                "completion_status": "Completed" if completed else ("In progress" if enrolled else "Not enrolled"),
                "assessment_pass": bool(post_score is not None and post_score >= 50) if post_score is not None else None,
                "pre_training_score": pre_score,
                "post_training_score": post_score,
                "synthetic": True,
            })
    elif module == "Performance Management":
        for index in range(size):
            records.append({
                "employee_id": f"EMP-{index + 1:06d}",
                "department": str(rng.choice(_DEPARTMENTS)),
                "appraisal_period": "2025",
                "performance_rating": round(float(np.clip(rng.normal(3.2, .75), 1, 5)), 2),
                "goal_achievement": round(float(np.clip(rng.normal(.78, .15), 0, 1)), 3),
                "synthetic": True,
            })
    elif module == "Workforce Planning":
        for index in range(size):
            month_offset = index % 12
            forecast_month = date(2026, month_offset + 1, 1)
            department = str(rng.choice(_DEPARTMENTS))
            supply = int(rng.integers(10, 201))
            demand = max(0, supply + int(rng.integers(-20, 31)))
            productivity = round(float(rng.uniform(.75, 1.25)), 3)
            records.append({
                "month": forecast_month.strftime("%Y-%m"),
                "department": department,
                "workforce_supply": supply,
                "workforce_demand": demand,
                "productivity_index": productivity,
                "fte_requirement": round(demand / productivity, 2),
                "synthetic": True,
            })
    elif module == "Compensation & Benefits":
        for index in range(size):
            salary = round(float(np.clip(rng.normal(60000, 15000), 25000, 250000)), 2)
            records.append({
                "employee_id": f"EMP-{index + 1:06d}",
                "department": str(rng.choice(_DEPARTMENTS)),
                "base_salary": salary,
                "allowances": round(salary * float(rng.uniform(0, .12)), 2),
                "variable_pay": round(salary * float(rng.uniform(0, .2)), 2),
                "benefits": round(salary * float(rng.uniform(.05, .18)), 2),
                "synthetic": True,
            })
    else:
        for index in range(size):
            raised = _date_in_past(rng, 90)
            investigation_start = raised + timedelta(days=int(rng.integers(0, 15)))
            resolved = investigation_start + timedelta(days=int(rng.integers(1, 46)))
            status = "Resolved" if resolved <= _BASE_DATE else "Open"
            records.append({
                "grievance_id": f"GRV-{index + 1:06d}",
                "date_raised": raised.isoformat(),
                "grievance_category": str(rng.choice(["Workload", "Communication", "Policy", "Management", "Other"])),
                "investigation_start_date": investigation_start.isoformat(),
                "resolution_date": resolved.isoformat() if status == "Resolved" else None,
                "status": status,
                "synthetic": True,
            })
    return records


def generate_employees(num: int = 500, num_departments: int = 5, seed: int = 42) -> Any:
    """Legacy employee-generator API; Pandas is imported only when this API is called."""
    if num < 0 or num_departments <= 0:
        raise ValueError("Number of departments must be positive.")
    if seed < 0:
        raise ValueError("Random seed must be non-negative.")
    rng = np.random.default_rng(seed)
    department_names = [f"Dept_{index + 1}" for index in range(num_departments)]
    records = []
    for index in range(num):
        records.append({
            "employee_id": f"EMP-{index + 1:06d}",
            "department": str(rng.choice(department_names)),
            "job_level": str(rng.choice(["Junior", "Mid", "Senior", "Lead"], p=[.4, .3, .2, .1])),
            "salary": int(np.clip(rng.normal(60000, 15000), 30000, 200000)),
            "hire_date": _date_in_past(rng, 365 * 5).isoformat(),
            "experience_years": round(float(np.clip(rng.exponential(3), 0, 30)), 1),
            "performance_score": round(float(np.clip(rng.normal(3, .7), 1, 5)), 2),
            "synthetic": True,
        })
    import pandas as pd

    return pd.DataFrame(records)


def generate_candidates(num: int = 300, num_departments: int = 5, seed: int = 42) -> Any:
    """Legacy candidate-generator API; Pandas is imported only when this API is called."""
    if num < 0 or num_departments <= 0:
        raise ValueError("Number of departments must be positive.")
    if seed < 0:
        raise ValueError("Random seed must be non-negative.")
    rng = np.random.default_rng(seed)
    records = [
        {
            "candidate_id": f"CAND-{index + 1:06d}",
            "source": str(rng.choice(["Referral", "Job Portal", "Agency", "Campus", "Internal"])),
            "applied_position": str(rng.choice(["Engineer", "Analyst", "Manager", "Director"])),
            "education_level": str(rng.choice(["High School", "Bachelors", "Masters", "PhD"],
                                              p=[.1, .6, .25, .05])),
            "years_experience": round(float(np.clip(rng.exponential(2), 0, 20)), 1),
            "application_date": _date_in_past(rng, 180).isoformat(),
            "synthetic": True,
        }
        for index in range(num)
    ]
    import pandas as pd

    return pd.DataFrame(records)


def records_to_csv(records: list[dict]) -> bytes:
    """Serialize synthetic records to UTF-8 CSV bytes."""
    if not records:
        return b""
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue().encode("utf-8-sig")


def records_to_xlsx(records: list[dict], sheet_name: str = "Synthetic data") -> bytes:
    """Serialize synthetic records to an Excel workbook in memory."""
    workbook = Workbook(write_only=True)
    worksheet = workbook.create_sheet(title=sheet_name[:31])
    columns = list(records[0]) if records else []
    if columns:
        worksheet.append(columns)
        for record in records:
            worksheet.append([record.get(column) for column in columns])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
