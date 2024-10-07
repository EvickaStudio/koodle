# Filename: dashboard.py
from PyQt6 import QtWidgets, QtCore, QtGui
from .widgets import CourseTile
from .config import Config
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


class FetchCourseStatesRunnable(QtCore.QRunnable):
    def __init__(self, moodle_api, courses):
        super().__init__()
        self.moodle_api = moodle_api
        self.courses = courses
        self.signals = FetchCoursesSignals()
        self.results = []

    @QtCore.pyqtSlot()
    def run(self):
        try:
            for course in self.courses:
                course_id = course["id"]
                contents = self.moodle_api.get_course_content(course_id)
                # Compute the state
                if contents is None:
                    continue
                state = []
                for section in contents:
                    for module in section.get("modules", []):
                        module_id = module.get("id")
                        module_modified = module.get("timemodified", 0)
                        state.append({"id": module_id, "timemodified": module_modified})
                self.results.append({"course_id": course_id, "state": state})
            self.signals.courses_loaded.emit(self.results)
        except Exception as e:
            print(f"Error fetching course states: {e}")
            self.signals.error.emit()


class Dashboard(QtWidgets.QWidget):
    course_selected = QtCore.pyqtSignal(dict)

    def __init__(self, moodle_api, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.token = moodle_api.token
        self.config = Config()
        self.init_ui()
        self.all_courses = []
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

        # Search Bar and Refresh Button Layout
        search_layout = QtWidgets.QHBoxLayout()
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search courses...")
        self.search_bar.setStyleSheet(
            """
            QLineEdit {
                padding: 10px;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                background-color: #252526;
                color: #d4d4d4;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """
        )
        self.search_bar.textChanged.connect(self.update_course_list)
        search_layout.addWidget(self.search_bar)

        # Refresh Button
        self.refresh_button = QtWidgets.QPushButton()
        self.refresh_button.setIcon(QtGui.QIcon("icons/refresh.png"))
        self.refresh_button.setFixedSize(40, 40)
        self.refresh_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2c2c2c;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #1e90ff;
            }
        """
        )
        self.refresh_button.clicked.connect(self.refresh_courses)
        search_layout.addWidget(self.refresh_button)

        self.layout.addLayout(search_layout)

        # Scroll Area
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(
            """
            QScrollArea {
                background-color: #1e1e1e;
                border-radius: 10px;
            }
            /* Scrollbar styles omitted for brevity */
        """
        )
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
        self.all_courses = courses
        self.update_course_list()

    def update_course_list(self):
        search_text = self.search_bar.text().lower()
        if search_text:
            filtered_courses = [
                course
                for course in self.all_courses
                if search_text in course.get("shortname", "").lower()
                or search_text in course.get("fullname", "").lower()
            ]
        else:
            filtered_courses = self.all_courses

        # Sort courses: favorites first
        def course_sort_key(course):
            is_favorite = course["id"] in self.config.favorites
            return (0 if is_favorite else 1, course.get("shortname", ""))

        self.courses = sorted(filtered_courses, key=course_sort_key)
        self.populate_grid()

    def refresh_courses(self):
        self.loading_indicator = QtWidgets.QProgressDialog(
            "Refreshing courses...", None, 0, 0, self
        )
        self.loading_indicator.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.loading_indicator.show()

        # Fetch the list of courses first
        runnable = FetchCoursesRunnable(self.moodle_api)
        runnable.signals.courses_loaded.connect(self.on_courses_fetched_for_refresh)
        runnable.signals.error.connect(self.on_error)
        QtCore.QThreadPool.globalInstance().start(runnable)

    @QtCore.pyqtSlot(list)
    def on_courses_fetched_for_refresh(self, courses):
        self.all_courses = courses
        # Now fetch course states
        state_runnable = FetchCourseStatesRunnable(self.moodle_api, self.all_courses)
        state_runnable.signals.courses_loaded.connect(self.on_course_states_fetched)
        state_runnable.signals.error.connect(self.on_error)
        QtCore.QThreadPool.globalInstance().start(state_runnable)

    @QtCore.pyqtSlot(list)
    def on_course_states_fetched(self, results):
        self.loading_indicator.close()
        # Process the results
        for result in results:
            course_id = result["course_id"]
            current_state = result["state"]
            saved_state = self.config.get_course_state(course_id)
            course = next((c for c in self.all_courses if c["id"] == course_id), None)
            if course:
                if saved_state != current_state:
                    course["has_update"] = True
                    self.config.update_course_state(course_id, current_state)
                else:
                    course["has_update"] = False
        self.update_course_list()

    @QtCore.pyqtSlot()
    def on_error(self):
        self.loading_indicator.close()
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
        tile_width = 300  # Width of each CourseTile
        spacing = self.grid.spacing()
        columns = max(1, available_width // (tile_width + spacing))

        # Limit to 4 columns for better display
        columns = min(columns, 4)

        # Populate grid
        row = 0
        col = 0
        for course in self.courses:
            tile = CourseTile(course, self.token, self.config)
            tile.clicked.connect(self.on_tile_clicked)
            tile.favorite_changed.connect(self.update_course_list)
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
        # Clear the update flag
        course["has_update"] = False
        self.config.update_course_state(
            course["id"], self.config.get_course_state(course["id"])
        )
        self.update_course_list()
        self.course_selected.emit(course)
