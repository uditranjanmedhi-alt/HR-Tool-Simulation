import unittest

import numpy as np

from data.upload_pipeline import DEFAULT_SIMULATION_PARAMS
from engines.simulation_core import (
    MODULES,
    run_monte_carlo,
    run_sensitivity_analysis,
    run_simulation,
)


class SimulationCoreTests(unittest.TestCase):
    def test_all_modules_return_kpis_and_chart_data(self):
        examples = {
            "Recruitment & Talent Acquisition": {
                "vacancies": 10, "applicants": 200, "recruiters": 2, "interviewers": 4,
                "budget": 10000, "screen_rate": .8, "shortlist_rate": .4, "dropout_rate": .1,
                "offer_rate": .8, "acceptance_rate": .7, "joining_rate": .9,
                "screen_days": .5, "interview_days": 1,
            },
            "Employee Attrition & Retention": {
                "workforce": 100, "months": 12, "voluntary": .02, "involuntary": .005,
                "retirement": .002, "hires": 4, "replacement_cost": 5000,
            },
            "Learning & Development": {
                "employees": 100, "budget": 10000, "cost_per_person": 100, "participation": .8,
                "completion": .75, "pass_rate": .8, "learning_gain": 1, "value_per_gain": 100,
            },
            "Performance Management": {
                "employees": 100, "mean_rating": 3, "rating_spread": .8,
                "training_effect": .2, "reward_budget": 10000,
            },
            "Workforce Planning": {
                "workforce": 100, "demand": 110, "months": 12, "growth": .01,
                "turnover": .01, "productivity": 1, "monthly_cost": 3000,
            },
            "Compensation & Benefits": {
                "employees": 100, "salary": 60000, "spread": 12000,
                "increment": .04, "bonus": .05, "benefits": .1,
            },
            "Employee Relations": {
                "employees": 100, "grievance_rate": .03, "capacity": 5, "resolution_days": 10,
            },
        }
        self.assertEqual(set(examples), set(MODULES))
        for module, params in examples.items():
            with self.subTest(module=module):
                result = run_simulation(module, params, seed=7)
                self.assertGreater(len(result["kpis"]), 0)
                self.assertGreater(len(result["series"]), 0)

    def test_simulation_is_reproducible_and_sensitive_to_inputs(self):
        params = {"employees": 100, "salary": 60000, "spread": 12000,
                  "increment": .04, "bonus": .05, "benefits": .1}
        first = run_simulation("Compensation & Benefits", params, seed=10)
        repeat = run_simulation("Compensation & Benefits", params, seed=10)
        higher = run_simulation("Compensation & Benefits", {**params, "increment": .08}, seed=10)
        self.assertEqual(first["kpis"], repeat["kpis"])
        values = {row["KPI"]: row["Value"] for row in first["kpis"]}
        higher_values = {row["KPI"]: row["Value"] for row in higher["kpis"]}
        self.assertGreater(higher_values["Total Compensation Cost (INR/year)"],
                           values["Total Compensation Cost (INR/year)"])
        self.assertAlmostEqual(
            values["Compensation Increase (%)"],
            100 * (values["Total Compensation Cost (INR/year)"] / values["Base Payroll (INR/year)"] - 1),
            places=1,
        )
        self.assertAlmostEqual(
            values["Total Compensation Cost (INR/year)"],
            values["Base Payroll (INR/year)"] + values["Increment Cost (INR/year)"]
            + values["Bonus Cost (INR/year)"] + values["Benefits Cost (INR/year)"],
            places=1,
        )

    def test_budget_and_development_inputs_change_simulated_outputs(self):
        recruitment = {
            "vacancies": 20, "applicants": 500, "recruiters": 2, "interviewers": 4,
            "budget": 1000, "screen_rate": .8, "shortlist_rate": .4, "dropout_rate": .1,
            "offer_rate": .8, "acceptance_rate": .7, "joining_rate": .9,
            "screen_days": .5, "interview_days": 1,
        }
        low_budget = run_simulation("Recruitment & Talent Acquisition", recruitment, seed=3)
        high_budget = run_simulation("Recruitment & Talent Acquisition", {**recruitment, "budget": 50000}, seed=3)
        self.assertGreater(high_budget["series"][1]["Count"], low_budget["series"][1]["Count"])

        overfilled = run_simulation("Recruitment & Talent Acquisition", {
            **recruitment, "vacancies": 10, "budget": 1000000,
            "screen_rate": 1, "shortlist_rate": 1, "dropout_rate": 0,
            "offer_rate": 1, "acceptance_rate": 1, "joining_rate": 1,
        }, seed=3)
        self.assertEqual(overfilled["series"][-1]["Count"], 10)
        self.assertEqual({row["KPI"]: row["Value"] for row in overfilled["kpis"]}["Employees Joined"], 10)

        performance = {"employees": 200, "mean_rating": 2.8, "rating_spread": .8,
                       "training_effect": 0, "reward_budget": 10000}
        baseline = run_simulation("Performance Management", performance, seed=5)
        improved = run_simulation("Performance Management", {**performance, "training_effect": .5}, seed=5)
        baseline_kpis = {row["KPI"]: row["Value"] for row in baseline["kpis"]}
        improved_kpis = {row["KPI"]: row["Value"] for row in improved["kpis"]}
        self.assertGreater(improved_kpis["Average Performance Score After Intervention"],
                           baseline_kpis["Average Performance Score After Intervention"])
        high_performers = round(baseline_kpis["High Performer Share (%)"] * performance["employees"] / 100)
        expected_rewards = performance["reward_budget"] if high_performers else 0
        self.assertEqual(baseline_kpis["Rewards Allocated (INR)"], expected_rewards)
        self.assertEqual(
            baseline_kpis["Average Reward per High Performer (INR)"],
            round(expected_rewards / high_performers, 2) if high_performers else 0,
        )
        self.assertTrue(any("do not establish" in note for note in baseline["notes"]))

    def test_recruitment_cost_per_hire_uses_estimated_spend_and_effort_units(self):
        params = {
            "vacancies": 20, "applicants": 5, "recruiters": 2, "interviewers": 2,
            "budget": 250, "cost_per_applicant": 100, "screen_rate": 1,
            "shortlist_rate": 1, "dropout_rate": 0, "offer_rate": 1,
            "acceptance_rate": 1, "joining_rate": 1, "screen_capacity": 10,
            "screen_days": .5, "interview_days": 1,
        }
        result = run_simulation("Recruitment & Talent Acquisition", params, seed=3)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        self.assertEqual(values["Candidates Within Recruitment Budget"], 2)
        self.assertEqual(values["Estimated Recruitment Spend (INR)"], 200)
        self.assertEqual(values["Cost per Hire (INR/hire)"], 100)
        self.assertEqual(values["Estimated Recruitment Processing Effort (person-days)"], 3)

        no_hires = run_simulation(
            "Recruitment & Talent Acquisition", {**params, "joining_rate": 0}, seed=3,
        )
        no_hire_values = {row["KPI"]: row["Value"] for row in no_hires["kpis"]}
        self.assertEqual(no_hire_values["Estimated Recruitment Spend (INR)"], 200)
        self.assertIsNone(no_hire_values["Cost per Hire (INR/hire)"])

    def test_recruitment_cost_per_hire_uses_unrounded_estimated_spend(self):
        result = run_simulation("Recruitment & Talent Acquisition", {
            "vacancies": 2, "applicants": 2, "recruiters": 1, "interviewers": 1,
            "screen_capacity": 2, "interview_capacity": 2, "budget": 2.02,
            "cost_per_applicant": 1.0051, "screen_rate": 1, "shortlist_rate": 1,
            "dropout_rate": 0, "offer_rate": 1, "acceptance_rate": 1,
            "joining_rate": 1, "screen_days": 0, "interview_days": 0,
        }, seed=3)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        self.assertEqual(values["Estimated Recruitment Spend (INR)"], 2.01)
        self.assertEqual(values["Cost per Hire (INR/hire)"], 1.01)

    def test_interviewer_capacity_limits_recruitment_funnel(self):
        params = {
            "vacancies": 20, "applicants": 20, "recruiters": 2, "interviewers": 2,
            "screen_capacity": 20, "interview_capacity": 3, "budget": 2000,
            "screen_rate": 1, "shortlist_rate": 1, "dropout_rate": 0,
            "offer_rate": 1, "acceptance_rate": 1, "joining_rate": 1,
            "screen_days": .5, "interview_days": 1,
        }
        result = run_simulation("Recruitment & Talent Acquisition", params, seed=3)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        self.assertEqual(values["Employees Joined"], 6)
        self.assertEqual(result["series"][3]["Count"], 6)
        self.assertTrue(any("scenario interview capacity (6)" in note for note in result["notes"]))

    def test_invalid_module_is_rejected(self):
        with self.assertRaises(ValueError):
            run_simulation("not a module", {}, seed=1)
        with self.assertRaisesRegex(ValueError, "whole number"):
            run_simulation("Recruitment & Talent Acquisition", {
                "vacancies": 1.5, "applicants": 2, "recruiters": 1, "interviewers": 1,
                "budget": 100, "screen_rate": 1, "shortlist_rate": 1, "dropout_rate": 0,
                "offer_rate": 1, "acceptance_rate": 1, "joining_rate": 1,
                "screen_days": 0, "interview_days": 0,
            }, seed=1)

    def test_attrition_tracks_original_cohort_separately_from_replacement_hires(self):
        params = {
            "workforce": 10, "months": 1, "voluntary": 1.0, "involuntary": 0.0,
            "retirement": 0.0, "hires": 3, "replacement_cost": 100,
        }
        result = run_simulation("Employee Attrition & Retention", params, seed=2)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        self.assertEqual(values["Original Cohort Retention (%)"], 0)
        self.assertEqual(values["Final Workforce"], 3)
        self.assertEqual(values["Total Hires"], 3)
        self.assertEqual(values["Net Workforce Change"], -7)
        self.assertEqual(values["Original Cohort Exits"], 10)
        self.assertEqual(values["Period Workforce Attrition (%)"], 100)
        self.assertNotIn("Retention Rate (%)", values)
        for month in result["series"]:
            self.assertEqual(
                month["Opening Workforce"] + month["Hires"] - month["Exits"],
                month["Workforce"],
            )
            self.assertEqual(
                month["Voluntary Exits"] + month["Involuntary Exits"] + month["Retirement Exits"],
                month["Exits"],
            )
            self.assertEqual(month["Original Cohort Exits"] + month["Original Cohort Remaining"],
                             10 if month["Month"] == 1 else result["series"][month["Month"] - 2]["Original Cohort Remaining"])

    def test_attrition_rate_denominators_are_distinct_and_exposure_based(self):
        params = {
            "workforce": 100, "months": 6, "voluntary": .03, "involuntary": .01,
            "retirement": .005, "hires": 4, "replacement_cost": 100,
        }
        result = run_simulation("Employee Attrition & Retention", params, seed=19)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        exposure = sum(row["Opening Workforce"] for row in result["series"])
        exits = sum(row["Exits"] for row in result["series"])
        period_survival = 1.0
        for row in result["series"]:
            if row["Opening Workforce"]:
                period_survival *= 1 - row["Exits"] / row["Opening Workforce"]
        original_exits = sum(row["Original Cohort Exits"] for row in result["series"])
        original_remaining = result["series"][-1]["Original Cohort Remaining"]
        self.assertAlmostEqual(values["Monthly Attrition Rate (%)"], 100 * exits / exposure, places=2)
        monthly_rate = exits / exposure
        self.assertAlmostEqual(
            values["Annualized Attrition Rate (%)"],
            100 * (1 - (1 - monthly_rate) ** 12),
            places=2,
        )
        self.assertAlmostEqual(values["Period Workforce Attrition (%)"], 100 * (1 - period_survival), places=2)
        self.assertEqual(values["Original Cohort Exits"], original_exits)
        self.assertEqual(original_exits + original_remaining, params["workforce"])
        self.assertAlmostEqual(
            values["Original Cohort Retention (%)"],
            100 * original_remaining / params["workforce"],
            places=2,
        )
        zero_start = run_simulation("Employee Attrition & Retention", {
            "workforce": 0, "months": 2, "voluntary": 1, "involuntary": 0,
            "retirement": 0, "hires": 3, "replacement_cost": 0,
        }, seed=1)
        zero_start_values = {row["KPI"]: row["Value"] for row in zero_start["kpis"]}
        self.assertEqual(zero_start_values["Original Cohort Exits"], 0)
        self.assertEqual(zero_start_values["Original Cohort Retention (%)"], 0)
        self.assertEqual(zero_start_values["Period Workforce Attrition (%)"], 100)

    def test_workforce_productivity_and_cumulative_monthly_cost(self):
        params = {
            "workforce": 10, "demand": 12, "months": 3, "growth": 0, "turnover": 0,
            "productivity": 2, "monthly_cost": 100,
        }
        result = run_simulation("Workforce Planning", params, seed=1)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        self.assertEqual(values["Required FTE"], 6)
        self.assertEqual(values["Workforce Gap"], -4)
        self.assertEqual(values["Estimated Labour Cost (INR over horizon)"], 3000)
        self.assertEqual(sum(row["Monthly Labour Cost"] for row in result["series"]), 3000)
        lower_productivity = run_simulation(
            "Workforce Planning", {**params, "productivity": 1}, seed=1
        )
        lower_values = {row["KPI"]: row["Value"] for row in lower_productivity["kpis"]}
        self.assertEqual(lower_values["Required FTE"], 12)
        self.assertEqual(lower_values["Workforce Gap"], 2)

        near_shortage = run_simulation("Workforce Planning", {
            "workforce": 10, "demand": 10.001, "months": 1, "growth": 0,
            "turnover": 0, "productivity": 1, "monthly_cost": 0,
        }, seed=1)
        near_values = {row["KPI"]: row["Value"] for row in near_shortage["kpis"]}
        self.assertEqual(near_values["Workforce Gap"], 0.001)
        self.assertEqual(near_values["Hiring Requirement"], 1)

        no_supply = run_simulation("Workforce Planning", {
            "workforce": 0, "demand": 10, "months": 1, "growth": 0,
            "turnover": 0, "productivity": 1, "monthly_cost": 0,
        }, seed=1)
        no_supply_values = {row["KPI"]: row["Value"] for row in no_supply["kpis"]}
        self.assertIsNone(no_supply_values["Workforce Utilization (%)"])
        self.assertEqual(no_supply_values["Hiring Requirement"], 10)

    def test_learning_roi_uses_post_minus_pre_scores_and_handles_zero_cost(self):
        params = {
            "employees": 100, "eligibility_rate": .5, "participation": .5, "budget": 1000,
            "cost_per_person": 10, "completion": .8, "pass_rate": .5, "learning_gain": 10,
            "pre_training_score": 50, "value_per_gain": 20,
        }
        result = run_simulation("Learning & Development", params, seed=1)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        self.assertEqual(values["Training Eligible"], 50)
        self.assertEqual(values["Enrolled"], 25)
        self.assertEqual(values["Completed"], 20)
        self.assertEqual(values["Assessment Passes"], 10)
        self.assertEqual(values["Post-training Score"], 60)
        self.assertEqual(values["Estimated Financial Benefit (INR, assumption-based)"], 2000)
        self.assertEqual(values["Estimated Training ROI (%)"], 700)

        free_training = run_simulation(
            "Learning & Development", {**params, "cost_per_person": 0}, seed=1
        )
        free_values = {row["KPI"]: row["Value"] for row in free_training["kpis"]}
        self.assertIsNone(free_values["Estimated Training ROI (%)"])

        capped_gain = run_simulation("Learning & Development", {
            **params, "employees": 1, "eligibility_rate": 1, "participation": 1,
            "completion": 1, "pass_rate": 1, "budget": 10, "cost_per_person": 1,
            "learning_gain": 5, "pre_training_score": 99, "value_per_gain": 10,
        }, seed=1)
        capped_values = {row["KPI"]: row["Value"] for row in capped_gain["kpis"]}
        self.assertEqual(capped_values["Average Learning Gain (points)"], 1)
        self.assertEqual(capped_values["Estimated Financial Benefit (INR, assumption-based)"], 10)

    def test_employee_relations_queue_conserves_cases_and_is_reproducible(self):
        params = {
            "employees": 0, "grievance_rate": .03, "capacity": 2,
            "resolution_days": 5, "period_days": 30, "sla_days": 10,
        }
        empty = run_simulation("Employee Relations", params, seed=9)
        empty_values = {row["KPI"]: row["Value"] for row in empty["kpis"]}
        self.assertEqual(empty_values["Total Grievances"], 0)
        self.assertEqual(empty_values["Cases Unresolved"], 0)
        self.assertEqual(empty_values["Resolution Rate (%)"], 0)
        self.assertIsNone(empty_values["SLA Compliance (%)"])
        self.assertEqual(empty_values["SLA Compliance Denominator"], 0)

        queued = run_simulation(
            "Employee Relations",
            {**params, "employees": 100, "total_grievances": 4,
             "capacity": 1, "resolution_days": .01, "sla_days": 30},
            seed=9,
        )
        repeated = run_simulation(
            "Employee Relations",
            {**params, "employees": 100, "total_grievances": 4,
             "capacity": 1, "resolution_days": .01, "sla_days": 30},
            seed=9,
        )
        queued_values = {row["KPI"]: row["Value"] for row in queued["kpis"]}
        self.assertEqual(queued["kpis"], repeated["kpis"])
        self.assertEqual(queued_values["Cases Resolved"] + queued_values["Cases Unresolved"], 4)
        self.assertEqual(sum(row["Grievances"] for row in queued["series"]), 4)
        self.assertEqual(queued_values["Cases Waiting at Period End"], 0)
        self.assertIsNotNone(queued_values["Average Waiting Time for Started Cases (days)"])
        self.assertEqual(queued_values["SLA Compliance (%)"], 100)

    def test_employee_relations_censors_waiting_cases_at_observation_end(self):
        result = run_simulation("Employee Relations", {
            "employees": 100, "grievance_rate": .1, "capacity": 1,
            "resolution_days": 100, "period_days": 1, "sla_days": 1,
            "total_grievances": 8,
        }, seed=4)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        self.assertEqual(values["Cases Resolved"], 0)
        self.assertEqual(values["Cases Unresolved"], 8)
        self.assertEqual(
            values["Cases Waiting at Period End"] + values["Cases in Investigation at Period End"],
            values["Cases Unresolved"],
        )
        self.assertLessEqual(
            values["Average Waiting Time for Started Cases (days)"],
            values["Average Censored Wait for Cases Still Waiting (days)"],
        )
        self.assertGreater(values["Average Pending-Case Age (days)"], 0)
        self.assertGreater(values["Average Censored Wait for Cases Still Waiting (days)"], 0)

    def test_employee_relations_sla_counts_overdue_unresolved_cases_as_failures(self):
        result = run_simulation("Employee Relations", {
            "employees": 100, "grievance_rate": .1, "capacity": 1,
            "resolution_days": 100, "period_days": 1, "sla_days": .1,
            "total_grievances": 8,
        }, seed=4)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        self.assertEqual(values["Unresolved Past SLA Deadline"], 6)
        self.assertEqual(values["Unresolved Before SLA Deadline"], 2)
        self.assertEqual(values["SLA Compliance Denominator"], 6)
        self.assertEqual(values["SLA Compliance (%)"], 0)

    def test_monte_carlo_reports_simulation_percentiles_and_rejects_deterministic_modules(self):
        params = {
            "workforce": 100, "months": 3, "voluntary": .02, "involuntary": .005,
            "retirement": .002, "hires": 4, "replacement_cost": 5000,
        }
        first = run_monte_carlo("Employee Attrition & Retention", params, iterations=20, seed=3)
        repeated = run_monte_carlo("Employee Attrition & Retention", params, iterations=20, seed=3)
        self.assertEqual(first, repeated)
        self.assertIn("not a statistical confidence interval", first["interval_label"])
        annual = next(row for row in first["summaries"] if row["KPI"] == "Final Workforce")
        self.assertLessEqual(annual["5th Percentile"], annual["Mean"])
        self.assertLessEqual(annual["Mean"], annual["95th Percentile"])
        with self.assertRaises(ValueError):
            run_monte_carlo("Workforce Planning", {}, iterations=10, seed=3)

    def test_monte_carlo_runs_for_each_stochastic_module_reproducibly(self):
        examples = {
            "Employee Attrition & Retention": {
                "workforce": 20, "months": 2, "voluntary": .02, "involuntary": .005,
                "retirement": .002, "hires": 1, "replacement_cost": 100,
            },
            "Performance Management": {
                "employees": 20, "mean_rating": 3, "rating_spread": .5,
                "training_effect": .2, "reward_budget": 100,
            },
            "Compensation & Benefits": {
                "employees": 20, "salary": 60000, "spread": 5000,
                "increment": .04, "bonus": .05, "benefits": .1,
            },
            "Employee Relations": {
                "employees": 20, "grievance_rate": .03, "capacity": 2,
                "resolution_days": 5, "period_days": 10, "sla_days": 5,
            },
        }
        for module, params in examples.items():
            with self.subTest(module=module):
                result = run_monte_carlo(module, params, iterations=5, seed=11)
                self.assertEqual(result, run_monte_carlo(module, params, iterations=5, seed=11))
                self.assertTrue(result["summaries"])
                for summary in result["summaries"]:
                    self.assertLessEqual(summary["5th Percentile"], summary["95th Percentile"])

    def test_monte_carlo_seed_wraps_at_supported_upper_boundary(self):
        result = run_monte_carlo("Employee Attrition & Retention", {
            "workforce": 5, "months": 1, "voluntary": .02, "involuntary": 0,
            "retirement": 0, "hires": 0, "replacement_cost": 0,
        }, iterations=2, seed=2147483647)
        repeated = run_monte_carlo("Employee Attrition & Retention", {
            "workforce": 5, "months": 1, "voluntary": .02, "involuntary": 0,
            "retirement": 0, "hires": 0, "replacement_cost": 0,
        }, iterations=2, seed=2147483647)
        self.assertEqual(result, repeated)

    def test_sensitivity_analysis_uses_common_seed_and_identifies_productivity(self):
        result = run_sensitivity_analysis("Workforce Planning", {
            "workforce": 100, "demand": 110, "months": 12, "growth": .01,
            "turnover": .01, "productivity": 1, "monthly_cost": 3000,
        }, seed=4)
        self.assertEqual(result["target_kpi"], "Hiring Requirement")
        productivity = next(row for row in result["results"] if row["Input"] == "productivity")
        self.assertNotEqual(productivity["Output change"], 0)
        self.assertIn(productivity["Direction"], {"increase", "decrease"})

    def test_sensitivity_uses_valid_directions_at_module_bounds(self):
        result = run_sensitivity_analysis("Performance Management", {
            "employees": 20, "mean_rating": 5, "rating_spread": .1,
            "training_effect": 2, "reward_budget": 0,
        }, seed=8)
        by_input = {row["Input"]: row for row in result["results"]}
        self.assertEqual(by_input["mean_rating"]["Direction"], "decrease")
        self.assertLess(by_input["mean_rating"]["Perturbed"], 5)
        self.assertEqual(by_input["training_effect"]["Direction"], "decrease")
        self.assertLessEqual(by_input["training_effect"]["Perturbed"], 2)
        self.assertEqual(by_input["reward_budget"]["Direction"], "increase")

    def test_sensitivity_covers_every_numeric_default_with_valid_perturbations(self):
        for module, params in DEFAULT_SIMULATION_PARAMS.items():
            with self.subTest(module=module):
                result = run_sensitivity_analysis(module, params, seed=14)
                expected_inputs = {
                    key for key, value in params.items()
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                }
                actual_inputs = {row["Input"] for row in result["results"]}
                self.assertEqual(actual_inputs, expected_inputs)
                for row in result["results"]:
                    self.assertIn(row["Direction"], {"increase", "decrease"})
                    self.assertNotEqual(row["Baseline"], row["Perturbed"])

    def test_non_finite_numeric_inputs_are_rejected_for_all_modules(self):
        for module, params in DEFAULT_SIMULATION_PARAMS.items():
            with self.subTest(module=module):
                numeric_parameter = next(
                    key for key, value in params.items()
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                )
                with self.assertRaisesRegex(ValueError, "must be finite"):
                    run_simulation(module, {**params, numeric_parameter: float("nan")}, seed=2)

    def test_zero_volume_and_invalid_rate_boundaries(self):
        recruitment = run_simulation("Recruitment & Talent Acquisition", {
            "vacancies": 0, "applicants": 0, "recruiters": 1, "interviewers": 1,
            "budget": 0, "screen_rate": 0, "shortlist_rate": 0, "dropout_rate": 0,
            "offer_rate": 0, "acceptance_rate": 0, "joining_rate": 0,
            "screen_days": 0, "interview_days": 0,
        }, seed=1)
        recruitment_values = {row["KPI"]: row["Value"] for row in recruitment["kpis"]}
        self.assertEqual(recruitment_values["Employees Joined"], 0)
        self.assertEqual(recruitment_values["Hiring Target Attainment (%)"], 0)

        free_training = run_simulation("Learning & Development", {
            "employees": 0, "eligibility_rate": 0, "participation": 0, "budget": 0,
            "cost_per_person": 0, "completion": 0, "pass_rate": 0, "learning_gain": 0,
            "pre_training_score": 0, "value_per_gain": 0,
        }, seed=1)
        training_values = {row["KPI"]: row["Value"] for row in free_training["kpis"]}
        self.assertEqual(training_values["Enrolled"], 0)
        self.assertIsNone(training_values["Estimated Training ROI (%)"])

        zero_performance = run_simulation("Performance Management", {
            "employees": 0, "mean_rating": 3, "rating_spread": .5,
            "training_effect": .2, "reward_budget": 100,
        }, seed=1)
        performance_values = {row["KPI"]: row["Value"] for row in zero_performance["kpis"]}
        self.assertEqual(performance_values["High Performer Share (%)"], 0)
        self.assertEqual(performance_values["Rewards Allocated (INR)"], 0)

        zero_workforce = run_simulation("Workforce Planning", {
            "workforce": 0, "demand": 0, "months": 1, "growth": 0, "turnover": 0,
            "productivity": 1, "monthly_cost": 0,
        }, seed=1)
        workforce_values = {row["KPI"]: row["Value"] for row in zero_workforce["kpis"]}
        self.assertEqual(workforce_values["Workforce Utilization (%)"], 0)
        self.assertEqual(workforce_values["Estimated Labour Cost (INR over horizon)"], 0)

        zero_compensation = run_simulation("Compensation & Benefits", {
            "employees": 0, "salary": 60000, "spread": 0,
            "increment": 0, "bonus": 0, "benefits": 0,
        }, seed=1)
        compensation_values = {row["KPI"]: row["Value"] for row in zero_compensation["kpis"]}
        self.assertEqual(compensation_values["Base Payroll (INR/year)"], 0)
        self.assertEqual(compensation_values["Compensation Increase (%)"], 0)

        with self.assertRaises(ValueError):
            run_simulation("Employee Attrition & Retention", {
                "workforce": 10, "months": 1, "voluntary": .8, "involuntary": .3,
                "retirement": 0, "hires": 0, "replacement_cost": 0,
            }, seed=1)

    def test_grievance_arrival_volume_scales_with_observation_period(self):
        params = {
            "employees": 100, "grievance_rate": .1, "capacity": 2,
            "resolution_days": 12, "period_days": 60,
        }
        result = run_simulation("Employee Relations", params, seed=13)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        expected = int(np.random.default_rng(13).poisson(20))
        self.assertEqual(values["Total Grievances"], expected)
        self.assertTrue(any("20 expected cases" in note for note in result["notes"]))


if __name__ == "__main__":
    unittest.main()
