import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


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


if __name__ == "__main__":
    unittest.main()
