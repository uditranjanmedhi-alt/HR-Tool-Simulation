# Validation report

## Scope

Validation covers the active Streamlit entry point and the seven calculations
used by it, data generators, upload mapping and cleaning logic, and local
dependency consistency.

## Current checks

Run the following from the `hr_simulate` project directory:

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py engines\simulation_core.py data\synthetic_generator.py data\upload_pipeline.py data\data_loader.py data\data_validator.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

## Results (2026-11-19)

- Python compilation succeeded for all listed files.
- The full test suite passed: 23 tests.
- `pip check` reported no broken requirements.

The test suite checks module results, formula-level attrition/workforce/L&D
outputs, queue invariants, fixed-seed reproducibility, synthetic data
reproducibility and exports, mapping/cleaning/provenance, navigation, module
execution, and uploaded data flowing through the Streamlit UI into a simulation.

## Environment notes

The local Python 3.13 environment previously used for deployment testing is
`hr_simulate\.venv`. Streamlit's dependency graph includes Pandas and PyArrow,
but the deployed app's active code path avoids importing Pandas or rendering
Arrow-backed tables. The app uses standard-library CSV, OpenPyXL, NumPy,
Plotly, SimPy, Streamlit, and optional ReportLab for its active functionality.

Passing local tests does not independently verify a new Streamlit Community
Cloud build; Cloud deployment logs and the live app must be checked after
publishing code.
