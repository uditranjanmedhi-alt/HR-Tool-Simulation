# hr_simulate/engines/performance_engine.py
"""Performance Management simulation engine.
Simulates annual performance appraisal for a workforce.
Generates KPIs and an event log.
"""
import simpy
import numpy as np
import pandas as pd

def run_performance_simulation(params: dict, seed: int = 42):
    """Run the performance management simulation.

    Expected params keys:
    - employee_count (int)
    - rating_distribution (list of floats, sum=1) for ratings 1-5
    - appraisal_frequency_months (int)
    - increment_budget (float) – total amount available for salary increments
    - bonus_percentage (float) – proportion of salary allocated to bonuses
    - pip_threshold (float) – rating below which PIP is triggered
    """
    np.random.seed(seed)
    env = simpy.Environment()
    # KPI counters
    stats = {
        "high_performers": 0,
        "low_performers": 0,
        "pip_cases": 0,
        "total_bonus": 0.0,
        "total_increment": 0.0,
    }
    event_log = []

    rating_probs = params.get("rating_distribution", [0.1, 0.2, 0.4, 0.2, 0.1])
    pip_thresh = params.get("pip_threshold", 2)  # rating <= this triggers PIP
    increment_budget = params.get("increment_budget", 50000.0)
    bonus_pct = params.get("bonus_percentage", 0.05)

    def employee_process(emp_id):
        # Determine rating
        rating = np.random.choice([1, 2, 3, 4, 5], p=rating_probs)
        if rating >= 4:
            stats["high_performers"] += 1
        if rating <= 2:
            stats["low_performers"] += 1
            if rating <= pip_thresh:
                stats["pip_cases"] += 1
                event_log.append({"time": env.now, "type": "pip_started", "emp_id": emp_id})
        # Increment allocation – proportionally split budget across employees
        inc = increment_budget / params.get("employee_count", 1)
        stats["total_increment"] += inc
        # Bonus allocation
        bonus = inc * bonus_pct
        stats["total_bonus"] += bonus
        event_log.append({"time": env.now, "type": "appraisal", "emp_id": emp_id, "rating": rating})
        # Simulate PIP duration if any (simple fixed 2 months)
        if rating <= pip_thresh:
            yield env.timeout(2)  # months
            event_log.append({"time": env.now, "type": "pip_completed", "emp_id": emp_id})

    for i in range(params.get("employee_count", 0)):
        env.process(employee_process(i))
    # Run for the appraisal period (e.g., 12 months)
    env.run(until=params.get("appraisal_frequency_months", 12))

    # KPI calculations
    total_emp = params.get("employee_count", 0)
    kpis = {
        "Total Employees": total_emp,
        "High Performers (%)": round(stats["high_performers"] / total_emp * 100, 2) if total_emp else 0,
        "Low Performers (%)": round(stats["low_performers"] / total_emp * 100, 2) if total_emp else 0,
        "PIP Cases": stats["pip_cases"],
        "Total Increment Allocated": round(stats["total_increment"], 2),
        "Total Bonus Allocated": round(stats["total_bonus"], 2),
    }
    kpi_df = pd.DataFrame.from_dict(kpis, orient="index", columns=["Value"]).reset_index().rename(columns={"index": "KPI"})
    return {"kpis": kpi_df, "event_log": event_log}
