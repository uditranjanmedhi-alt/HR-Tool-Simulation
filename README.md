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

## Deploy on Streamlit Community Cloud

Create a GitHub repository containing this project, then create a new app in
Streamlit Community Cloud with the repository, `main` branch, and `app.py` as
the entry point. Keep `requirements.txt` at the repository root so Cloud can
install the app dependencies.

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
- Dashboard indicators and recruitment funnel, workload, cost, and hiring-efficiency analysis.
- Editable department headcount mix on the dashboard; changes update the workforce distribution and total employee KPI for the current session.
- Session-only scenario saving and comparison (up to five scenarios).
- Seven educational manager case studies and transparent checklist scoring.
- Local CSV/Excel preview and validation summary.
- Offline rule-based recommendations and CSV, Excel, and PDF result exports.
- Synthetic dashboard indicators are labelled illustrative.

All calculations use the entered assumptions and a recorded random seed. Uploaded
files and scenario state remain in the local Streamlit session. The simulations
are educational estimates, not predictions about individuals or automated
employment decisions.

## Tests

```powershell
python -m unittest discover -s tests -v
```
