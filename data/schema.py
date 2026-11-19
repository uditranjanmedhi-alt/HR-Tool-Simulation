"""Required columns and basic type expectations for module datasets."""

SCHEMA = {
    "employees": [
        "employee_id", "department", "job_level", "salary", "hire_date",
        "experience_years", "performance_score",
    ],
    "attrition_records": [
        "employee_id", "hire_date", "exit_date", "exit_category", "department",
        "tenure_months", "employment_status",
    ],
    "candidates": [
        "candidate_id", "source", "applied_position", "education_level",
        "years_experience", "application_date",
    ],
    "recruitment_applications": [
        "candidate_id", "application_date", "recruitment_stage", "interview_result",
        "offer_status", "joining_status", "department",
    ],
    "training_records": [
        "employee_id", "training_programme", "enrolment_date", "completion_status",
        "assessment_pass", "pre_training_score", "post_training_score",
    ],
    "performance_records": [
        "employee_id", "department", "appraisal_period", "performance_rating",
        "goal_achievement",
    ],
    "workforce_records": [
        "month", "department", "workforce_supply", "workforce_demand",
        "productivity_index", "fte_requirement",
    ],
    "compensation_records": [
        "employee_id", "department", "base_salary", "allowances",
        "variable_pay", "benefits",
    ],
    "grievance_records": [
        "grievance_id", "date_raised", "grievance_category",
        "investigation_start_date", "resolution_date", "status",
    ],
}

NUMERIC_COLUMNS = {
    "employees": {"salary", "experience_years", "performance_score"},
    "attrition_records": {"tenure_months"},
    "candidates": {"years_experience"},
    "training_records": {"pre_training_score", "post_training_score"},
    "performance_records": {"performance_rating", "goal_achievement"},
    "workforce_records": {
        "workforce_supply", "workforce_demand", "productivity_index", "fte_requirement",
    },
    "compensation_records": {"base_salary", "allowances", "variable_pay", "benefits"},
}

VALUE_RANGES = {
    "employees": {
        "salary": (0, None), "experience_years": (0, None),
        "performance_score": (1, 5),
    },
    "attrition_records": {"tenure_months": (0, None)},
    "candidates": {"years_experience": (0, None)},
    "training_records": {
        "pre_training_score": (0, 100), "post_training_score": (0, 100),
    },
    "performance_records": {
        "performance_rating": (1, 5), "goal_achievement": (0, 1),
    },
    "workforce_records": {
        "workforce_supply": (0, None), "workforce_demand": (0, None),
        "productivity_index": (0.000001, None), "fte_requirement": (0, None),
    },
    "compensation_records": {
        "base_salary": (0, None), "allowances": (0, None),
        "variable_pay": (0, None), "benefits": (0, None),
    },
}

DATE_COLUMNS = {
    "employees": {"hire_date"},
    "attrition_records": {"hire_date", "exit_date"},
    "candidates": {"application_date"},
    "training_records": {"enrolment_date"},
    "grievance_records": {"date_raised", "investigation_start_date", "resolution_date"},
}

DATE_ORDERING = {
    "attrition_records": (("hire_date", "exit_date"),),
    "grievance_records": (
        ("date_raised", "investigation_start_date"),
        ("investigation_start_date", "resolution_date"),
    ),
}

NULLABLE_COLUMNS = {
    "attrition_records": {"exit_date", "exit_category"},
    "training_records": {"enrolment_date", "assessment_pass", "post_training_score"},
    "grievance_records": {"investigation_start_date", "resolution_date"},
}
