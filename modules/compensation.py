# hr_simulate/modules/compensation.py
"""Compensation & Benefits module UI.
Provides controls for salary distribution and runs the compensation simulation engine.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.session_manager import init_session
from data.synthetic_generator import generate_employees
from data.data_loader import load_file
from data.data_validator import validate_dataframe
from engines.compensation_engine import run_compensation_simulation

def render():
    st.title("💰 Compensation & Benefits")
    st.markdown("Configure compensation parameters and simulate total cost.")

    # Data source – we only need employee count, can use synthetic generation
    st.subheader("Workforce Size")
    employee_count = st.number_input("Number of employees", min_value=1, max_value=5000, value=500, step=10)

    st.subheader("Compensation Parameters")
    avg_salary = st.number_input("Average salary (USD)", min_value=20000.0, value=60000.0, step=5000.0)
    salary_std = st.slider("Salary standard deviation", 5000, 50000, 15000, step=1000)
    increment_pct = st.slider("Annual increment percentage", 0.0, 0.2, 0.03, 0.005)
    bonus_pct = st.slider("Bonus percentage of salary", 0.0, 0.5, 0.05, 0.01)
    benefits_pct = st.slider("Benefits percentage of salary", 0.0, 0.5, 0.1, 0.01)

    if st.button("Run Compensation Simulation"):
        params = {
            "employee_count": employee_count,
            "avg_salary": avg_salary,
            "salary_std": salary_std,
            "increment_pct": increment_pct,
            "bonus_pct": bonus_pct,
            "benefits_pct": benefits_pct,
        }
        with st.spinner("Simulating compensation..."):
            result = run_compensation_simulation(params, seed=st.session_state.get("random_seed", 42))
        kpi_df = result["kpis"]
        st.subheader("KPIs")
        st.dataframe(kpi_df.set_index("KPI"))
        # Salary distribution histogram
        salaries = [e["value"] for e in result["event_log"]]
        fig = go.Figure(go.Histogram(x=salaries, nbinsx=30))
        fig.update_layout(title="Salary Distribution", xaxis_title="Salary (USD)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
        if st.checkbox("Save this scenario for comparison"):
            scenario = {
                "module": "compensation",
                "params": params,
                "kpis": kpi_df.to_dict(orient="records"),
                "timestamp": pd.Timestamp.now().isoformat(),
            }
            st.session_state.scenarios.append(scenario)
            st.success("Scenario saved.")
    if st.button("Reset Parameters"):
        st.experimental_rerun()
