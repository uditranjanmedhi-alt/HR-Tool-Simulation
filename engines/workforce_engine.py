# hr_simulate/engines/workforce_engine.py
"""Workforce Planning simulation engine.
Simulates staffing across shifts with absenteeism and overtime.
"""
import simpy
import numpy as np
import pandas as pd

def run_workforce_simulation(params: dict, seed: int = 42):
    """Run workforce planning simulation.

    Expected params keys:
    - initial_workforce (int)
    - shifts (int) number of daily shifts
    - shift_duration (float) hours per shift
    - absenteeism_rate (float) monthly probability
    - overtime_hours (float) per month
    - overtime_cost_per_hour (float)
    - labour_cost_per_employee (float) per month
    - demand (list of float) expected demand per day (length = simulation_days)
    """
    np.random.seed(seed)
    env = simpy.Environment()
    workforce = params.get("initial_workforce", 0)
    shift_res = simpy.Resource(env, capacity=workforce)
    stats = {
        "total_overtime_hours": 0.0,
        "total_overtime_cost": 0.0,
        "understaffed_days": 0,
        "overstaffed_days": 0,
        "labour_cost": 0.0,
    }
    event_log = []

    def daily_process(day_idx):
        demand = params["demand"][day_idx] if day_idx < len(params["demand"]) else params["demand"][-1]
        # absenteeism affects available staff for the day
        absent = np.random.binomial(workforce, params.get("absenteeism_rate", 0.02))
        available = max(0, workforce - absent)
        # overtime can fill gap up to overtime_hours limit
        gap = max(0, demand - available)
        overtime_needed = min(gap, params.get("overtime_hours", 0))
        overtime_cost = overtime_needed * params.get("overtime_cost_per_hour", 20)
        stats["total_overtime_hours"] += overtime_needed
        stats["total_overtime_cost"] += overtime_cost
        # Determine understaffed/overstaffed
        if demand > available + overtime_needed:
            stats["understaffed_days"] += 1
        elif available > demand:
            stats["overstaffed_days"] += 1
        # Record labour cost
        labour_cost = workforce * params.get("labour_cost_per_employee", 3000)
        stats["labour_cost"] += labour_cost
        event_log.append({"time": day_idx, "type": "day_summary", "demand": demand,
                          "available": available, "overtime": overtime_needed, "labour_cost": labour_cost})
        # No explicit wait – move to next day
        yield env.timeout(1)

    sim_days = len(params.get("demand", [0]))
    for d in range(sim_days):
        env.process(daily_process(d))
    env.run()

    # KPI calculations
    kpis = {
        "Initial Workforce": workforce,
        "Total Labour Cost": round(stats["labour_cost"], 2),
        "Total Overtime Hours": round(stats["total_overtime_hours"], 2),
        "Total Overtime Cost": round(stats["total_overtime_cost"], 2),
        "Understaffed Days": stats["understaffed_days"],
        "Overstaffed Days": stats["overstaffed_days"],
    }
    kpi_df = pd.DataFrame.from_dict(kpis, orient="index", columns=["Value"]).reset_index().rename(columns={"index": "KPI"})
    return {"kpis": kpi_df, "event_log": event_log}
