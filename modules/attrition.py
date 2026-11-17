# hr_simulate/modules/attrition.py
"""Employee Attrition & Retention module UI.
Allows configuration of workforce size and attrition probabilities,
runs the attrition simulation engine, and displays KPIs and a simple line chart.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.session_manager import init_session
from data.synthetic_generator import generate_employees
from data.data_loader import load_file
from data.data_validator import validate_dataframe
from engines.attrition_engine import run_attrition_simulation

def render():
    st.title("📉 Employee Attrition & Retention")
    st.markdown("Configure attrition parameters and observe workforce evolution.")

    # ----- Data source -----
    st.subheader("Data Source")
    source = st.radio("Select data source", ["Synthetic", "Upload CSV/XLSX"], index=0)
    if source == "Synthetic":
        num_emp = st.slider("Initial number of employees", 100, 2000, 500, step=50)
        seed = st.number_input("Random seed", min_value=0, value=st.session_state.get("random_seed", 42), step=1)
        employees_df = generate_employees(num=num_emp, seed=seed)
        st.success(f"Generated {len(employees_df)} synthetic employee records.")
    else:
        uploaded = st.file_uploader("Upload employees CSV/Excel", type=["csv", "xlsx"])
        if uploaded is not None:
            df = load_file(uploaded)
            if df is not None:
                report = validate_dataframe(df, "employees")
                st.info(report["summary"])
                if not report["valid"]:
                    st.warning("Data validation issues detected. Proceed with caution.")
                employees_df = df
            else:
                st.error("Failed to load file.")
                return
        else:
            st.info("Awaiting file upload…")
            return

    # ----- Simulation Parameters -----
    st.subheader("Simulation Parameters")
    months = st.number_input("Simulation duration (months)", min_value=1, max_value=60, value=12, step=1)
    voluntary = st.slider("Monthly voluntary resignation probability", 0.0, 0.2, 0.02, 0.001)
    involuntary = st.slider("Monthly involuntary exit probability", 0.0, 0.2, 0.01, 0.001)
    retirement = st.slider("Monthly retirement probability", 0.0, 0.2, 0.005, 0.001)
    replacement = st.slider("Average hires per month (replacement rate)", 0, 200, 20, step=5)
    retention_budget = st.number_input("Retention programme budget (USD)", min_value=0.0, value=10000.0, step=500.0, format="%0.2f")

    if st.button("Run Attrition Simulation"):
        params = {
            "initial_workforce": len(employees_df),
            "months": months,
            "voluntary_rate": voluntary,
            "involuntary_rate": involuntary,
            "retirement_rate": retirement,
            "replacement_rate": replacement,
            "retention_budget": retention_budget,
        }
        with st.spinner("Simulating attrition…"):
            result = run_attrition_simulation(params, seed=st.session_state.get("random_seed", 42))
        kpi_df = result["kpis"]
        st.subheader("KPIs")
        st.dataframe(kpi_df.set_index("KPI"))
        # Simple workforce trajectory line chart
        # Re‑run simulation to capture month‑by‑month workforce sizes from the event log
        workforce_series = []
        for month in range(months):
            # Find month_end event
            month_events = [e for e in result["event_log"] if e["type"] == "month_end" and e["time"] == month]
            if month_events:
                workforce_series.append(month_events[0]["workforce"])
            else:
                workforce_series.append(None)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, months + 1)), y=workforce_series, mode="lines+markers"))
        fig.update_layout(title="Workforce Over Time", xaxis_title="Month", yaxis_title="Headcount")
        st.plotly_chart(fig, use_container_width=True)
        # Optionally save scenario
        if st.checkbox("Save this scenario for comparison"):
            scenario = {
                "module": "attrition",
                "params": params,
                "kpis": kpi_df.to_dict(orient="records"),
                "timestamp": pd.Timestamp.now().isoformat(),
            }
            st.session_state.scenarios.append(scenario)
            st.success("Scenario saved.")
    if st.button("Reset Parameters"):
        st.experimental_rerun()
