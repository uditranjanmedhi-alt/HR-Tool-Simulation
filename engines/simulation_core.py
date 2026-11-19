"""Reproducible, educational HR simulation calculations."""

from __future__ import annotations

import numpy as np
import simpy


MODULES = {
    "Recruitment & Talent Acquisition": "recruitment",
    "Employee Attrition & Retention": "attrition",
    "Learning & Development": "learning",
    "Performance Management": "performance",
    "Workforce Planning": "workforce",
    "Compensation & Benefits": "compensation",
    "Employee Relations": "employee_relations",
}

STOCHASTIC_MODULES = {
    "Employee Attrition & Retention",
    "Performance Management",
    "Compensation & Benefits",
    "Employee Relations",
}

SENSITIVITY_OUTPUTS = {
    "Recruitment & Talent Acquisition": "Employees Joined",
    "Employee Attrition & Retention": "Final Workforce",
    "Learning & Development": "Estimated Financial Benefit (assumption-based)",
    "Performance Management": "Average Performance Score After Intervention",
    "Workforce Planning": "Hiring Requirement",
    "Compensation & Benefits": "Total Compensation Cost",
    "Employee Relations": "Open Grievances",
}


def _result(kpis: dict, series: list[dict], notes: list[str] | None = None) -> dict:
    return {
        "kpis": [{"KPI": key, "Value": value} for key, value in kpis.items()],
        "series": series,
        "notes": notes or [],
    }


