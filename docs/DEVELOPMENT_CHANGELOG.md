# Development changelog

## HR model, data, and validation enhancement

- Corrected recruitment cost per hire to use funded-applicant expenditure and
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
