# hr_simulate/engines/recruitment_engine.py
"""Recruitment simulation engine using SimPy.
Implements a simple pipeline:
Application → Screening → Shortlisting → Interview → Offer → Joining
Each applicant moves through stages with configurable probabilities and times.
Returns KPI summary and an event log for optional animation.
"""
import simpy
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def run_recruitment_simulation(params: dict, seed: int = 42):
    """Run the recruitment simulation.

    Parameters
    ----------
    params : dict
        Dictionary of simulation parameters. Expected keys:
        - total_applicants (int)
        - recruiters (int)
        - screening_time (float, days per applicant)
        - shortlisting_rate (float, 0-1)
        - interview_duration (float, days per interview)
        - interview_dropout_rate (float, 0-1)
        - offer_release_rate (float, 0-1)   # probability an offer is made after interview
        - offer_acceptance_rate (float, 0-1)
        - joining_rate (float, 0-1)        # probability joined after acceptance
        - recruitment_budget (float)
        - recruiter_productivity (float, not used in simple model)
        - hiring_target (int)               # optional goal
    seed : int
        Random seed for reproducibility.
    Returns
    -------
    dict
        Contains 'kpis' (DataFrame) and 'event_log' (list of dicts).
    """
    np.random.seed(seed)
    env = simpy.Environment()
    # Resources
    recruiter_res = simpy.Resource(env, capacity=params.get("recruiters", 1))
    interview_res = simpy.Resource(env, capacity=params.get("interviewers", 2))

    # KPI counters
    stats = {
        "applicants": params.get("total_applicants", 0),
        "screened": 0,
        "shortlisted": 0,
        "interviewed": 0,
        "offers_released": 0,
        "offers_accepted": 0,
        "joined": 0,
    }
    event_log = []

    def applicant_process(app_id):
        arrival_time = env.now
        event_log.append({"time": arrival_time, "type": "arrival", "app_id": app_id, "module": "recruitment"})
        # Screening
        with recruiter_res.request() as req:
            yield req
            screening_duration = params.get("screening_time", 1)
            yield env.timeout(screening_duration)
            stats["screened"] += 1
            event_log.append({"time": env.now, "type": "screened", "app_id": app_id, "module": "recruitment"})
        # Shortlisting decision
        if np.random.rand() > params.get("shortlisting_rate", 0.5):
            # Dropout after screening
            return
        stats["shortlisted"] += 1
        event_log.append({"time": env.now, "type": "shortlisted", "app_id": app_id, "module": "recruitment"})
        # Interview
        with interview_res.request() as req:
            yield req
            # Possible dropout before interview starts
            if np.random.rand() < params.get("interview_dropout_rate", 0.1):
                return
            interview_dur = params.get("interview_duration", 1)
            yield env.timeout(interview_dur)
            stats["interviewed"] += 1
            event_log.append({"time": env.now, "type": "interviewed", "app_id": app_id, "module": "recruitment"})
        # Offer decision
        if np.random.rand() > params.get("offer_release_rate", 0.9):
            return
        stats["offers_released"] += 1
        event_log.append({"time": env.now, "type": "offer_released", "app_id": app_id, "module": "recruitment"})
        # Acceptance
        if np.random.rand() > params.get("offer_acceptance_rate", 0.8):
            return
        stats["offers_accepted"] += 1
        event_log.append({"time": env.now, "type": "offer_accepted", "app_id": app_id, "module": "recruitment"})
        # Joining
        if np.random.rand() > params.get("joining_rate", 0.9):
            return
        stats["joined"] += 1
        event_log.append({"time": env.now, "type": "joined", "app_id": app_id, "module": "recruitment"})

    # Launch applicant processes
    for i in range(stats["applicants"]):
        env.process(applicant_process(i))
    # Run simulation until all processes finish
    env.run()

    # Compute KPIs
    hires = stats["joined"]
    cost_per_hire = params.get("recruitment_budget", 0) / hires if hires > 0 else np.nan
    time_to_hire = env.now / hires if hires > 0 else np.nan
    kpis = {
        "Total Applicants": stats["applicants"],
        "Screened": stats["screened"],
        "Shortlisted": stats["shortlisted"],
        "Interviewed": stats["interviewed"],
        "Offers Released": stats["offers_released"],
        "Offers Accepted": stats["offers_accepted"],
        "Employees Joined": hires,
        "Screening Conversion Rate": stats["screened"] / stats["applicants"] if stats["applicants"] else 0,
        "Offer Acceptance Rate": stats["offers_accepted"] / stats["offers_released"] if stats["offers_released"] else 0,
        "Joining Ratio": hires / stats["offers_accepted"] if stats["offers_accepted"] else 0,
        "Time to Hire (days)": round(time_to_hire, 2),
        "Cost per Hire": round(cost_per_hire, 2) if not np.isnan(cost_per_hire) else None,
    }
    kpi_df = pd.DataFrame.from_dict(kpis, orient="index", columns=["Value"]).reset_index().rename(columns={"index": "KPI"})
    return {"kpis": kpi_df, "event_log": event_log}
