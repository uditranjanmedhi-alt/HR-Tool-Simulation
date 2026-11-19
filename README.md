# HR SIMULATE

An offline-first Streamlit learning lab for exploring seven HR decision areas:
recruitment, attrition, learning and development, performance, workforce
planning, compensation, and employee relations.

## Run locally

From this directory, install the packages listed in `requirements.txt` and run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502
```

Open [http://127.0.0.1:8502](http://127.0.0.1:8502). If port 8502 is occupied,
choose another local port and update the URL accordingly.

## Live app

[HR SIMULATE on Streamlit Community Cloud](https://hr-simulate.streamlit.app)

To deploy a fork, create a new Streamlit Community Cloud app using the GitHub
repository, `main` branch, and `app.py` as the entry point. Keep
`requirements.txt` at the repository root so Cloud can install the dependencies.

The project environment uses Python 3.13. The main app uses NumPy and native
Python records instead of importing Pandas or rendering Arrow-backed Streamlit
tables, so it remains usable under this machine's Application Control policy,
which blocks the installed PyArrow native extension. Pandas remains listed for
the existing legacy module files, but is not imported by the main dashboard.

## Features

- Premium deep-navy dashboard with blue and teal accents, grouped navigation, and responsive module layouts.
- High-contrast Plotly charts use coordinated blue, teal, violet, amber, coral, and green series colors; PDF reports use a clean print-friendly theme.
- Seven configurable, reproducible simulation modules with interactive Plotly visualizations.
- Instant and staged-progress simulation modes.
- Optional Monte Carlo summaries for stochastic models and one-at-a-time sensitivity analysis for all modules.
- Dashboard indicators and recruitment funnel, workload, cost, and hiring-efficiency analysis.
- Editable department headcount mix on the dashboard; changes update the workforce distribution and total employee KPI for the current session.
- Session-only scenario saving and comparison (up to five scenarios).
- Seven educational manager case studies and transparent checklist scoring.
- Seed-reproducible, synthetic datasets for all seven modules with CSV and Excel downloads.
- CSV/Excel preview, explicit worksheet selection, and two upload modes: Aggregate Parameter Mode for mapped scalar simulations and schema-gated Record-Level Analysis Mode for descriptive distributions.
- Record-level compensation, attrition, performance, and training summaries, with optional matched performance period/group comparisons where required fields are present.
- Confirmed aggregate simulations with mapping, cleaning, and provenance; record-level comparisons are clearly descriptive, not causal.
- Offline rule-based recommendations and CSV, Excel, and PDF result exports.
- Module-level methodology and assumptions expanders; reports include scenario
  provenance, generation time, recommendations, assumptions, and an
  illustrative outcome chart where series data is available.
- Synthetic dashboard indicators are labelled illustrative.

All calculations use the entered assumptions and a recorded random seed. Uploaded
files and scenario state remain in the current Streamlit session. The simulations
are educational estimates, not predictions about individuals or automated
employment decisions.

## Model and data documentation

See `docs\MODEL_METHODOLOGY.md`, `docs\DATA_DICTIONARY.md`,
`docs\ASSUMPTIONS_AND_LIMITATIONS.md`, and `docs\PROJECT_AUDIT.md` for the
implemented formulas, generated dataset fields, upload mapping behavior, and
limitations.

## Tests

```powershell
python -m unittest discover -s tests -v
```
