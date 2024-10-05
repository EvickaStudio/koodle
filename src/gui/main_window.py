# Filename: main_window.py
from PyQt6 import QtWidgets, QtCore, QtGui
from .dashboard import Dashboard
from .course_detail import CourseDetail
from .settings import SettingsWidget
import os
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, moodle_api, token):
        super().__init__()
        self.moodle_api = moodle_api
        self.token = token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Moodle Desktop Client")
        self.resize(1400, 900)  # Increased window size for better layout

        # Central Widget with horizontal layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Sidebar
        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setFixedWidth(220)  # Increased width for better icons and labels
        self.sidebar.setStyleSheet("background-color: #2c2c2c; border-radius: 10px;")
        sidebar_layout = QtWidgets.QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(20)
        self.sidebar.setLayout(sidebar_layout)

        # Sidebar buttons
        self.dashboard_button = QtWidgets.QPushButton("Dashboard")
        self.dashboard_button.setIcon(QtGui.QIcon("icons/dashboard.png"))
        self.dashboard_button.setIconSize(QtCore.QSize(24, 24))
        self.dashboard_button.setFixedHeight(50)
        self.dashboard_button.setStyleSheet(self.get_sidebar_button_style())

        self.settings_button = QtWidgets.QPushButton("Settings")
        self.settings_button.setIcon(QtGui.QIcon("icons/settings.png"))
        self.settings_button.setIconSize(QtCore.QSize(24, 24))
        self.settings_button.setFixedHeight(50)
        self.settings_button.setStyleSheet(self.get_sidebar_button_style())

        self.logout_button = QtWidgets.QPushButton("Logout")
        self.logout_button.setIcon(QtGui.QIcon("icons/logout.png"))
        self.logout_button.setIconSize(QtCore.QSize(24, 24))
        self.logout_button.setFixedHeight(50)
        self.logout_button.setStyleSheet(self.get_sidebar_button_style())

        # Add buttons to sidebar
        sidebar_layout.addWidget(self.dashboard_button)
        sidebar_layout.addWidget(self.settings_button)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.logout_button)

        # Connect sidebar buttons
        self.dashboard_button.clicked.connect(self.show_dashboard)
        self.settings_button.clicked.connect(self.show_settings)
        self.logout_button.clicked.connect(self.logout)

        # Main content area with stacked layout
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setStyleSheet("background-color: #1e1e1e; border-radius: 10px;")

        # Dashboard View
        self.dashboard = Dashboard(self.moodle_api)
        self.dashboard.course_selected.connect(self.show_course_detail)
        self.stack.addWidget(self.dashboard)

        # Placeholder for Course Detail View
        self.course_detail = None

        # Settings View
        self.settings = SettingsWidget(self.moodle_api)
        self.settings.settings_saved.connect(self.handle_settings_saved)
        self.stack.addWidget(self.settings)

        # Add sidebar and stack to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        # Initially show Dashboard
        self.stack.setCurrentWidget(self.dashboard)

    def get_sidebar_button_style(self):
        return """
            QPushButton {
                background-color: #2c2c2c;
                color: white;
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #1e90ff;
            }
        """

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)

    def show_course_detail(self, course):
        if self.course_detail:
            self.stack.removeWidget(self.course_detail)
            self.course_detail.deleteLater()

        self.course_detail = CourseDetail(self.moodle_api, course, token=self.token)
        self.course_detail.back_requested.connect(self.show_dashboard)
        self.stack.addWidget(self.course_detail)

        # Transition animation
        self.stack.setCurrentWidget(self.course_detail)

    def show_settings(self):
        self.stack.setCurrentWidget(self.settings)

    def handle_settings_saved(self):
        # Optionally, switch back to Dashboard or prompt restart
        self.show_dashboard()

    def logout(self):
        reply = QtWidgets.QMessageBox.question(
            self,
            'Logout',
            "Are you sure you want to logout?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Remove token and restart the application
            if os.path.exists("token.pkl"):
                os.remove("token.pkl")
            QtCore.QCoreApplication.quit()
            os.execl(sys.executable, sys.executable, *sys.argv)
