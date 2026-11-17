# hr_simulate/modules/recruitment.py
"""Recruitment & Talent Acquisition module UI.
Provides controls for parameters, data source selection, and runs the recruitment simulation engine.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.session_manager import init_session
from data.synthetic_generator import generate_candidates, generate_employees
from data.data_loader import load_file
from data.data_validator import validate_dataframe
from engines.recruitment_engine import run_recruitment_simulation

def render():
    st.title("📋 Recruitment & Talent Acquisition")
    st.markdown("Configure the recruitment simulation and view results.")

    # ----- Data source -----
    st.subheader("Data Source")
    source = st.radio("Select data source", ["Synthetic", "Upload CSV/XLSX"], index=0)
    if source == "Synthetic":
        # generate synthetic candidates (ignore employees for now)
        num_candidates = st.slider("Number of candidates", min_value=100, max_value=1000, value=300, step=50)
        seed = st.number_input("Random seed", min_value=0, value=st.session_state.get("random_seed", 42), step=1)
        candidates_df = generate_candidates(num=num_candidates, seed=seed)
        st.success(f"Generated {len(candidates_df)} synthetic candidates.")
        data_df = candidates_df
    else:
        uploaded = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
        if uploaded is not None:
            df = load_file(uploaded)
            if df is not None:
                # Validate against candidate schema
                report = validate_dataframe(df, "candidates")
                st.info(report["summary"])
                if not report["valid"]:
                    st.warning("Data has issues – see validation report above.")
                data_df = df
            else:
                st.error("Failed to load file.")
                return
        else:
            st.info("Awaiting file upload...")
            return

    # ----- Simulation Parameters -----
    st.subheader("Simulation Parameters")
    total_applicants = st.number_input("Total applicants", min_value=1, value=int(data_df.shape[0]), step=1)
    recruiters = st.slider("Number of recruiters", 1, 10, 2)
    screening_time = st.slider("Average screening time (days per applicant)", 0.1, 5.0, 1.0, 0.1)
    shortlisting_rate = st.slider("Shortlisting pass rate", 0.0, 1.0, 0.5, 0.01)
    interview_duration = st.slider("Interview duration (days per interview)", 0.1, 5.0, 1.0, 0.1)
    interview_dropout = st.slider("Interview dropout rate", 0.0, 1.0, 0.1, 0.01)
    offer_release = st.slider("Offer release rate", 0.0, 1.0, 0.9, 0.01)
    offer_acceptance = st.slider("Offer acceptance rate", 0.0, 1.0, 0.8, 0.01)
    joining_rate = st.slider("Joining rate after acceptance", 0.0, 1.0, 0.9, 0.01)
    recruitment_budget = st.number_input("Recruitment budget (USD)", min_value=0.0, value=50000.0, step=1000.0, format="%0.2f")

    # ----- Run Simulation -----
    if st.button("Run Instant Simulation"):
        params = {
            "total_applicants": total_applicants,
            "recruiters": recruiters,
            "screening_time": screening_time,
            "shortlisting_rate": shortlisting_rate,
            "interview_duration": interview_duration,
            "interview_dropout_rate": interview_dropout,
            "offer_release_rate": offer_release,
            "offer_acceptance_rate": offer_acceptance,
            "joining_rate": joining_rate,
            "recruitment_budget": recruitment_budget,
        }
        with st.spinner("Simulating recruitment..."):
            result = run_recruitment_simulation(params, seed=st.session_state.get("random_seed", 42))
        kpi_df = result["kpis"]
        st.subheader("KPIs")
        st.dataframe(kpi_df.set_index("KPI"))

        # Funnel visualization using Plotly
        funnel_vals = [
            kpi_df.loc[kpi_df["KPI"] == "Total Applicants", "Value"].values[0],
            kpi_df.loc[kpi_df["KPI"] == "Screened", "Value"].values[0],
            kpi_df.loc[kpi_df["KPI"] == "Shortlisted", "Value"].values[0],
            kpi_df.loc[kpi_df["KPI"] == "Interviewed", "Value"].values[0],
            kpi_df.loc[kpi_df["KPI"] == "Offers Released", "Value"].values[0],
            kpi_df.loc[kpi_df["KPI"] == "Employees Joined", "Value"].values[0],
        ]
        fig = go.Figure(go.Funnel(
            y=["Applicants", "Screened", "Shortlisted", "Interviewed", "Offers", "Joined"],
            x=funnel_vals,
            textinfo="value+percent previous"
        ))
        fig.update_layout(title="Recruitment Funnel")
        st.plotly_chart(fig, use_container_width=True)

        # Store scenario for later comparison (optional)
        if st.checkbox("Save this scenario for comparison"):
            scenario = {
                "module": "recruitment",
                "params": params,
                "kpis": kpi_df.to_dict(orient="records"),
                "timestamp": pd.Timestamp.now().isoformat(),
            }
            st.session_state.scenarios.append(scenario)
            st.success("Scenario saved.")

    # ----- Reset -----
    if st.button("Reset Parameters"):
        st.experimental_rerun()

