# gui/main_window.py

from PyQt6 import QtWidgets, QtCore
from .dashboard import Dashboard
from .course_detail import CourseDetail


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, moodle_api, token):
        super().__init__()
        self.moodle_api = moodle_api
        self.token = token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Moodle Desktop Client")
        self.resize(1000, 700)

        # Central Widget with Stacked Layout
        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Dashboard View
        self.dashboard = Dashboard(self.moodle_api)  # Pass moodle_api to Dashboard
        self.dashboard.course_selected.connect(self.show_course_detail)
        self.central_widget.addWidget(self.dashboard)

        # Placeholder for Course Detail View
        self.course_detail = None

        # Initially show Dashboard
        self.central_widget.setCurrentWidget(self.dashboard)

    def show_course_detail(self, course):
        if self.course_detail:
            self.central_widget.removeWidget(self.course_detail)
            self.course_detail.deleteLater()

        self.course_detail = CourseDetail(self.moodle_api, course, token=self.token)
        self.course_detail.back_requested.connect(self.show_dashboard)
        self.central_widget.addWidget(self.course_detail)
        self.central_widget.setCurrentWidget(self.course_detail)

    def show_dashboard(self):
        self.central_widget.setCurrentWidget(self.dashboard)
