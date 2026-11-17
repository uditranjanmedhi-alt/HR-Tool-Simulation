# hr_simulate/modules/employee_relations.py
"""Employee Relations module UI.
Simulates grievance handling.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.session_manager import init_session
from data.synthetic_generator import generate_employees
from data.data_loader import load_file
from data.data_validator import validate_dataframe
from engines.employee_relations_engine import run_employee_relations_simulation

def render():
    st.title("🤝 Employee Relations")
    st.markdown("Configure grievance rates and HR capacity, then simulate handling.")

    # Workforce size – could reuse synthetic employees
    st.subheader("Workforce Size")
    employee_count = st.number_input("Number of employees", min_value=1, max_value=5000, value=500, step=10)
    st.subheader("Simulation Parameters")
    grievance_rate = st.slider("Grievance rate per employee per month", 0.0, 0.2, 0.02, 0.001)
    avg_resolution = st.slider("Average resolution time (days)", 1, 30, 5)
    hr_capacity = st.slider("HR investigation capacity (parallel cases)", 1, 10, 2)
    if st.button("Run Employee Relations Simulation"):
        params = {
            "employee_count": employee_count,
            "grievance_rate": grievance_rate,
            "avg_resolution_days": avg_resolution,
            "hr_capacity": hr_capacity,
        }
        with st.spinner("Simulating employee relations..."):
            result = run_employee_relations_simulation(params, seed=st.session_state.get("random_seed", 42))
        kpi_df = result["kpis"]
        st.subheader("KPIs")
        st.dataframe(kpi_df.set_index("KPI"))
        # Bar chart of resolved vs total
        fig = go.Figure(go.Bar(x=["Total Grievances", "Resolved"],
                             y=[kpi_df.loc[kpi_df["KPI"] == "Total Grievances", "Value"].values[0],
                                kpi_df.loc[kpi_df["KPI"] == "Grievances Resolved", "Value"].values[0]]))
        fig.update_layout(title="Grievance Outcomes")
        st.plotly_chart(fig, use_container_width=True)
        if st.checkbox("Save this scenario for comparison"):
            scenario = {
                "module": "employee_relations",
                "params": params,
                "kpis": kpi_df.to_dict(orient="records"),
                "timestamp": pd.Timestamp.now().isoformat(),
            }
            st.session_state.scenarios.append(scenario)
            st.success("Scenario saved.")
    if st.button("Reset Parameters"):
        st.experimental_rerun()
