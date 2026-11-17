# hr_simulate/config/defaults.py
"""Default configuration values for HR Simulate.
These are used to initialise session state and provide sensible defaults
for simulation parameters.
"""

DEFAULT_RANDOM_SEED = 42
DEFAULT_SIM_DURATION_DAYS = 30

# Example defaults for recruitment module – extend as needed
RECRUITMENT_DEFAULTS = {
    "total_applicants": 200,
    "vacancies": 10,
    "recruiters": 2,
    "screening_time": 2,  # days per applicant
    "interview_duration": 1,  # days per interview
    "offer_acceptance_rate": 0.8,
}
