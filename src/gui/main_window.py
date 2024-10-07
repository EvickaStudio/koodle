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
        self.dashboard_button.clicked.connect(self.open_dashboard_tab)
        self.settings_button.clicked.connect(self.open_settings_tab)
        self.logout_button.clicked.connect(self.logout)

        # Main content area with QTabWidget
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setStyleSheet(
            """
            /* QTabWidget Pane */
            QTabWidget::pane { 
                border: 1px solid #444; 
                background-color: #1e1e1e; 
                border-radius: 10px;
            }

            /* QTabBar Tabs */
            QTabBar::tab {
                background: #2c2c2c;
                color: white;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 5px;
                min-width: 120px;
                height: 30px;
            }

            /* Selected Tab */
            QTabBar::tab:selected {
                background: #007acc;
            }
        """
        )

        # Add QTabWidget to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.tab_widget)

        # Connect tab close signal
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Open Dashboard tab by default
        self.open_dashboard_tab()

    def get_sidebar_button_style(self):
        return """
            QPushButton {
                background-color: #2c2c2c;
                color: white;
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

    def open_dashboard_tab(self):
        # Check if Dashboard tab already exists
        for index in range(self.tab_widget.count()):
            if self.tab_widget.tabText(index) == "Dashboard":
                self.tab_widget.setCurrentIndex(index)
                return

        dashboard = Dashboard(self.moodle_api)
        dashboard.course_selected.connect(self.open_course_detail_tab)
        self.tab_widget.addTab(dashboard, "Dashboard")
        self.tab_widget.setCurrentWidget(dashboard)

    def open_settings_tab(self):
        # Check if Settings tab already exists
        for index in range(self.tab_widget.count()):
            if self.tab_widget.tabText(index) == "Settings":
                self.tab_widget.setCurrentIndex(index)
                return

        settings = SettingsWidget(self.moodle_api)
        settings.settings_saved.connect(self.handle_settings_saved)
        self.tab_widget.addTab(settings, "Settings")
        self.tab_widget.setCurrentWidget(settings)

    def open_course_detail_tab(self, course):
        course_name = course.get("shortname", "Course Detail")
        # Create a unique tab name
        tab_name = course_name
        existing_tabs = [
            self.tab_widget.tabText(i) for i in range(self.tab_widget.count())
        ]
        if tab_name in existing_tabs:
            index = existing_tabs.index(tab_name)
            self.tab_widget.setCurrentIndex(index)
            return

        course_detail = CourseDetail(self.moodle_api, course, token=self.token)
        course_detail.back_requested.connect(self.close_current_tab)
        self.tab_widget.addTab(course_detail, tab_name)
        self.tab_widget.setCurrentWidget(course_detail)

    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.removeTab(current_index)

    def close_tab(self, index):
        # Prevent closing Dashboard and Settings tabs
        tab_name = self.tab_widget.tabText(index)
        if tab_name in ["Dashboard", "Settings"]:
            QtWidgets.QMessageBox.information(
                self, "Info", f"The '{tab_name}' tab cannot be closed."
            )
            return
        self.tab_widget.removeTab(index)

    def handle_settings_saved(self):
        # Optionally, switch back to Dashboard or prompt restart
        self.open_dashboard_tab()

    def logout(self):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Remove token and restart the application
            if os.path.exists("token.pkl"):
                os.remove("token.pkl")
            QtCore.QCoreApplication.quit()
            os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    moodle_api = None  # Replace with actual Moodle API instance
    token = None  # Replace with actual token
    main_window = MainWindow(moodle_api, token)
    main_window.show()
    sys.exit(app.exec())