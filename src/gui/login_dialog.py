# gui/login_dialog.py

from PyQt6 import QtWidgets, QtCore
import pickle
import os


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, moodle_api, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Moodle Login")
        self.setFixedSize(300, 150)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Username
        self.username_edit = QtWidgets.QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        layout.addWidget(self.username_edit)

        # Password
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_edit)

        # Login Button
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        if self.moodle_api.login(username, password):
            QtWidgets.QMessageBox.information(self, "Success", "Login successful!")
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(
                self, "Error", "Login failed. Please check your credentials."
            )
