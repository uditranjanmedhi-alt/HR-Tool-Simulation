import csv
import unittest
from io import BytesIO, StringIO

from data.synthetic_generator import (
    MODULE_DATASETS,
    generate_synthetic_data,
    records_to_csv,
    records_to_xlsx,
)
from data.data_validator import validate_dataframe
from data.record_analysis import analyze_record_level_data
from data.upload_pipeline import DEFAULT_SIMULATION_PARAMS, map_uploaded_data


class SyntheticDataTests(unittest.TestCase):
    def test_all_module_datasets_are_reproducible_and_marked_synthetic(self):
        self.assertEqual(len(MODULE_DATASETS), 7)
        for module in MODULE_DATASETS:
            with self.subTest(module=module):
                first = generate_synthetic_data(module, size=12, seed=7)
                repeated = generate_synthetic_data(module, size=12, seed=7)
                self.assertEqual(first, repeated)
                self.assertEqual(len(first), 12)
                self.assertTrue(all(record["synthetic"] for record in first))
        attrition_report = validate_dataframe(
            generate_synthetic_data("Employee Attrition & Retention", size=12, seed=7),
            "attrition_records",
        )
        self.assertTrue(attrition_report["valid"], attrition_report["summary"])

    def test_synthetic_exports_are_valid_csv_and_xlsx(self):
        records = generate_synthetic_data("Compensation & Benefits", size=3, seed=2)
        csv_rows = list(csv.DictReader(StringIO(records_to_csv(records).decode("utf-8-sig"))))
        self.assertEqual(len(csv_rows), 3)
        workbook_bytes = records_to_xlsx(records)
        self.assertTrue(workbook_bytes.startswith(b"PK"))


class UploadedDataMappingTests(unittest.TestCase):
    def test_schema_validator_reports_missing_duplicate_and_invalid_values(self):
        report = validate_dataframe([
            {"employee_id": "E1", "department": "HR", "salary": "not a salary"},
            {"employee_id": "E1", "department": "HR", "salary": 50000},
        ], "employees")
        self.assertFalse(report["valid"])
        self.assertEqual(report["missing_columns"], [
            "job_level", "hire_date", "experience_years", "performance_score",
        ])
        self.assertEqual(report["duplicate_ids"], 1)
        self.assertEqual(report["invalid_numeric_values"]["salary"], 1)

    def test_column_mapping_aggregates_only_after_explicit_cleaning_choices(self):
        columns = ["employee_id", "salary", "rating"]
        rows = [
            ["E1", 100, 2],
            ["E2", 200, 4],
            ["E3", None, 6],
            ["E4", "not numeric", 5],
        ]
        defaults = DEFAULT_SIMULATION_PARAMS["Performance Management"]
        mappings = {"employees": "employee_id", "mean_rating": "rating", "training_effect": "salary"}
        aggregations = {"employees": "count", "mean_rating": "mean", "training_effect": "mean"}
        common = {
            "missing_treatment": "median-fill numeric columns",
            "duplicate_treatment": "keep duplicates",
            "random_seed": 13,
            "dataset_name": "company.csv",
        }
        with self.assertRaisesRegex(ValueError, "non-numeric"):
            map_uploaded_data(
                columns, rows, mappings, aggregations, defaults,
                invalid_treatment="stop if invalid values exist", **common,
            )
        params, provenance, report = map_uploaded_data(
            columns, rows, mappings, aggregations, defaults,
            invalid_treatment="exclude rows with invalid values", **common,
        )
        self.assertEqual(params["employees"], 3)
        self.assertEqual(params["mean_rating"], 4)
        self.assertEqual(params["training_effect"], 150)
        self.assertEqual(report["invalid_cells_in_mapped_columns"], 1)
        self.assertEqual(report["missing_cells_in_mapped_columns"], 1)
        self.assertEqual(report["excluded_records"], 1)
        self.assertEqual(provenance["column_mappings"]["employees"]["aggregation"], "count")
        self.assertEqual(provenance["random_seed"], 13)

    def test_duplicate_rows_are_excluded_only_when_selected(self):
        columns = ["employee_id", "rating"]
        rows = [["E1", 3], ["E1", 3], ["E2", 4]]
        params, _, report = map_uploaded_data(
            columns, rows,
            {"employees": "employee_id", "mean_rating": "rating"},
            {"employees": "count", "mean_rating": "mean"},
            DEFAULT_SIMULATION_PARAMS["Performance Management"],
            missing_treatment="exclude affected rows",
            invalid_treatment="stop if invalid values exist",
            duplicate_treatment="exclude duplicate rows",
            random_seed=42,
            dataset_name="duplicates.csv",
        )
        self.assertEqual(report["duplicate_records"], 1)
        self.assertEqual(report["retained_records"], 2)
        self.assertEqual(params["employees"], 2)
        self.assertEqual(params["mean_rating"], 3.5)

    def test_invalid_values_can_be_corrected_with_an_explicit_numeric_replacement(self):
        params, provenance, report = map_uploaded_data(
            ["employee_id", "rating"],
            [["E1", 3], ["E2", "invalid"]],
            {"employees": "employee_id", "mean_rating": "rating"},
            {"employees": "count", "mean_rating": "mean"},
            DEFAULT_SIMULATION_PARAMS["Performance Management"],
            missing_treatment="exclude affected rows",
            invalid_treatment="replace invalid values with explicit number",
            invalid_replacements={"mean_rating": 2},
            duplicate_treatment="keep duplicates",
            random_seed=2,
            dataset_name="corrected.csv",
        )
        self.assertEqual(params["mean_rating"], 2.5)
        self.assertEqual(report["retained_records"], 2)
        self.assertEqual(report["excluded_records"], 0)
        self.assertEqual(provenance["invalid_value_replacements"], {"mean_rating": 2.0})


