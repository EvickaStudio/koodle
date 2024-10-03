from PyQt6 import QtWidgets, QtCore
from .widgets import CourseTile
import math

class Dashboard(QtWidgets.QWidget):
    course_selected = QtCore.pyqtSignal(dict)

    def __init__(self, moodle_api, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.token = moodle_api.token
        self.init_ui()

    def init_ui(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Title
        title = QtWidgets.QLabel("Your Courses")
        title.setStyleSheet("color: white; font-size: 24px;")
        self.layout.addWidget(title)

        # Scroll Area
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: #1e1e1e;")
        self.layout.addWidget(self.scroll)

        # Container widget
        self.container = QtWidgets.QWidget()
        self.scroll.setWidget(self.container)

        # Grid Layout
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(20)
        self.container.setLayout(self.grid)

        self.load_courses()

    def load_courses(self):
        courses = self.moodle_api.get_course(self.moodle_api.get_user_id())
        if not courses:
            QtWidgets.QMessageBox.warning(self, "Error", "Could not load courses.")
            return

        self.courses = courses
        self.update_grid()

    def update_grid(self):
        # Clear existing items in the grid
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Determine number of columns based on window width
        available_width = self.scroll.viewport().width()
        tile_width = 250  # Width of each CourseTile
        spacing = self.grid.spacing()
        columns = max(1, available_width // (tile_width + spacing))

        # Limit to 3 columns
        columns = min(columns, 3)

        # Populate grid
        row = 0
        col = 0
        for course in self.courses:
            tile = CourseTile(course, self.token)
            tile.clicked.connect(self.on_tile_clicked)
            self.grid.addWidget(tile, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        # Add stretch to push items to the top
        self.grid.setRowStretch(row + 1, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_grid()

    def on_tile_clicked(self, course):
        self.course_selected.emit(course)
