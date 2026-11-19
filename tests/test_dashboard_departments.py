import unittest
from pathlib import Path
from io import BytesIO

from openpyxl import Workbook
from streamlit.testing.v1 import AppTest

from engines.simulation_core import MODULES

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class DashboardDepartmentTests(unittest.TestCase):
    def test_department_headcounts_update_dashboard_and_rows_can_be_managed(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
        self.assertFalse(app.exception, [item.message for item in app.exception])

        initial_total = int(next(item for item in app.metric if item.label == "Total employees").value)
        first_department = next(
            item for item in app.number_input if item.label == "Employees in department 1"
        )
        first_department.set_value(first_department.value + 10)
        app.run()
        self.assertFalse(app.exception, [item.message for item in app.exception])
        updated_total = int(next(item for item in app.metric if item.label == "Total employees").value)
        self.assertEqual(updated_total, initial_total + 10)

        next(button for button in app.button if button.label == "Add department").click()
        app.run()
        self.assertFalse(app.exception, [item.message for item in app.exception])
        self.assertEqual(
            len([item for item in app.text_input if item.label == "Department name"]),
            6,
        )

        next(button for button in app.button if button.key == "remove_department_6").click()
        app.run()
        self.assertFalse(app.exception, [item.message for item in app.exception])
        self.assertFalse(
            any(item.label == "Employees in department 6" for item in app.number_input)
        )

    def test_sidebar_modules_and_run_controls_render_without_exceptions(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
        for module, module_key in MODULES.items():
            with self.subTest(module=module):
                next(item for item in app.button if item.key == f"nav_{module}").click()
                app.run()
                self.assertFalse(app.exception, [item.message for item in app.exception])
                next(item for item in app.button if item.key == f"run_{module_key}").click()
                app.run()
                self.assertFalse(app.exception, [item.message for item in app.exception])
        next(item for item in app.button if item.key == "nav_Reports & Exports").click()
        app.run()
        self.assertFalse(app.exception, [item.message for item in app.exception])
        report_downloads = [item.label for item in app.get("download_button")]
        self.assertIn("Download KPI report (CSV)", report_downloads)
        self.assertIn("Download report (Excel)", report_downloads)
        self.assertIn("Download report (PDF)", report_downloads)

    def test_synthetic_dataset_generation_renders_downloads(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
        next(item for item in app.button if item.key == "nav_Data Management").click()
        app.run()
        next(item for item in app.button if item.label == "Generate synthetic dataset").click()
        app.run()
        self.assertFalse(app.exception, [item.message for item in app.exception])
        download_labels = [item.label for item in app.get("download_button")]
        self.assertIn("Download synthetic CSV", download_labels)
        self.assertIn("Download synthetic Excel", download_labels)

    def test_confirmed_uploaded_mapping_drives_simulation_with_provenance(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
        app.session_state["uploaded_source"] = {
            "name": "company.csv",
            "content": b"applicant_id\nA1\nA2\nA3\nA4\n",
        }
        next(item for item in app.button if item.key == "nav_Data Management").click()
        app.run()
        next(item for item in app.selectbox
             if item.key == "upload_map_Recruitment & Talent Acquisition_applicants").set_value("applicant_id")
        next(item for item in app.selectbox
             if item.key == "upload_agg_Recruitment & Talent Acquisition_applicants").set_value("count")
        app.run()
        next(item for item in app.checkbox
             if item.label.startswith("I reviewed the column mappings")).set_value(True)
        app.run()
        next(item for item in app.button
             if item.label == "Run simulation with selected data").click()
        app.run()
        self.assertFalse(app.exception, [item.message for item in app.exception])
        latest = app.session_state["latest_results"]["Recruitment & Talent Acquisition"]
        self.assertEqual(latest["params"]["applicants"], 4)
        self.assertEqual(latest["provenance"]["dataset_source"], "Uploaded company data")

    def test_excel_worksheet_is_user_selectable(self):
        workbook = Workbook()
        workbook.active.title = "Summary"
        workbook.active.append(["ignored"])
        second = workbook.create_sheet("Employee table")
        second.append(["employee_id", "salary"])
        second.append(["E1", 50000])
        contents = BytesIO()
        workbook.save(contents)

        app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
        app.session_state["uploaded_source"] = {
            "name": "company.xlsx", "content": contents.getvalue(),
        }
        next(item for item in app.button if item.key == "nav_Data Management").click()
        app.run()
        next(item for item in app.selectbox if item.key == "company_sheet").set_value("Employee table")
        app.run()
        self.assertFalse(app.exception, [item.message for item in app.exception])
        self.assertEqual(app.session_state["uploaded_data"]["columns"], ["employee_id", "salary"])
        self.assertEqual(app.session_state["uploaded_data"]["rows"], [["E1", 50000]])

    def test_record_level_upload_mode_shows_supported_analysis_and_unavailable_schema(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
        app.session_state["uploaded_source"] = {
            "name": "performance.csv",
            "content": (
                b"employee_id,department,appraisal_period,performance_rating,goal_achievement\n"
                b"E1,HR,2025,3.0,0.7\nE1,HR,2026,4.0,0.8\n"
            ),
        }
        next(item for item in app.button if item.key == "nav_Data Management").click()
        app.run()
        next(item for item in app.selectbox
             if item.key == "uploaded_module").set_value("Performance Management")
        next(item for item in app.radio
             if item.label == "Choose how to use the selected dataset").set_value(
                 "Record-Level Analysis Mode"
             )
        app.run()
        self.assertFalse(app.exception, [item.message for item in app.exception])
        self.assertTrue(any("Record-Level Analysis Mode" in item.value for item in app.markdown))
        comparison_checkbox = next(
            item for item in app.checkbox
            if item.label == "Compare matched employee ratings across appraisal periods"
        )
        comparison_checkbox.set_value(True)
        app.run(timeout=60)
        self.assertFalse(app.exception, [item.message for item in app.exception])
        self.assertTrue(any(
            "Matched appraisal-period comparison" in item.value for item in app.markdown
        ))

        next(item for item in app.selectbox
             if item.key == "uploaded_module").set_value("Employee Attrition & Retention")
        app.session_state["uploaded_source"] = {
            "name": "employees.csv",
            "content": b"employee_id,department,hire_date,tenure_months\nE1,HR,2024-01-01,12\n",
        }
        app.run()
        self.assertFalse(app.exception, [item.message for item in app.exception])
        self.assertTrue(any(
            "lacks: exit_date" in item.value for item in app.info
        ))

    def test_monte_carlo_and_sensitivity_controls_render_results(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
        next(item for item in app.button
             if item.key == "nav_Employee Attrition & Retention").click()
        app.run()
        next(item for item in app.number_input
             if item.key == "mc_iterations_attrition").set_value(10)
        app.run()
        next(item for item in app.button if item.key == "mc_run_attrition").click()
        app.run()
        self.assertIn("Employee Attrition & Retention", app.session_state["monte_carlo_results"])
        next(item for item in app.button
             if item.key == "sensitivity_run_attrition").click()
        app.run()
        self.assertIn("Employee Attrition & Retention", app.session_state["sensitivity_results"])
        self.assertEqual(
            app.session_state["sensitivity_results"]["Employee Attrition & Retention"]["seed"],
            42,
        )
        self.assertFalse(app.exception, [item.message for item in app.exception])


if __name__ == "__main__":
    unittest.main()
