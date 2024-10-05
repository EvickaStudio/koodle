# Filename: settings.py
from PyQt6 import QtWidgets, QtCore, QtGui

class SettingsWidget(QtWidgets.QWidget):
    settings_saved = QtCore.pyqtSignal()

    def __init__(self, moodle_api, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QtWidgets.QLabel("Settings")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Moodle URL
        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.setPlaceholderText("Moodle URL")
        self.url_edit.setText(self.moodle_api.url)
        self.url_edit.setStyleSheet("""
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
        """)
        layout.addWidget(QtWidgets.QLabel("Moodle URL:"))
        layout.addWidget(self.url_edit)

        # Save Button
        save_button = QtWidgets.QPushButton("Save Settings")
        save_button.setFixedHeight(40)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        # Add spacer
        layout.addStretch()

        self.setLayout(layout)

    def save_settings(self):
        new_url = self.url_edit.text().strip()
        if not new_url:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Moodle URL cannot be empty.")
            return
        self.moodle_api.url = new_url
        # Optionally, reset token and require re-login
        self.moodle_api.token = None
        QtWidgets.QMessageBox.information(self, "Settings Saved", "Settings have been saved. Please restart the application.")
        self.settings_saved.emit()