def run_simulation(module: str, params: dict, seed: int = 42) -> dict:
    """Run a single-module simulation and return its measured outputs."""
    rng = np.random.default_rng(int(seed))
    if module not in MODULES:
        raise ValueError(f"Unknown HR simulation module: {module}")

    if module == "Recruitment & Talent Acquisition":
        vacancies = int(params["vacancies"])
        applicants = int(params["applicants"])
        recruiters = int(params["recruiters"])
        interviewers = int(params["interviewers"])
        budget = float(params["budget"])
        cost_per_applicant = float(params.get("cost_per_applicant", 100.0))
        if min(vacancies, applicants) < 0 or min(recruiters, interviewers) <= 0:
            raise ValueError("Vacancies and applicants must be non-negative; recruiter and interviewer counts must be positive.")
        if budget < 0 or cost_per_applicant <= 0:
            raise ValueError("Recruitment budget must be non-negative and cost per applicant must be positive.")
        for key in ("screen_rate", "shortlist_rate", "dropout_rate", "offer_rate",
                    "acceptance_rate", "joining_rate"):
            if not 0 <= float(params[key]) <= 1:
                raise ValueError(f"{key} must be between 0 and 1.")
        screen_capacity_per_recruiter = int(params.get("screen_capacity", applicants))
        if screen_capacity_per_recruiter < 0:
            raise ValueError("Screening capacity must be non-negative.")
        funded_applicants = min(applicants, int(budget / cost_per_applicant))
        screening_capacity = screen_capacity_per_recruiter * recruiters
        screened = min(funded_applicants, int(funded_applicants * params["screen_rate"]), screening_capacity)
        shortlisted = int(screened * params["shortlist_rate"])
        interviewed = int(shortlisted * (1 - params["dropout_rate"]))
        offers = int(interviewed * params["offer_rate"])
        accepted = int(offers * params["acceptance_rate"])
        joined = min(int(params["vacancies"]), int(accepted * params["joining_rate"]))
        screen_days = float(params["screen_days"])
        interview_days = float(params["interview_days"])
        if min(screen_days, interview_days) < 0:
            raise ValueError("Screening and interview effort must be non-negative.")
        days = (screened * screen_days / recruiters
                + interviewed * interview_days / interviewers)
        stages = ["Applicants", "Screened", "Shortlisted", "Interviewed", "Offers", "Joined"]
        counts = [applicants, screened, shortlisted, interviewed, offers, joined]
        return _result({
            "Vacancies": vacancies, "Applicants": applicants, "Employees Joined": joined,
            "Hiring Target Attainment (%)": round(100 * min(joined / vacancies, 1), 1) if vacancies else 0,
            "Estimated Time to Fill (days)": round(days, 1),
            "Cost per Hire": round(budget / joined, 2) if joined else 0,
            "Offer Acceptance Rate (%)": round(100 * accepted / offers, 1) if offers else 0,
            "Recruitment Conversion (%)": round(100 * joined / applicants, 1) if applicants else 0,
            "Budget": round(budget, 2),
            "Candidates Within Recruitment Budget": funded_applicants,
        }, [{"Stage": stage, "Count": count} for stage, count in zip(stages, counts)],
           ["Recruitment budget is translated to candidate reach using the stated $100-per-applicant planning assumption; set cost_per_applicant to override it.",
            "The funnel is deterministic: each stage is floored from the prior stage count and configured conversion assumption."])

    if module == "Employee Attrition & Retention":
        initial = int(params["workforce"])
        months = int(params["months"])
        if initial < 0 or months <= 0:
            raise ValueError("Workforce must be non-negative and the simulation horizon must be positive.")
        voluntary, involuntary, retire = (float(params[k]) for k in ("voluntary", "involuntary", "retirement"))
        if min(voluntary, involuntary, retire) < 0 or voluntary + involuntary + retire > 1:
            raise ValueError("Monthly exit probabilities must be non-negative and sum to no more than 1.")
        replacement_hires = int(params["hires"])
        replacement_cost = float(params["replacement_cost"])
        if replacement_hires < 0 or replacement_cost < 0:
            raise ValueError("Replacement hires and cost must be non-negative.")
        original_cohort = initial
        replacement_cohort = 0
        rows = []
        exits_total = voluntary_total = involuntary_total = retirement_total = 0
        exposure = 0
        period_survival = 1.0
        for month in range(1, months + 1):
            opening = original_cohort + replacement_cohort
            exposure += opening
            probabilities = [voluntary, involuntary, retire, 1 - voluntary - involuntary - retire]
            original_moves = rng.multinomial(original_cohort, probabilities)
            replacement_moves = rng.multinomial(replacement_cohort, probabilities)
            voluntary_exits, involuntary_exits, retirement_exits = (
                int(original_moves[index] + replacement_moves[index]) for index in range(3)
            )
            exits = voluntary_exits + involuntary_exits + retirement_exits
            if opening:
                period_survival *= 1 - exits / opening
            original_exits = int(original_moves[:3].sum())
            original_cohort -= original_exits
            replacement_cohort -= int(replacement_moves[:3].sum())
            hires = replacement_hires
            replacement_cohort += hires
            exits_total += exits
            voluntary_total += voluntary_exits
            involuntary_total += involuntary_exits
            retirement_total += retirement_exits
            rows.append({
                "Month": month, "Opening Workforce": opening, "Voluntary Exits": voluntary_exits,
                "Involuntary Exits": involuntary_exits, "Retirement Exits": retirement_exits,
                "Exits": exits, "Hires": hires, "Workforce": original_cohort + replacement_cohort,
                "Original Cohort Remaining": original_cohort,
            })
        final = original_cohort + replacement_cohort
        monthly_rate = exits_total / exposure if exposure else 0
        period_attrition = 1 - period_survival if initial else 0
        return _result({
            "Initial Workforce": initial, "Final Workforce": final, "Total Exits": exits_total,
            "Voluntary Exits": voluntary_total, "Involuntary Exits": involuntary_total,
            "Retirement Exits": retirement_total, "Total Hires": replacement_hires * months,
            "Monthly Attrition Rate (%)": round(100 * monthly_rate, 2),
            "Annualized Attrition Rate (%)": round(100 * (1 - (1 - monthly_rate) ** 12), 2),
            "Period Attrition (%)": round(100 * period_attrition, 2),
            "Original Cohort Retention (%)": round(100 * original_cohort / initial, 2) if initial else 0,
            "Retention Rate (%)": round(100 * original_cohort / initial, 2) if initial else 0,
            "Net Workforce Change": final - initial,
            "Estimated Replacement Cost": round(exits_total * replacement_cost, 2),
        }, rows, [
            "Monthly voluntary, involuntary and retirement exits are mutually exclusive outcomes for each employee; their configured probabilities must sum to at most 1.",
            "Original employees and replacement hires are tracked as separate cohorts. Retention uses original-cohort employees still employed divided by starting workforce.",
            "Monthly attrition uses exits divided by observed workforce employee-month exposure; annualized attrition compounds the average monthly rate.",
        ])

    if module == "Learning & Development":
        employees = int(params["employees"])
        eligibility_rate = float(params.get("eligibility_rate", 1.0))
        if employees < 0 or not 0 <= eligibility_rate <= 1:
            raise ValueError("Employee count must be non-negative and eligibility rate must be between 0 and 1.")
        for key in ("participation", "completion", "pass_rate"):
            if not 0 <= float(params[key]) <= 1:
                raise ValueError(f"{key} must be between 0 and 1.")
        eligible = int(employees * eligibility_rate)
        requested = int(eligible * float(params["participation"]))
        budget = float(params["budget"])
        cost_per_person = float(params["cost_per_person"])
        if budget < 0 or cost_per_person < 0:
            raise ValueError("Training budget and cost per enrollee must be non-negative.")
        enrolled = min(requested, int(budget / cost_per_person)) if cost_per_person else requested
        completed = int(enrolled * float(params["completion"]))
        passed = int(completed * float(params["pass_rate"]))
        cost = enrolled * cost_per_person
        gain = float(params["learning_gain"])
        pre_score = float(params.get("pre_training_score", 60.0))
        value_per_gain = float(params["value_per_gain"])
        if gain < 0 or not 0 <= pre_score <= 100 or value_per_gain < 0:
            raise ValueError("Learning gain and value per gain must be non-negative; pre-training score must be 0–100.")
        post_score = min(100.0, pre_score + gain)
        observed_gain = post_score - pre_score
        benefit = passed * observed_gain * value_per_gain
        roi = 100 * (benefit - cost) / cost if cost else None
        series = [
            {"Stage": stage, "Employees": count}
            for stage, count in (
                ("Eligible", eligible), ("Requested", requested), ("Enrolled", enrolled),
                ("Completed", completed), ("Assessment passes", passed),
            )
        ]
        return _result({
            "Employees": employees, "Training Eligible": eligible, "Requested Enrollments": requested,
            "Enrolled": enrolled, "Completed": completed,
            "Participation Rate (%)": round(100 * requested / eligible, 1) if eligible else 0,
            "Training Completion Rate (%)": round(100 * completed / enrolled, 1) if enrolled else 0,
            "Assessment Passes": passed, "Average Learning Gain (points)": round(gain, 2),
            "Pre-training Score": round(pre_score, 2), "Post-training Score": round(post_score, 2),
            "Learning Improvement (points)": round(observed_gain, 2),
            "Training Cost": round(cost, 2), "Estimated Financial Benefit (assumption-based)": round(benefit, 2),
            "Budget Utilization (%)": round(100 * cost / budget, 1) if budget else 0,
            "Estimated Training ROI (%)": round(roi, 1) if roi is not None else None,
            "Cost per Trainee": round(cost / max(enrolled, 1), 2),
        }, series, [
            "Financial benefit assumes each assessment pass realizes the configured monetary value per score point; it is not evidence that training caused business gains.",
            "Training ROI is undefined when training cost is zero.",
        ])


    if module == "Performance Management":
        employees = int(params["employees"])
        mean = float(params["mean_rating"])
        spread = float(params["rating_spread"])
        effect = float(params["training_effect"])
        reward_budget = float(params["reward_budget"])
        if employees < 0 or not 1 <= mean <= 5 or spread < 0 or effect < 0 or reward_budget < 0:
            raise ValueError("Performance inputs must be non-negative; mean rating must be between 1 and 5.")
        before = np.clip(rng.normal(mean, spread, employees), 1, 5)
        after = np.clip(before + effect, 1, 5)
        counts, _ = np.histogram(after, bins=np.arange(0.5, 6.5, 1))
        improvement = float(after.mean() - before.mean()) if employees else 0.0
        high_performers = int((after >= 4).sum())
        allocated_rewards = reward_budget if high_performers else 0.0
        return _result({
            "Employees": employees, "Baseline Average Performance Score": round(float(before.mean()), 2) if employees else 0,
            "Average Performance Score After Intervention": round(float(after.mean()), 2) if employees else 0,
            "Goal Achievement Rate (%)": round(100 * float((after >= 3).mean()), 1) if employees else 0,
            "High Performer Share (%)": round(100 * float((after >= 4).mean()), 1) if employees else 0,
            "Employees Requiring Support (%)": round(100 * float((after < 2.5).mean()), 1) if employees else 0,
            "Estimated Improvement (points)": round(improvement, 2),
            "Reward Budget": round(reward_budget, 2),
            "Rewards Allocated": round(allocated_rewards, 2),
            "Average Reward per High Performer": round(allocated_rewards / high_performers, 2)
            if high_performers else 0,
        }, [{"Rating": rating, "Employees": int(count)} for rating, count in zip(range(1, 6), counts)],
           [
               "Ratings are sampled from a normal distribution clipped to the 1–5 scale; intervention points are an assumption, not causal evidence.",
               "The reward budget is split equally across simulated employees rated 4 or higher; if there are none, no rewards are allocated.",
           ])

    if module == "Workforce Planning":
        current = int(params["workforce"])
        demand = float(params["demand"])
        months = int(params["months"])
        productivity = float(params["productivity"])
        turnover = float(params["turnover"])
        growth = float(params["growth"])
        monthly_cost = float(params["monthly_cost"])
        if current < 0 or demand < 0 or months <= 0:
            raise ValueError("Workforce and demand must be non-negative and forecast horizon must be positive.")
        if productivity <= 0 or not 0 <= turnover <= 1 or growth < -1 or monthly_cost < 0:
            raise ValueError("Productivity and cost must be non-negative, turnover must be 0–1, and demand growth must exceed -100%.")
        rows = []
        total_labour_cost = 0.0
        for month in range(1, months + 1):
            expected_supply = max(0, round(current * ((1 - turnover) ** (month - 1))))
            expected_workload = demand * ((1 + growth) ** (month - 1))
            required_fte = expected_workload / productivity
            effective_capacity = expected_supply * productivity
            gap = required_fte - expected_supply
            month_cost = expected_supply * monthly_cost
            total_labour_cost += month_cost
            rows.append({
                "Month": month, "Workforce Supply": expected_supply,
                "Forecast Workload (standard FTE units)": round(expected_workload, 2),
                "Required FTE": round(required_fte, 2),
                "Effective Capacity (workload units)": round(effective_capacity, 2),
                "Workforce Gap (required FTE - available FTE)": round(gap, 2),
                "Monthly Labour Cost": round(month_cost, 2),
            })
        final = rows[-1]
        final_gap = final["Workforce Gap (required FTE - available FTE)"]
        return _result({
            "Current Workforce": current, "Forecast Workload (standard FTE units)": final["Forecast Workload (standard FTE units)"],
            "Required FTE": final["Required FTE"], "Forecast Workforce Supply": final["Workforce Supply"],
            "Effective Capacity (workload units)": final["Effective Capacity (workload units)"],
            "Workforce Gap": round(final_gap, 2),
            "Hiring Requirement": max(0, int(np.ceil(final_gap))),
            "Workforce Utilization (%)": round(100 * final["Forecast Workload (standard FTE units)"]
                                               / max(final["Effective Capacity (workload units)"], 1e-12), 1),
            "Estimated Labour Cost": round(total_labour_cost, 2),
            "Productivity Index": round(productivity * 100, 1),
        }, rows, [
            "Demand is expressed as standard-workload FTE at productivity index 1.0. Required FTE equals workload divided by the productivity index.",
            "Labour cost is the sum of each forecast month's workforce supply multiplied by monthly cost per employee.",
        ])

    if module == "Compensation & Benefits":
        count = int(params["employees"])
        salary, spread = float(params["salary"]), float(params["spread"])
        increment_rate, bonus_rate, benefit_rate = (
            float(params[key]) for key in ("increment", "bonus", "benefits")
        )
        if count < 0 or salary <= 0 or spread < 0 or min(increment_rate, bonus_rate, benefit_rate) < 0:
            raise ValueError("Employee count and compensation rates must be non-negative; average salary must be positive.")
        salaries = rng.normal(salary, spread, count).clip(20000, 300000)
        increment = salaries * increment_rate
        bonus = salaries * bonus_rate
        benefits = salaries * benefit_rate
        total = salaries + increment + bonus + benefits
        return _result({
            "Employees": count, "Average Salary": round(float(salaries.mean()), 2) if count else 0,
            "Base Payroll": round(float(salaries.sum()), 2), "Increment Cost": round(float(increment.sum()), 2),
            "Bonus Cost": round(float(bonus.sum()), 2), "Benefits Cost": round(float(benefits.sum()), 2),
            "Total Compensation Cost": round(float(total.sum()), 2),
            "Compensation Increase (%)": round(100 * (float(total.sum()) / max(1, float(salaries.sum())) - 1), 1) if count else 0,
        }, [{"Salary": round(float(salary), 2)} for salary in salaries], [
            "Base salaries are sampled from a normal distribution and clipped to 20,000–300,000 in the same currency units as the salary input.",
            "Increments, variable pay and benefits are modeled as fixed proportions of simulated base salary.",
        ])

    employees = int(params["employees"])
    grievance_rate = float(params["grievance_rate"])
    capacity = int(params["capacity"])
    resolution_days = float(params["resolution_days"])
    period_days = float(params.get("period_days", 30.0))
    sla_days = float(params.get("sla_days", 30.0))
    if employees < 0 or grievance_rate < 0 or capacity <= 0 or resolution_days <= 0:
        raise ValueError("Employee count and grievance rate must be non-negative; capacity and service time must be positive.")
    if period_days <= 0 or sla_days <= 0:
        raise ValueError("Observation period and SLA deadline must be positive.")
    specified_grievances = params.get("total_grievances")
    grievances = (int(rng.poisson(employees * grievance_rate))
                  if specified_grievances is None else int(specified_grievances))
    if grievances < 0:
        raise ValueError("Total grievance count must be non-negative.")
    env = simpy.Environment()
    investigators = simpy.Resource(env, capacity=capacity)
    categories = ["Workload", "Communication", "Policy", "Management", "Other"]
    cases = []
    for case_id in range(grievances):
        cases.append({
            "id": case_id,
            "arrival": float(rng.uniform(0, period_days)),
            "category": str(rng.choice(categories, p=[0.28, 0.22, 0.2, 0.18, 0.12])),
            "service": max(0.01, float(rng.exponential(resolution_days))),
            "start": None,
            "resolved": None,
        })
    event_log = []

    def investigate(case):
        yield env.timeout(case["arrival"])
        event_log.append({"time": env.now, "type": "submitted", "id": case["id"],
                          "category": case["category"]})
        with investigators.request() as request:
            yield request
            case["start"] = float(env.now)
            event_log.append({"time": env.now, "type": "investigation_started", "id": case["id"]})
            yield env.timeout(case["service"])
            case["resolved"] = float(env.now)
            event_log.append({"time": env.now, "type": "resolved", "id": case["id"],
                              "duration": case["service"]})

    for case in cases:
        env.process(investigate(case))
    env.run(until=period_days)
    resolved_cases = [case for case in cases if case["resolved"] is not None]
    open_cases = [case for case in cases if case["resolved"] is None]
    waits = [
        (case["start"] if case["start"] is not None else period_days) - case["arrival"]
        for case in cases
    ]
    avg_wait = float(np.mean(waits)) if waits else 0.0
    avg_resolution = float(np.mean([case["resolved"] - case["arrival"] for case in resolved_cases])) if resolved_cases else None
    on_time = sum(case["resolved"] - case["arrival"] <= sla_days for case in resolved_cases)
    busy_time = sum(
        max(0.0, min(period_days, case["resolved"] if case["resolved"] is not None
                     else (case["start"] + case["service"] if case["start"] is not None else period_days))
            - case["start"]) if case["start"] is not None else 0.0
        for case in cases
    )
    category_counts = {category: sum(case["category"] == category for case in cases)
                       for category in categories}
    return _result({
        "Employees": employees, "Total Grievances": grievances,
        "Grievances Resolved": len(resolved_cases), "Resolved in Period": len(resolved_cases),
        "Open Grievances": len(open_cases), "Pending Grievances": len(open_cases),
        "Average Waiting Time (days)": round(avg_wait, 2),
        "Average Resolution Time (days)": round(avg_resolution, 2) if avg_resolution is not None else None,
        "Resolution Rate (%)": round(100 * len(resolved_cases) / grievances, 1) if grievances else 0,
        "SLA Compliance (%)": round(100 * on_time / len(resolved_cases), 1) if resolved_cases else 0,
        "Investigator Utilization (%)": round(100 * busy_time / (capacity * period_days), 1),
    }, [{"Category": category, "Grievances": int(category_counts[category])} for category in categories],
       [
           f"Cases arrive according to a Poisson process over {period_days:g} days; each investigator serves one case at a time with exponentially distributed service time (mean {resolution_days:g} days).",
           f"FIFO queue; pending cases at day {period_days:g} remain open. SLA compliance is the share of resolved cases completed within {sla_days:g} days of arrival.",
           "Investigator utilization is observed busy time within the observation period divided by available investigator time.",
       ])


