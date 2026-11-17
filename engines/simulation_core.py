"""Reproducible, educational HR simulation calculations."""

from __future__ import annotations

import numpy as np


MODULES = {
    "Recruitment & Talent Acquisition": "recruitment",
    "Employee Attrition & Retention": "attrition",
    "Learning & Development": "learning",
    "Performance Management": "performance",
    "Workforce Planning": "workforce",
    "Compensation & Benefits": "compensation",
    "Employee Relations": "employee_relations",
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
        applicants = max(0, int(params["applicants"]))
        budget = float(params["budget"])
        funding_factor = budget / (budget + max(1, int(params["vacancies"])) * 100)
        screening_capacity = int(params.get("screen_capacity", applicants)) * max(1, int(params["recruiters"]))
        screened = min(applicants, int(applicants * params["screen_rate"] * funding_factor), screening_capacity)
        shortlisted = int(screened * params["shortlist_rate"])
        interviewed = int(shortlisted * (1 - params["dropout_rate"]))
        offers = int(interviewed * params["offer_rate"])
        accepted = int(offers * params["acceptance_rate"])
        joined = min(int(params["vacancies"]), int(accepted * params["joining_rate"]))
        recruiters = max(1, int(params["recruiters"]))
        days = (screened * float(params["screen_days"]) / recruiters
                + interviewed * float(params["interview_days"]) / max(1, int(params["interviewers"])))
        stages = ["Applicants", "Screened", "Shortlisted", "Interviewed", "Offers", "Joined"]
        counts = [applicants, screened, shortlisted, interviewed, offers, joined]
        return _result({
            "Vacancies": int(params["vacancies"]), "Applicants": applicants, "Employees Joined": joined,
            "Hiring Target Attainment (%)": round(100 * min(joined / max(1, int(params["vacancies"])), 1), 1),
            "Estimated Time to Fill (days)": round(days, 1),
            "Cost per Hire": round(budget / joined, 2) if joined else 0,
            "Offer Acceptance Rate (%)": round(100 * accepted / offers, 1) if offers else 0,
            "Recruitment Conversion (%)": round(100 * joined / applicants, 1) if applicants else 0,
            "Budget": round(budget, 2),
        }, [{"Stage": stage, "Count": count} for stage, count in zip(stages, counts)])

    if module == "Employee Attrition & Retention":
        initial = max(0, int(params["workforce"]))
        months = max(1, int(params["months"]))
        voluntary, involuntary, retire = (float(params[k]) for k in ("voluntary", "involuntary", "retirement"))
        team = initial
        rows = []
        exits_total = voluntary_total = 0
        replacement_cost = float(params["replacement_cost"])
        for month in range(1, months + 1):
            total_exit_rate = voluntary + involuntary + retire
            exits = rng.binomial(team, min(max(total_exit_rate, 0), 1))
            voluntary_exits = rng.binomial(exits, voluntary / total_exit_rate) if total_exit_rate else 0
            hires = min(int(params["hires"]), max(0, initial * 2 - team + exits))
            team = max(0, team - exits + hires)
            exits_total += exits
            voluntary_total += voluntary_exits
            rows.append({"Month": month, "Workforce": team, "Exits": exits, "Hires": hires})
        avg_workforce = max(1, (initial + team) / 2)
        monthly_rate = exits_total / (avg_workforce * months)
        return _result({
            "Initial Workforce": initial, "Final Workforce": team, "Total Exits": exits_total,
            "Voluntary Exits": voluntary_total, "Monthly Attrition Rate (%)": round(100 * monthly_rate, 2),
            "Annualized Attrition Rate (%)": round(100 * (1 - (1 - monthly_rate) ** 12), 2),
            "Retention Rate (%)": round(100 * max(0, 1 - monthly_rate), 2),
            "Estimated Replacement Cost": round(exits_total * replacement_cost, 2),
        }, rows)

    if module == "Learning & Development":
        employees = max(0, int(params["employees"]))
        requested = int(employees * float(params["participation"]))
        budget = max(0, float(params["budget"]))
        cost_per_person = max(0, float(params["cost_per_person"]))
        enrolled = min(requested, int(budget / cost_per_person)) if cost_per_person else requested
        completed = int(enrolled * float(params["completion"]))
        passed = int(completed * float(params["pass_rate"]))
        cost = enrolled * cost_per_person
        gain = float(params["learning_gain"])
        benefit = passed * gain * float(params["value_per_gain"])
        methods = ["Classroom", "E-learning", "Blended", "On-the-job"]
        factors = [0.92, 0.88, 1.0, 0.96]
        series = [{"Method": method, "Completion (%)": round(float(np.clip(params["completion"] * factor, 0, 1)) * 100, 1)}
                  for method, factor in zip(methods, factors)]
        return _result({
            "Employees": employees, "Requested Enrollments": requested, "Enrolled": enrolled, "Completed": completed,
            "Training Completion Rate (%)": round(100 * completed / enrolled, 1) if enrolled else 0,
            "Assessment Passes": passed, "Average Learning Gain (points)": round(gain, 2),
            "Training Cost": round(cost, 2), "Budget Utilization (%)": round(100 * cost / budget, 1) if budget else 0,
            "Estimated Training ROI (%)": round(100 * (benefit - cost) / cost, 1) if cost else 0,
            "Cost per Trainee": round(cost / max(enrolled, 1), 2),
        }, series)

    if module == "Performance Management":
        employees = max(0, int(params["employees"]))
        mean = float(params["mean_rating"])
        before = np.clip(rng.normal(mean, float(params["rating_spread"]), employees), 1, 5)
        after = np.clip(before + float(params["training_effect"]), 1, 5)
        counts, _ = np.histogram(after, bins=np.arange(0.5, 6.5, 1))
        improvement = float(params["training_effect"])
        return _result({
            "Employees": employees, "Baseline Average Performance Score": round(float(before.mean()), 2) if employees else 0,
            "Average Performance Score After Intervention": round(float(after.mean()), 2) if employees else 0,
            "Goal Achievement Rate (%)": round(100 * float((after >= 3).mean()), 1) if employees else 0,
            "High Performer Share (%)": round(100 * float((after >= 4).mean()), 1) if employees else 0,
            "Employees Requiring Support (%)": round(100 * float((after < 2.5).mean()), 1) if employees else 0,
            "Estimated Improvement (points)": round(improvement, 2),
            "Reward Budget": round(float(params["reward_budget"]), 2),
        }, [{"Rating": rating, "Employees": int(count)} for rating, count in zip(range(1, 6), counts)])

    if module == "Workforce Planning":
        current = max(0, int(params["workforce"]))
        demand = max(0, int(params["demand"]))
        months = max(1, int(params["months"]))
        productivity = max(0.05, float(params["productivity"]))
        turnover = max(0, float(params["turnover"]))
        rows = []
        for month in range(1, months + 1):
            expected_supply = max(0, round(current * ((1 - turnover) ** (month - 1))))
            expected_demand = round(demand * (1 + float(params["growth"])) ** (month - 1))
            rows.append({"Month": month, "Workforce Supply": expected_supply,
                         "Workforce Demand": expected_demand, "Gap": expected_supply - expected_demand})
        final = rows[-1]
        return _result({
            "Current Workforce": current, "Forecast Workforce Demand": final["Workforce Demand"],
            "Forecast Workforce Supply": final["Workforce Supply"],
            "Workforce Gap": final["Workforce Supply"] - final["Workforce Demand"],
            "Hiring Requirement": max(0, final["Workforce Demand"] - final["Workforce Supply"]),
            "Workforce Utilization (%)": round(100 * min(final["Workforce Demand"] / max(1, final["Workforce Supply"]), 1), 1),
            "Estimated Labour Cost": round(final["Workforce Supply"] * float(params["monthly_cost"]) * months, 2),
            "Productivity Index": round(productivity * 100, 1),
        }, rows)

    if module == "Compensation & Benefits":
        count = max(0, int(params["employees"]))
        salaries = rng.normal(float(params["salary"]), float(params["spread"]), count).clip(20000, 300000)
        increment = salaries * float(params["increment"])
        bonus = salaries * float(params["bonus"])
        benefits = salaries * float(params["benefits"])
        total = salaries + increment + bonus + benefits
        return _result({
            "Employees": count, "Average Salary": round(float(salaries.mean()), 2) if count else 0,
            "Base Payroll": round(float(salaries.sum()), 2), "Increment Cost": round(float(increment.sum()), 2),
            "Bonus Cost": round(float(bonus.sum()), 2), "Benefits Cost": round(float(benefits.sum()), 2),
            "Total Compensation Cost": round(float(total.sum()), 2),
            "Compensation Increase (%)": round(100 * (float(total.sum()) / max(1, float(salaries.sum())) - 1), 1) if count else 0,
        }, [{"Salary": round(float(salary), 2)} for salary in salaries])

    employees = max(0, int(params["employees"]))
    grievances = int(rng.poisson(employees * float(params["grievance_rate"])))
    capacity = max(1, int(params["capacity"]))
    resolution_days = max(1, float(params["resolution_days"]))
    resolved = min(grievances, int(capacity * 30 / resolution_days))
    categories = ["Workload", "Communication", "Policy", "Management", "Other"]
    category_counts = rng.multinomial(grievances, [0.28, 0.22, 0.2, 0.18, 0.12]) if grievances else np.zeros(5, dtype=int)
    return _result({
        "Employees": employees, "Total Grievances": grievances, "Resolved in Period": resolved,
        "Pending Grievances": grievances - resolved,
        "Resolution Rate (%)": round(100 * resolved / grievances, 1) if grievances else 100,
        "Average Resolution Time (days)": round(resolution_days, 1),
        "Illustrative Satisfaction Index": round(max(0, 100 - min(100, (grievances - resolved) * 1.5)), 1),
    }, [{"Category": category, "Grievances": int(count)} for category, count in zip(categories, category_counts)])
