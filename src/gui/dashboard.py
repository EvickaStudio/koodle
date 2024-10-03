# gui/dashboard.py

from PyQt6 import QtWidgets, QtCore
from .widgets import CourseTile


class Dashboard(QtWidgets.QWidget):
    course_selected = QtCore.pyqtSignal(dict)

    def __init__(self, moodle_api, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.token = moodle_api.token  # Get the token from moodle_api
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Scroll Area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)

        # Container widget
        container = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(20)
        container.setLayout(self.grid)

        scroll.setWidget(container)

        layout.addWidget(scroll)
        self.setLayout(layout)

        self.load_courses()

    def load_courses(self):
        courses = self.moodle_api.get_course(self.moodle_api.get_user_id())
        if not courses:
            QtWidgets.QMessageBox.warning(self, "Error", "Could not load courses.")
            return

        row = 0
        col = 0
        max_col = 4  # Number of columns in the grid

        for course in courses:
            tile = CourseTile(course, self.token)  # Pass the token to CourseTile
            tile.clicked.connect(self.on_tile_clicked)
            self.grid.addWidget(tile, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1

    def on_tile_clicked(self, course):
        self.course_selected.emit(course)