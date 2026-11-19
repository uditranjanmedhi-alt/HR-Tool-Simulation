# Validation report

## Scope

Validation covers the active Streamlit entry point and seven simulation
modules, record-level analysis and aggregate upload flows, schema validation,
synthetic datasets, sensitivity and Monte Carlo calculations, AppTest
navigation/runs, and dependency consistency.

## Commands

Run from the `hr_simulate` project directory using the installed project
environment:

```powershell
.\.venv\Scripts\python.exe -m compileall -q .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

## Results (2026-11-19, final release correction)

- `compileall -q .` completed successfully.
- The complete unittest suite passed: 50 tests.
- `pip check` reported no broken requirements.
- An additional seeded stress run completed 100,000 simulation executions
  across all seven modules (seeds 0–99,999). Every run returned KPI and chart
  data with finite numeric KPI values; recruitment runs also verified estimated
  spend and cost per hire against the funded-applicant formula.
- Streamlit AppTest passed for dashboard controls, all seven module runs and
  methodology expanders, Aggregate Parameter Mode, Record-Level Analysis Mode,
  upload mapping/provenance, scenario comparison, Monte Carlo, and sensitivity.
  Report generation exercised CSV, Excel, and PDF payload creation for each
  simulation module; download controls rendered without exceptions.

Formula and boundary coverage includes estimated recruitment spend from funded
applicants, zero hires and interviewer capacity; separate attrition rates and
original-cohort accounting; observation-horizon-scaled grievance arrivals,
queue conservation, SLA denominators and censored waits; corrected learning
benefit and compensation units; workforce gap rounding; record-level duplicate
and range checks; bounded sensitivity inputs; stochastic reproducibility; and
zero-volume boundaries. Upload limits and spreadsheet formula-injection
protection are also covered.

The project environment is Python 3.13 at `hr_simulate\\.venv`. The local
Streamlit process started successfully; its health endpoint and home page both
returned HTTP 200. After publishing commit `060d721`, the hosted Streamlit
Community Cloud app loaded the dashboard and recruitment module; manager
insights displayed the revised estimated-spend label. Future deployments still
require their own live verification.
