# Filename: dashboard.py
from PyQt6 import QtWidgets, QtCore
from .widgets import CourseTile
import math

class FetchCoursesSignals(QtCore.QObject):
    courses_loaded = QtCore.pyqtSignal(list)
    error = QtCore.pyqtSignal()

class FetchCoursesRunnable(QtCore.QRunnable):
    def __init__(self, moodle_api):
        super().__init__()
        self.moodle_api = moodle_api
        self.signals = FetchCoursesSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            user_id = self.moodle_api.get_user_id()
            if user_id is None:
                self.signals.error.emit()
                return

            courses = self.moodle_api.get_course(user_id)
            if courses:
                self.signals.courses_loaded.emit(courses)
            else:
                self.signals.error.emit()
        except Exception as e:
            print(f"Error fetching courses: {e}")
            self.signals.error.emit()

class Dashboard(QtWidgets.QWidget):
    course_selected = QtCore.pyqtSignal(dict)

    def __init__(self, moodle_api, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.token = moodle_api.token
        self.init_ui()
        self.courses = []
        self.load_courses()

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

    def load_courses(self):
        runnable = FetchCoursesRunnable(self.moodle_api)
        runnable.signals.courses_loaded.connect(self.on_courses_loaded)
        runnable.signals.error.connect(self.on_error)
        QtCore.QThreadPool.globalInstance().start(runnable)

    @QtCore.pyqtSlot(list)
    def on_courses_loaded(self, courses):
        self.courses = courses
        self.populate_grid()

    @QtCore.pyqtSlot()
    def on_error(self):
        QtWidgets.QMessageBox.warning(self, "Error", "Could not load courses.")

    @QtCore.pyqtSlot()
    def populate_grid(self):
        # Clear existing items in the grid
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Determine number of columns based on window width
        available_width = self.scroll.viewport().width()
        tile_width = 300  # Width of each CourseTile (updated)
        spacing = self.grid.spacing()
        columns = max(1, available_width // (tile_width + spacing))

        # Limit to 4 columns for better display
        columns = min(columns, 4)

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
        self.populate_grid()

    def on_tile_clicked(self, course):
        self.course_selected.emit(course)
