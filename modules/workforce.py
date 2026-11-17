# hr_simulate/modules/workforce.py
"""Workforce Planning module UI.
Configures shift planning, absenteeism, overtime, and runs the workforce engine.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.session_manager import init_session
from engines.workforce_engine import run_workforce_simulation

def render():
    st.title("🗓️ Workforce Planning")
    st.markdown("Configure staffing, shifts, and demand, then simulate workforce performance.")

    st.subheader("Simulation Parameters")
    initial_workforce = st.number_input("Initial workforce size", min_value=1, max_value=5000, value=500, step=10)
    shifts = st.slider("Number of daily shifts", 1, 4, 2)
    shift_duration = st.slider("Shift duration (hours)", 4, 12, 8)
    absenteeism = st.slider("Monthly absenteeism rate", 0.0, 0.3, 0.02, 0.01)
    overtime_hours = st.number_input("Overtime hours per day available", min_value=0, max_value=20, value=5)
    overtime_cost = st.number_input("Overtime cost per hour (USD)", min_value=0.0, value=20.0, step=5.0)
    labour_cost = st.number_input("Labour cost per employee per month (USD)", min_value=0.0, value=3000.0, step=200.0)
    # Simple demand profile: constant or random per day for simulation days
    sim_days = st.slider("Simulation days", 7, 30, 14)
    demand_option = st.radio("Demand pattern", ["Constant", "Random"], index=0)
    if demand_option == "Constant":
        demand_value = st.number_input("Daily demand (headcount)", min_value=1, max_value=2000, value=initial_workforce, step=10)
        demand = [demand_value] * sim_days
    else:
        demand_min = st.number_input("Demand min", min_value=1, max_value=2000, value=int(initial_workforce*0.8))
        demand_max = st.number_input("Demand max", min_value=1, max_value=2000, value=int(initial_workforce*1.2))
        demand = list(np.random.randint(demand_min, demand_max+1, size=sim_days))

    if st.button("Run Workforce Simulation"):
        params = {
            "initial_workforce": initial_workforce,
            "shifts": shifts,
            "shift_duration": shift_duration,
            "absenteeism_rate": absenteeism,
            "overtime_hours": overtime_hours,
            "overtime_cost_per_hour": overtime_cost,
            "labour_cost_per_employee": labour_cost,
            "demand": demand,
        }
        with st.spinner("Simulating workforce planning..."):
            result = run_workforce_simulation(params, seed=st.session_state.get("random_seed", 42))
        kpi_df = result["kpis"]
        st.subheader("KPIs")
        st.dataframe(kpi_df.set_index("KPI"))
        # Plot demand vs available staff
        day_idx = list(range(1, sim_days+1))
        available = []
        for e in result["event_log"]:
            if e["type"] == "day_summary":
                available.append(e["available"] + e["overtime"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=day_idx, y=demand, mode="lines+markers", name="Demand"))
        fig.add_trace(go.Scatter(x=day_idx, y=available, mode="lines+markers", name="Available (incl. overtime)"))
        fig.update_layout(title="Demand vs Available Staff", xaxis_title="Day", yaxis_title="Headcount")
        st.plotly_chart(fig, use_container_width=True)
        if st.checkbox("Save this scenario for comparison"):
            scenario = {
                "module": "workforce",
                "params": params,
                "kpis": kpi_df.to_dict(orient="records"),
                "timestamp": pd.Timestamp.now().isoformat(),
            }
            st.session_state.scenarios.append(scenario)
            st.success("Scenario saved.")
    if st.button("Reset Parameters"):
        st.experimental_rerun()
