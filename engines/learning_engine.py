# hr_simulate/engines/learning_engine.py
"""Learning & Development simulation engine.
Simulates employee registration for training programmes, participation, completion, assessment, and skill improvement.
Generates KPIs and an event log for later animation.
"""
import simpy
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def run_learning_simulation(params: dict, seed: int = 42):
    """Run the L&D simulation.

    Parameters
    ----------
    params : dict
        Expected keys:
        - employee_count (int)
        - training_budget (float)
        - num_programmes (int)
        - programme_duration (float, days)
        - cost_per_employee (float)
        - participation_rate (float, 0-1)
        - completion_rate (float, 0-1)
        - assessment_pass_rate (float, 0-1)
        - knowledge_retention (float, 0-1)
        - productivity_improvement (float, % increase e.g., 0.05 for 5%)
    seed : int
        Random seed for reproducibility.
    Returns
    -------
    dict with "kpis" (DataFrame) and "event_log" (list of dicts).
    """
    np.random.seed(seed)
    env = simpy.Environment()
    # Resource representing trainer capacity (simple fixed number of concurrent sessions)
    trainer_res = simpy.Resource(env, capacity=params.get("trainer_capacity", 2))

    stats = {
        "employees": params.get("employee_count", 0),
        "registered": 0,
        "participated": 0,
        "completed": 0,
        "passed_assessment": 0,
        "total_cost": 0.0,
        "skill_gain": 0.0,
    }
    event_log = []

    def employee_process(emp_id):
        # Registration – each employee decides to register based on participation_rate
        if np.random.rand() > params.get("participation_rate", 0.6):
            return
        stats["registered"] += 1
        event_log.append({"time": env.now, "type": "registered", "emp_id": emp_id, "module": "learning"})
        # Acquire trainer slot
        with trainer_res.request() as req:
            yield req
            # Participation
            stats["participated"] += 1
            event_log.append({"time": env.now, "type": "participated", "emp_id": emp_id, "module": "learning"})
            # Training duration
            yield env.timeout(params.get("programme_duration", 5))
            # Completion decision
            if np.random.rand() > params.get("completion_rate", 0.8):
                return
            stats["completed"] += 1
            event_log.append({"time": env.now, "type": "completed", "emp_id": emp_id, "module": "learning"})
            # Assessment
            if np.random.rand() < params.get("assessment_pass_rate", 0.7):
                stats["passed_assessment"] += 1
                # Skill gain calculation – simple linear based on retention
                gain = params.get("knowledge_retention", 0.5) * params.get("productivity_improvement", 0.05)
                stats["skill_gain"] += gain                event_log.append({"time": env.now, "type": "assessment_pass", "emp_id": emp_id, "module": "learning"})

        # Cost accrual per employee who participated
        stats["total_cost"] += params.get("cost_per_employee", 1000)

    # Launch processes for each employee
    for i in range(stats["employees"]):
        env.process(employee_process(i))
    env.run()

    # KPI calculations
    total_participated = stats["participated"]
    total_completed = stats["completed"]
    total_passed = stats["passed_assessment"]
    avg_skill_gain = (stats["skill_gain"] / total_passed) if total_passed else 0
    training_roi = ((avg_skill_gain * params.get("productivity_improvement", 0.05) * params.get("employee_count", 0) * 1000) - stats["total_cost"]) / stats["total_cost"] if stats["total_cost"] > 0 else np.nan
    kpis = {
        "Employees": stats["employees"],
        "Registered": stats["registered"],
        "Participated": total_participated,
        "Completed": total_completed,
        "Assessment Pass": total_passed,
        "Average Skill Gain": round(avg_skill_gain, 4),
        "Total Training Cost": round(stats["total_cost"], 2),
        "Training ROI": round(training_roi, 4) if not np.isnan(training_roi) else None,
    }
    kpi_df = pd.DataFrame.from_dict(kpis, orient="index", columns=["Value"]).reset_index().rename(columns={"index": "KPI"})
    return {"kpis": kpi_df, "event_log": event_log}
