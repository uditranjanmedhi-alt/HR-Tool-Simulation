import unittest

from engines.simulation_core import MODULES, run_simulation


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


if __name__ == "__main__":
    unittest.main()
