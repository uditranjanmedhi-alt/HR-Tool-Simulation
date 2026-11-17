# hr_simulate/engines/employee_relations_engine.py
"""Employee Relations simulation engine.
Simulates grievance submission, investigation, and resolution.
"""
import simpy
import numpy as np
import pandas as pd

def run_employee_relations_simulation(params: dict, seed: int = 42):
    """Run the employee relations simulation.

    Expected params keys:
    - employee_count (int)
    - grievance_rate (float) – average grievances per employee per month
    - avg_resolution_days (float)
    - hr_capacity (int) – number of parallel investigations
    """
    np.random.seed(seed)
    env = simpy.Environment()
    hr_res = simpy.Resource(env, capacity=params.get("hr_capacity", 2))
    total_grievances = int(params.get("employee_count", 0) * params.get("grievance_rate", 0.02))
    stats = {
        "grievances_submitted": total_grievances,
        "grievances_resolved": 0,
        "total_resolution_time": 0.0,
    }
    event_log = []

    def grievance_process(grievance_id):
        # Submission event
        event_log.append({"time": env.now, "type": "submitted", "id": grievance_id})
        with hr_res.request() as req:
            yield req
            # Investigation time drawn from exponential around avg_resolution_days
            duration = max(0.1, np.random.exponential(params.get("avg_resolution_days", 5)))
            yield env.timeout(duration)
            stats["grievances_resolved"] += 1
            stats["total_resolution_time"] += duration
            event_log.append({"time": env.now, "type": "resolved", "id": grievance_id, "duration": duration})

    for i in range(total_grievances):
        env.process(grievance_process(i))
    env.run()

    avg_res_time = (stats["total_resolution_time"] / stats["grievances_resolved"]) if stats["grievances_resolved"] else np.nan
    kpis = {
        "Total Grievances": total_grievances,
        "Grievances Resolved": stats["grievances_resolved"],
        "Average Resolution Time (days)": round(avg_res_time, 2) if not np.isnan(avg_res_time) else None,
        "Resolution Rate": round(stats["grievances_resolved"] / total_grievances, 2) if total_grievances else 0,
    }
    kpi_df = pd.DataFrame.from_dict(kpis, orient="index", columns=["Value"]).reset_index().rename(columns={"index": "KPI"})
    return {"kpis": kpi_df, "event_log": event_log}
