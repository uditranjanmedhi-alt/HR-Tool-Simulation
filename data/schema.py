# hr_simulate/data/schema.py
"""Data schema definitions for HR Simulate.
Provides column name expectations for each entity type.
"""

# Define required columns for each synthetic dataset
SCHEMA = {
    "employees": [
        "employee_id",
        "department",
        "job_level",
        "salary",
        "hire_date",
        "experience_years",
        "performance_score",
    ],
    "candidates": [
        "candidate_id",
        "source",
        "applied_position",
        "education_level",
        "years_experience",
        "application_date",
    ],
    "recruitment_applications": [
        "application_id",
        "candidate_id",
        "vacancy_id",
        "status",
        "screening_date",
        "interview_date",
        "offer_date",
        "joined_date",
    ],
    "training_records": [
        "record_id",
        "employee_id",
        "programme_id",
        "start_date",
        "end_date",
        "completion_status",
        "pre_score",
        "post_score",
    ],
    "performance_records": [
        "record_id",
        "employee_id",
        "evaluation_period",
        "performance_score",
        "rating",
    ],
    "compensation_records": [
        "record_id",
        "employee_id",
        "salary",
        "bonus",
        "benefits",
        "effective_date",
    ],
    "grievance_records": [
        "grievance_id",
        "employee_id",
        "category",
        "submission_date",
        "resolution_date",
        "outcome",
    ],
}
