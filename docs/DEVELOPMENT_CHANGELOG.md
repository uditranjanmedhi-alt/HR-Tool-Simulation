# Development changelog

## HR model, data, and validation enhancement

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
