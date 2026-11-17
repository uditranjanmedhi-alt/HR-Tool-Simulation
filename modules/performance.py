# hr_simulate/modules/performance.py
"""Performance Management module UI.
Runs the performance simulation engine and displays KPIs and a rating distribution bar chart.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.session_manager import init_session
from engines.performance_engine import run_performance_simulation

def render():
    st.title("📈 Performance Management")
    st.markdown("Configure appraisal parameters and simulate performance outcomes.")

    st.subheader("Simulation Parameters")
    employee_count = st.number_input("Number of employees", min_value=1, max_value=5000, value=500, step=10)
    # Rating distribution sliders must sum to 1 – use normalized input
    st.write("Rating distribution (must sum to 1)")
    r1 = st.slider("Rating 1 (low)", 0.0, 1.0, 0.1, 0.01)
    r2 = st.slider("Rating 2", 0.0, 1.0, 0.2, 0.01)
    r3 = st.slider("Rating 3", 0.0, 1.0, 0.4, 0.01)
    r4 = st.slider("Rating 4", 0.0, 1.0, 0.2, 0.01)
    r5 = st.slider("Rating 5 (high)", 0.0, 1.0, 0.1, 0.01)
    total = r1 + r2 + r3 + r4 + r5    if total == 0:
        st.error("Rating distribution cannot be all zero.")
        return
    rating_distribution = [r1/total, r2/total, r3/total, r4/total, r5/total]
    appraisal_freq = st.slider("Appraisal frequency (months)", 1, 24, 12)
    increment_budget = st.number_input("Increment budget (USD)", min_value=0.0, value=50000.0, step=1000.0, format="%0.2f")
    bonus_pct = st.slider("Bonus percentage of increment", 0.0, 0.5, 0.05, 0.01)
    pip_thresh = st.slider("PIP rating threshold (≤) ", 1, 5, 2)

    if st.button("Run Performance Simulation"):
        params = {
            "employee_count": employee_count,
            "rating_distribution": rating_distribution,
            "appraisal_frequency_months": appraisal_freq,
            "increment_budget": increment_budget,
            "bonus_percentage": bonus_pct,
            "pip_threshold": pip_thresh,
        }
        with st.spinner("Simulating performance..."):
            result = run_performance_simulation(params, seed=st.session_state.get("random_seed", 42))
        kpi_df = result["kpis"]
        st.subheader("KPIs")
        st.dataframe(kpi_df.set_index("KPI"))
        # Bar chart of rating distribution (using the sampled results, not the input probabilities)
        # Re‑sample to get actual counts for visualization
        counts = result["event_log"]
        rating_counts = {1:0,2:0,3:0,4:0,5:0}
        for e in counts:
            if e["type"] == "appraisal":
                rating_counts[e["rating"]] += 1
        fig = go.Figure(go.Bar(x=["1","2","3","4","5"], y=[rating_counts[i] for i in range(1,6)]))
        fig.update_layout(title="Rating Outcomes", xaxis_title="Rating", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
        if st.checkbox("Save this scenario for comparison"):
            scenario = {
                "module": "performance",
                "params": params,
                "kpis": kpi_df.to_dict(orient="records"),
                "timestamp": pd.Timestamp.now().isoformat(),
            }
            st.session_state.scenarios.append(scenario)
            st.success("Scenario saved.")
    if st.button("Reset Parameters"):
        st.experimental_rerun()