class RecordLevelAnalysisTests(unittest.TestCase):
    def test_compensation_summarizes_record_level_total_compensation(self):
        result = analyze_record_level_data(
            "Compensation & Benefits",
            ["employee_id", "department", "base_salary", "allowances", "variable_pay", "benefits"],
            [
                ["E1", "HR", 100, 10, 20, 30],
                ["E2", "Finance", 200, 0, 0, 20],
            ],
        )
        total = next(row for row in result["summaries"] if row["Measure"] == "Total compensation")
        self.assertEqual(total["Records with value"], 2)
        self.assertEqual(total["Mean"], 190)
        self.assertEqual(result["distributions"]["Total compensation"], [160, 220])
        self.assertEqual(result["mode"], "Record-Level Analysis Mode")

    def test_attrition_requires_exit_fields_and_reports_snapshot_not_period_rate(self):
        with self.assertRaisesRegex(ValueError, "exit_date"):
            analyze_record_level_data(
                "Employee Attrition & Retention",
                ["employee_id", "hire_date", "tenure_months"],
                [["E1", "2024-01-01", 12]],
            )
        result = analyze_record_level_data(
            "Employee Attrition & Retention",
            ["employee_id", "hire_date", "exit_date", "exit_category", "department",
             "tenure_months", "employment_status"],
            [
                ["E1", "2024-01-01", None, None, "HR", 24, "Active"],
                ["E2", "2022-01-01", "2025-01-01", "Voluntary", "HR", 36, "Exited"],
            ],
        )
        status_counts = {
            row["Category"]: row["Records"]
            for row in result["category_counts"] if row["Field"] == "employment_status"
        }
        self.assertEqual(status_counts, {"Active": 1, "Exited": 1})
        self.assertTrue(any("no period attrition rate is inferred" in note.lower()
                            for note in result["notes"]))

    def test_learning_analysis_uses_only_complete_pre_post_pairs(self):
        result = analyze_record_level_data(
            "Learning & Development",
            ["employee_id", "training_programme", "enrolment_date", "completion_status",
             "assessment_pass", "pre_training_score", "post_training_score"],
            [
                ["E1", "Safety", "2026-01-01", "Completed", True, 60, 80],
                ["E2", "Safety", "2026-01-01", "In progress", None, 50, None],
                ["E3", "Analytics", "2026-01-01", "Completed", False, 70, 60],
            ],
        )
        comparison = result["paired_score_comparison"]
        self.assertEqual(comparison["Matched records"], 2)
        self.assertEqual(comparison["Mean pre/post score change (points)"], 5)
        gain = next(row for row in result["summaries"] if row["Measure"] == "Paired score change")
        self.assertEqual(gain["Records with value"], 2)
        self.assertEqual(gain["Mean"], 5)

    def test_performance_period_and_group_comparisons_are_matched_and_descriptive(self):
        columns = ["employee_id", "department", "appraisal_period", "performance_rating", "goal_achievement"]
        rows = [
            ["E1", "A", "pre", 3, .7], ["E1", "A", "post", 4, .8],
            ["E2", "A", "pre", 2, .6], ["E2", "A", "post", 4, .8],
            ["E3", "B", "pre", 3, .7], ["E3", "B", "post", 3.5, .7],
            ["E4", "B", "pre", 4, .9], ["E4", "B", "post", 3.5, .8],
        ]
        result = analyze_record_level_data(
            "Performance Management", columns, rows,
            pre_period="pre", post_period="post",
            comparison_group_column="department", group_a="A", group_b="B",
        )
        paired = result["paired_period_comparison"]
        groups = result["comparison_group_evaluation"]
        self.assertEqual(paired["Matched employees"], 4)
        self.assertEqual(paired["Mean paired rating change (points)"], .75)
        self.assertEqual(groups["Group A matched employees"], 2)
        self.assertEqual(groups["Group B matched employees"], 2)
        self.assertEqual(groups["Difference in mean change (A − B, points)"], 1.5)
        self.assertTrue(any("not a causal estimate" in note for note in result["notes"]))

    def test_record_level_mode_can_exclude_exact_duplicates(self):
        columns = ["employee_id", "department", "base_salary", "allowances", "variable_pay", "benefits"]
        rows = [
            ["E1", "HR", 100, 10, 20, 30],
            ["E1", "HR", 100, 10, 20, 30],
            ["E2", "Finance", 200, 0, 0, 20],
        ]
        result = analyze_record_level_data(
            "Compensation & Benefits", columns, rows, exclude_duplicate_rows=True,
        )
        self.assertEqual(result["duplicate_records"], 1)
        self.assertEqual(result["retained_records"], 2)
        self.assertEqual(result["excluded_duplicate_records"], 1)


if __name__ == "__main__":
    unittest.main()
