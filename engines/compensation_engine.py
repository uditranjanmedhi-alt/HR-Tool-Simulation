# hr_simulate/engines/compensation_engine.py
"""Compensation & Benefits simulation engine.
Calculates compensation costs based on salary distribution and benefit parameters.
"""
import numpy as np
import pandas as pd

def run_compensation_simulation(params: dict, seed: int = 42):
    """Run the compensation simulation.

    Expected params keys:
    - employee_count (int)
    - avg_salary (float)
    - salary_std (float)
    - increment_pct (float) – annual increment percentage
    - bonus_pct (float) – proportion of salary allocated to bonuses
    - benefits_pct (float) – proportion of salary allocated to benefits
    """
    np.random.seed(seed)
    count = params.get("employee_count", 0)
    salaries = np.random.normal(params.get("avg_salary", 60000), params.get("salary_std", 15000), size=count).clip(20000, 300000)
    increments = salaries * params.get("increment_pct", 0.03)
    bonuses = salaries * params.get("bonus_pct", 0.05)
    benefits = salaries * params.get("benefits_pct", 0.1)
    total_comp = (salaries + increments + bonuses + benefits).sum()
    kpis = {
        "Employee Count": count,
        "Average Salary": round(salaries.mean(), 2),
        "Total Salary Cost": round(salaries.sum(), 2),
        "Total Increment Cost": round(increments.sum(), 2),
        "Total Bonus Cost": round(bonuses.sum(), 2),
        "Total Benefits Cost": round(benefits.sum(), 2),
        "Total Compensation Cost": round(total_comp, 2),
    }
    kpi_df = pd.DataFrame.from_dict(kpis, orient="index", columns=["Value"]).reset_index().rename(columns={"index": "KPI"})
    # Event log can be simple list of salary entries
    event_log = [{"type": "salary", "value": float(s)} for s in salaries]
    return {"kpis": kpi_df, "event_log": event_log}
