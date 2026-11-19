"""Required columns and basic type expectations for module datasets."""

SCHEMA = {
    "employees": [
        "employee_id", "department", "job_level", "salary", "hire_date",
        "experience_years", "performance_score",
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
    "candidates": {"years_experience"},
    "training_records": {"pre_training_score", "post_training_score"},
    "performance_records": {"performance_rating", "goal_achievement"},
    "workforce_records": {
        "workforce_supply", "workforce_demand", "productivity_index", "fte_requirement",
    },
    "compensation_records": {"base_salary", "allowances", "variable_pay", "benefits"},
}
