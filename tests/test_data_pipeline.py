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


if __name__ == "__main__":
    unittest.main()