def run_monte_carlo(module: str, params: dict, iterations: int = 100, seed: int = 42) -> dict:
    """Summarize stochastic-output variation; percentiles are simulation intervals, not CIs."""
    if module not in STOCHASTIC_MODULES:
        raise ValueError(f"Monte Carlo uncertainty analysis is not defined for deterministic module: {module}.")
    if not 1 <= int(iterations) <= 1000:
        raise ValueError("Monte Carlo iterations must be between 1 and 1000.")
    collected: dict[str, list[float]] = {}
    for iteration in range(int(iterations)):
        result = run_simulation(module, params, seed=int(seed) + iteration)
        for row in result["kpis"]:
            value = row["Value"]
            if isinstance(value, (int, float, np.number)) and value is not None:
                collected.setdefault(row["KPI"], []).append(float(value))
    summaries = []
    for metric, samples in collected.items():
        values = np.asarray(samples, dtype=float)
        summaries.append({
            "KPI": metric,
            "Mean": round(float(values.mean()), 4),
            "Median": round(float(np.median(values)), 4),
            "Standard Deviation": round(float(values.std()), 4),
            "5th Percentile": round(float(np.percentile(values, 5)), 4),
            "95th Percentile": round(float(np.percentile(values, 95)), 4),
        })
    return {
        "module": module,
        "iterations": int(iterations),
        "seed": int(seed),
        "interval_label": "5th–95th simulation percentile interval (not a statistical confidence interval)",
        "summaries": summaries,
    }


