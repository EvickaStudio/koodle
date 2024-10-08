# Filename: grades_overview.py
from PyQt6 import QtWidgets, QtCore


class GradesOverview(QtWidgets.QWidget):
    def __init__(self, moodle_api, course_id, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.course_id = course_id
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QtWidgets.QLabel("Grades Overview")
        title.setStyleSheet("color: white; font-size: 24px;")
        layout.addWidget(title)

        # Grades Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Item", "Grade", "Range", "Feedback"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Fetch and populate grades
        self.fetch_and_display_grades()

    def fetch_and_display_grades(self):
        grades_data = self.moodle_api.get_user_grades(self.course_id)
        if not grades_data or "usergrades" not in grades_data:
            QtWidgets.QMessageBox.warning(self, "Error", "Could not fetch grades.")
            return

        usergrades = grades_data["usergrades"][0]
        grade_items = usergrades.get("gradeitems", [])

        self.table.setRowCount(len(grade_items))

        for row, item in enumerate(grade_items):
            item_name = item.get("itemname", "Unnamed Item")
            grade = item.get("graderaw", "N/A")
            grademin = item.get("grademin", 0)
            grademax = item.get("grademax", 100)
            feedback = item.get("feedback", "")

            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item_name))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(grade)))
            self.table.setItem(
                row, 2, QtWidgets.QTableWidgetItem(f"{grademin} - {grademax}")
            )
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(feedback))

        self.table.resizeColumnsToContents()
