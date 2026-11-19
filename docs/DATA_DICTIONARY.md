# Data dictionary

Generated datasets contain a `synthetic` boolean field and use stable,
seed-derived identifiers. Generated dates are anchored to 2026-01-01 so the same
seed produces the same records across runs.

| Module | Generated columns |
|---|---|
| Recruitment & Talent Acquisition | `candidate_id`, `application_date`, `recruitment_stage`, `interview_result`, `offer_status`, `joining_status`, `department`, `synthetic` |
| Employee Attrition & Retention | `employee_id`, `hire_date`, `exit_date`, `exit_category`, `department`, `tenure_months`, `employment_status`, `synthetic` |
| Learning & Development | `employee_id`, `training_programme`, `enrolment_date`, `completion_status`, `assessment_pass`, `pre_training_score`, `post_training_score`, `synthetic` |
| Performance Management | `employee_id`, `department`, `appraisal_period`, `performance_rating`, `goal_achievement`, `synthetic` |
| Workforce Planning | `month`, `department`, `workforce_supply`, `workforce_demand`, `productivity_index`, `fte_requirement`, `synthetic` |
| Compensation & Benefits | `employee_id`, `department`, `base_salary`, `allowances`, `variable_pay`, `benefits`, `synthetic` |
| Employee Relations | `grievance_id`, `date_raised`, `grievance_category`, `investigation_start_date`, `resolution_date`, `status`, `synthetic` |

## Upload mapping

The upload workflow maps a chosen source column to a named model input. Each
mapping also requires a selected aggregation: mean, median, sum, minimum,
maximum, non-empty count, or unique count. No column mapping is inferred.

The non-empty count aggregation works with identifiers and text fields. Numeric
aggregations require finite numeric cells. Unmapped model inputs keep the
displayed module defaults. For Employee Relations, the optional `total_grievances`
mapping lets a dataset's grievance count be used directly instead of generating
a Poisson count.

## Cleaning and provenance

- Missing mapped cells can cause affected rows to be excluded or can be filled
  with the mapped column's median.
- Invalid numeric cells can stop the run, be replaced by a user-entered numeric
  value for that input, or cause affected rows to be excluded.
- Exact duplicate records can be kept or excluded.
- Every run records source, dataset name, retained record count, mappings,
  aggregations, cleaning choices, excluded row count, and random seed.

The upload flow previews the original records and summarizes mapped-column
validation before requiring explicit user confirmation.