def run_sensitivity_analysis(module: str, params: dict, seed: int = 42) -> dict:
    """Run one-at-a-time positive input perturbations with a fixed seed."""
    if module not in MODULES:
        raise ValueError(f"Unknown HR simulation module: {module}")
    baseline = run_simulation(module, params, seed)
    target_kpi = SENSITIVITY_OUTPUTS[module]
    baseline_value = next(row["Value"] for row in baseline["kpis"] if row["KPI"] == target_kpi)
    if baseline_value is None:
        return {"module": module, "target_kpi": target_kpi, "results": []}
    probability_inputs = {
        "screen_rate", "shortlist_rate", "dropout_rate", "offer_rate", "acceptance_rate",
        "joining_rate", "voluntary", "involuntary", "retirement", "participation",
        "eligibility_rate", "completion", "pass_rate", "turnover", "grievance_rate",
    }
    results = []
    for parameter, current in params.items():
        if isinstance(current, bool) or not isinstance(current, (int, float, np.number)):
            continue
        value = float(current)
        increase = max(abs(value) * 0.1, 0.01 if parameter in probability_inputs else 1.0)
        changed = value + increase
        if parameter in probability_inputs:
            changed = min(1.0, changed)
        if parameter == "growth":
            changed = min(0.2, changed)
        if changed == value:
            continue
        changed_params = dict(params)
        changed_params[parameter] = int(changed) if isinstance(current, (int, np.integer)) else changed
        try:
            changed_result = run_simulation(module, changed_params, seed)
        except ValueError:
            continue
        changed_value = next(row["Value"] for row in changed_result["kpis"] if row["KPI"] == target_kpi)
        if changed_value is None:
            continue
        difference = float(changed_value) - float(baseline_value)
        results.append({
            "Input": parameter,
            "Baseline": float(value),
            "Perturbed": float(changed_params[parameter]),
            "Output change": round(difference, 4),
            "Output change (%)": round(100 * difference / abs(float(baseline_value)), 2)
            if baseline_value else None,
        })
    results.sort(key=lambda row: abs(row["Output change"]), reverse=True)
    return {"module": module, "target_kpi": target_kpi, "results": results}
