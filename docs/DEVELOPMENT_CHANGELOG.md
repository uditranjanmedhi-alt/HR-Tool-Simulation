# Development changelog

## HR model, data, and validation enhancement

- Corrected recruitment cost per hire to use modeled funded-applicant spend and
  replaced the ambiguous time-to-fill estimate with person-day processing
  effort.
- Separated exposure-based monthly, compounded annualized, period-workforce,
  and original-cohort attrition metrics and reported original-cohort exits.
- Restricted employee-relations average waiting time to cases whose
  investigation started; separately reported unresolved, waiting, in-service,
  and censored cases.
- Added Aggregate Parameter Mode and schema-gated Record-Level Analysis Mode
  for attrition, performance, compensation, and learning/training records.
- Added paired training-score summaries and optional matched performance
  period/group comparisons with explicit non-causal interpretation.
- Bounded sensitivity perturbations by module inputs and rejected non-finite
  numeric simulation parameters.
- Corrected original-cohort retention and monthly workforce conservation in
  attrition simulations.
- Made workforce planning productivity affect FTE requirements and effective
  capacity; summed month-specific forecast labour costs.
- Split L&D eligibility, participation, completion and pass counts; corrected
  ROI and made estimated benefit assumptions visible.
- Replaced Employee Relations throughput arithmetic with a seeded SimPy FIFO
  queue model.
- Made the recruitment cost-per-applicant assumption visible and used it for
  candidate reach.
- Applied performance reward budget to a stated high-performer allocation rule.
- Added reproducible, synthetic records and CSV/XLSX export for each HR module.
- Connected explicitly mapped and user-confirmed uploaded CSV/XLSX data to the
  same module simulation engine.
- Added source provenance, sensitivity analysis, and module-appropriate Monte
  Carlo simulation summaries.
- Added methodology, limitations, data dictionary, audit, and validation
  documentation.

## Final-release hardening

- Made estimated recruitment-spend and cost-per-hire units explicit, handled
  zero-hire cases, and capped interview volume by configured interviewer
  capacity; retained processing effort as a person-day workload, not elapsed
  time-to-fill.
- Scaled Poisson grievance counts by the observation horizon, distinguished
  fixed uploaded counts, and defined the SLA denominator to include overdue
  unresolved cases while excluding cases not yet due.
- Added report-time, simulation-time, seed, provenance, rule-based
  recommendations, and assumptions to CSV, Excel, and PDF reports; PDF reports
  also include an outcome chart when series data is available.
- Added visible module methodology/assumption expanders and explicit currency
  and time units to monetary KPIs.
- Hardened upload validation, record-level range and chronology checks,
  spreadsheet formula-injection handling, and upload/archive size limits.
- Added formula and dashboard tests for the corrections; final local validation
  passed 48 tests, `compileall`, and `pip check` on 2026-11-19.
