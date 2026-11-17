# hr_simulate/modules/learning_development.py
"""Learning & Development module UI.
Allows configuration of training budget, programmes, participation, etc., runs the learning simulation engine, and displays KPIs with a simple bar chart.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.session_manager import init_session
from data.synthetic_generator import generate_employees
from data.data_loader import load_file
from data.data_validator import validate_dataframe
from engines.learning_engine import run_learning_simulation

def render():
    st.title("🎓 Learning & Development")
    st.markdown("Configure training programmes and simulate employee skill development.")

    # ----- Data source -----
    st.subheader("Data Source")
    source = st.radio("Select data source", ["Synthetic Employees", "Upload Employees CSV/XLSX"], index=0)
    if source == "Synthetic Employees":
        num_emp = st.slider("Number of employees", 100, 2000, 500, step=50)
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
    training_budget = st.number_input("Training budget (USD)", min_value=0.0, value=50000.0, step=1000.0, format="%0.2f")
    num_programmes = st.slider("Number of training programmes", 1, 20, 5)
    programme_duration = st.slider("Programme duration (days)", 1, 30, 5)
    cost_per_emp = st.slider("Cost per employee per programme (USD)", 100, 5000, 1000)
    participation_rate = st.slider("Participation rate", 0.0, 1.0, 0.6, 0.01)
    completion_rate = st.slider("Completion rate", 0.0, 1.0, 0.8, 0.01)
    assessment_pass = st.slider("Assessment pass rate", 0.0, 1.0, 0.7, 0.01)
    knowledge_retention = st.slider("Knowledge retention factor", 0.0, 1.0, 0.5, 0.01)
    productivity_improvement = st.slider("Productivity improvement per successful learner (%)", 0.0, 0.2, 0.05, 0.005)
    trainer_capacity = st.slider("Trainer capacity (parallel sessions)", 1, 10, 2)

    if st.button("Run Learning Simulation"):
        params = {
            "employee_count": len(employees_df),
            "training_budget": training_budget,
            "num_programmes": num_programmes,
            "programme_duration": programme_duration,
            "cost_per_employee": cost_per_emp,
            "participation_rate": participation_rate,
            "completion_rate": completion_rate,
            "assessment_pass_rate": assessment_pass,
            "knowledge_retention": knowledge_retention,
            "productivity_improvement": productivity_improvement,
            "trainer_capacity": trainer_capacity,
        }
        with st.spinner("Simulating learning & development..."):
            result = run_learning_simulation(params, seed=st.session_state.get("random_seed", 42))
        kpi_df = result["kpis"]
        st.subheader("KPIs")
        st.dataframe(kpi_df.set_index("KPI"))
        # Simple bar chart of key metrics
        fig = go.Figure()
        fig.add_trace(go.Bar(x=["Participated", "Completed", "Assessment Pass"],
                             y=[kpi_df.loc[kpi_df["KPI"] == "Participated", "Value"].values[0],
                                kpi_df.loc[kpi_df["KPI"] == "Completed", "Value"].values[0],
                                kpi_df.loc[kpi_df["KPI"] == "Assessment Pass", "Value"].values[0]]))
        fig.update_layout(title="Learning Outcomes", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
        if st.checkbox("Save this scenario for comparison"):
            scenario = {
                "module": "learning",
                "params": params,
                "kpis": kpi_df.to_dict(orient="records"),
                "timestamp": pd.Timestamp.now().isoformat(),
            }
            st.session_state.scenarios.append(scenario)
            st.success("Scenario saved.")
    if st.button("Reset Parameters"):
        st.experimental_rerun()
