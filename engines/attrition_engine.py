# hr_simulate/engines/attrition_engine.py
"""Employee attrition and retention simulation using SimPy.
Simulates monthly exits (voluntary, involuntary, retirement) for a workforce.
Outputs KPI summary and event log.
"""
import simpy
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def run_attrition_simulation(params: dict, seed: int = 42):
    """Run the attrition simulation.

    Parameters
    ----------
    params : dict
        Expected keys:
        - initial_workforce (int)
        - months (int) – simulation duration
        - voluntary_rate (float) – monthly probability of voluntary resignation
        - involuntary_rate (float) – monthly probability of involuntary exit
        - retirement_rate (float) – monthly probability of retirement
        - replacement_rate (float) – average hires per month (optional)
        - retention_budget (float) – not used in core model but stored
    seed : int
        Random seed for reproducibility.
    Returns
    -------
    dict with keys "kpis" (DataFrame) and "event_log" (list of dicts).
    """
    np.random.seed(seed)
    env = simpy.Environment()
    # KPI counters
    stats = {
        "current": params.get("initial_workforce", 0),
        "voluntary_exits": 0,
        "involuntary_exits": 0,
        "retirements": 0,
        "hires": 0,
    }
    event_log = []

    def month_process(month_idx):
        """Process a single month of attrition and hiring."""
        # Record start of month
        event_log.append({"time": month_idx, "type": "month_start", "module": "attrition"})
        # For each existing employee, decide exit
        for _ in range(stats["current"]):
            rnd = np.random.rand()
            if rnd < params.get("voluntary_rate", 0.02):
                stats["voluntary_exits"] += 1
                event_log.append({"time": month_idx, "type": "voluntary_exit", "module": "attrition"})
                continue
            rnd = np.random.rand()
            if rnd < params.get("involuntary_rate", 0.01):
                stats["involuntary_exits"] += 1
                event_log.append({"time": month_idx, "type": "involuntary_exit", "module": "attrition"})
                continue
            rnd = np.random.rand()
            if rnd < params.get("retirement_rate", 0.005):
                stats["retirements"] += 1
                event_log.append({"time": month_idx, "type": "retirement", "module": "attrition"})
                continue
        # Update workforce after exits
        total_exits = stats["voluntary_exits"] + stats["involuntary_exits"] + stats["retirements"]
        # Simple approximation: assume exits happen at end of month, so workforce after month = previous - exits + hires
        hires = int(params.get("replacement_rate", 0))
        stats["hires"] += hires
        stats["current"] = max(0, stats["current"] - total_exits + hires)
        event_log.append({"time": month_idx, "type": "month_end", "module": "attrition", "workforce": stats["current"]})

    # Schedule each month
    for m in range(params.get("months", 12)):
        env.process(month_process(m))
    env.run()

    # Compute KPIs
    total_months = params.get("months", 12)
    total_exits = stats["voluntary_exits"] + stats["involuntary_exits"] + stats["retirements"]
    avg_workforce = (params.get("initial_workforce", 0) + stats["current"]) / 2
    monthly_attrition_rate = total_exits / (avg_workforce * total_months) if avg_workforce > 0 else 0    annualized_attrition = 1 - (1 - monthly_attrition_rate) ** 12    retention_rate = 1 - monthly_attrition_rate    kpis = {
        "Initial Workforce": params.get("initial_workforce", 0),
        "Final Workforce": stats["current"],
        "Total Voluntary Exits": stats["voluntary_exits"],
        "Total Involuntary Exits": stats["involuntary_exits"],
        "Total Retirements": stats["retirements"],
        "Total Hires": stats["hires"],
        "Monthly Attrition Rate": round(monthly_attrition_rate, 4),
        "Annualized Attrition Rate": round(annualized_attrition, 4),
        "Retention Rate": round(retention_rate, 4),
    }
    kpi_df = pd.DataFrame.from_dict(kpis, orient="index", columns=["Value"]).reset_index().rename(columns={"index": "KPI"})
    return {"kpis": kpi_df, "event_log": event_log}
