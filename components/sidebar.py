# hr_simulate/components/sidebar.py
"""Sidebar UI component for the HR SIMULATE application.
Provides navigation links for all sections defined in the spec.
"""
import streamlit as st

def render_sidebar() -> str:
    """Render the sidebar and return the selected page name.
    Returns
    -------
    str
        The label of the chosen navigation entry.
    """
    st.sidebar.title("HR Simulate")
    st.sidebar.caption("Interactive HR Management Decision Lab")
    # Define navigation sections in the required order
    sections = [
        "Home / Master Dashboard",
        "Recruitment & Talent Acquisition",
        "Employee Attrition & Retention",
        "Learning & Development",
        "Performance Management",
        "Workforce Planning",
        "Compensation & Benefits",
        "Employee Relations",
        "HR Manager Decision Lab",
        "Scenario Comparison",
        "Data Management",
        "AI Recommendations",
        "Reports & Exports",
        "Settings & Documentation",
    ]
    page = st.sidebar.radio("Navigation", sections, index=0)
    return page
