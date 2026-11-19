import unittest

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
        self.assertGreater(higher_values["Total Compensation Cost"], values["Total Compensation Cost"])

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

    def test_invalid_module_is_rejected(self):
        with self.assertRaises(ValueError):
            run_simulation("not a module", {}, seed=1)

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
        for month in result["series"]:
            self.assertEqual(
                month["Opening Workforce"] + month["Hires"] - month["Exits"],
                month["Workforce"],
            )
            self.assertEqual(
                month["Voluntary Exits"] + month["Involuntary Exits"] + month["Retirement Exits"],
                month["Exits"],
            )

    def test_workforce_productivity_and_cumulative_monthly_cost(self):
        params = {
            "workforce": 10, "demand": 12, "months": 3, "growth": 0, "turnover": 0,
            "productivity": 2, "monthly_cost": 100,
        }
        result = run_simulation("Workforce Planning", params, seed=1)
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        self.assertEqual(values["Required FTE"], 6)
        self.assertEqual(values["Workforce Gap"], -4)
        self.assertEqual(values["Estimated Labour Cost"], 3000)
        self.assertEqual(sum(row["Monthly Labour Cost"] for row in result["series"]), 3000)
        lower_productivity = run_simulation(
            "Workforce Planning", {**params, "productivity": 1}, seed=1
        )
        lower_values = {row["KPI"]: row["Value"] for row in lower_productivity["kpis"]}
        self.assertEqual(lower_values["Required FTE"], 12)
        self.assertEqual(lower_values["Workforce Gap"], 2)

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
        self.assertEqual(values["Estimated Financial Benefit (assumption-based)"], 2000)
        self.assertEqual(values["Estimated Training ROI (%)"], 700)

        free_training = run_simulation(
            "Learning & Development", {**params, "cost_per_person": 0}, seed=1
        )
        free_values = {row["KPI"]: row["Value"] for row in free_training["kpis"]}
        self.assertIsNone(free_values["Estimated Training ROI (%)"])

    def test_employee_relations_queue_conserves_cases_and_is_reproducible(self):
        params = {
            "employees": 0, "grievance_rate": .03, "capacity": 2,
            "resolution_days": 5, "period_days": 30, "sla_days": 10,
        }
        empty = run_simulation("Employee Relations", params, seed=9)
        empty_values = {row["KPI"]: row["Value"] for row in empty["kpis"]}
        self.assertEqual(empty_values["Total Grievances"], 0)
        self.assertEqual(empty_values["Open Grievances"], 0)
        self.assertEqual(empty_values["Resolution Rate (%)"], 0)

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
        self.assertEqual(queued_values["Grievances Resolved"] + queued_values["Open Grievances"], 4)
        self.assertEqual(sum(row["Grievances"] for row in queued["series"]), 4)
        self.assertEqual(queued_values["Average Waiting Time (days)"], 0)
        self.assertEqual(queued_values["SLA Compliance (%)"], 100)

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

    def test_sensitivity_analysis_uses_common_seed_and_identifies_productivity(self):
        result = run_sensitivity_analysis("Workforce Planning", {
            "workforce": 100, "demand": 110, "months": 12, "growth": .01,
            "turnover": .01, "productivity": 1, "monthly_cost": 3000,
        }, seed=4)
        self.assertEqual(result["target_kpi"], "Hiring Requirement")
        productivity = next(row for row in result["results"] if row["Input"] == "productivity")
        self.assertNotEqual(productivity["Output change"], 0)

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

        with self.assertRaises(ValueError):
            run_simulation("Employee Attrition & Retention", {
                "workforce": 10, "months": 1, "voluntary": .8, "involuntary": .3,
                "retirement": 0, "hires": 0, "replacement_cost": 0,
            }, seed=1)


if __name__ == "__main__":
    unittest.main()
