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

## Results (2026-11-19)

- `compileall -q .` completed successfully.
- The complete unittest suite passed: 36 tests.
- Streamlit AppTest coverage passed for dashboard controls, all seven module
  runs, Aggregate Parameter Mode, Record-Level Analysis Mode, missing-schema
  handling, upload mapping/provenance, exports, Monte Carlo, and sensitivity.
- `pip check` reported no broken requirements.

The full suite also verifies recruitment actual-spend and zero-hire handling,
attrition denominators and cohort accounting, employee-relations queue
conservation and censored waits, performance reward allocation, record-level
paired summaries, bounded sensitivity inputs, stochastic reproducibility, and
zero-volume boundaries.

The project environment is Python 3.13 at `hr_simulate\\.venv`. Streamlit's
dependency graph includes Pandas and PyArrow, but the active app path avoids
Pandas-backed rendering. Passing local tests does not independently verify a
new Streamlit Community Cloud build.
