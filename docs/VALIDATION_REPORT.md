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

## Results (2026-11-19, final-release hardening)

- `compileall -q .` completed successfully.
- The complete unittest suite passed: 48 tests.
- Streamlit AppTest passed for dashboard controls, all seven module runs and
  methodology expanders, report generation and charts for all seven modules,
  Aggregate Parameter Mode, Record-Level Analysis Mode, missing-schema
  handling, upload mapping/provenance, exports, Monte Carlo, and sensitivity.
- `pip check` reported no broken requirements.

Formula and boundary coverage includes recruitment expenditure from funded
applicants, zero hires and interviewer capacity; separate attrition rates and
original-cohort accounting; observation-horizon-scaled grievance arrivals,
queue conservation, SLA denominators and censored waits; corrected learning
benefit and compensation units; workforce gap rounding; record-level duplicate
and range checks; bounded sensitivity inputs; stochastic reproducibility; and
zero-volume boundaries. Upload limits and spreadsheet formula-injection
protection are also covered.

The project environment is Python 3.13 at `hr_simulate\\.venv`. Streamlit's
dependency graph includes Pandas and PyArrow, but the active app path avoids
Pandas-backed rendering. Passing local tests does not independently verify a new Streamlit Community
Cloud build.
