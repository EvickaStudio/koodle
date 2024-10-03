from PyQt6 import QtWidgets, QtCore, QtGui

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, moodle_api, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Moodle Login")
        self.setFixedSize(350, 250)
        self.setWindowIcon(QtGui.QIcon("icons/login_icon.png"))

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Title
        title = QtWidgets.QLabel("Please Log In")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Username
        self.username_edit = QtWidgets.QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        self.username_edit.setStyleSheet("""
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
        layout.addWidget(self.username_edit)

        # Password
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet("""
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
        layout.addWidget(self.password_edit)

        # Login Button
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setFixedHeight(40)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # Add spacer
        layout.addStretch()

        self.setLayout(layout)
        self.setStyleSheet("background-color: #1e1e1e; border-radius: 10px;")

    def handle_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        # Show loading animation or disable inputs
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")

        # Perform login in a separate thread to avoid blocking UI
        self.login_thread = QtCore.QThread()
        self.login_worker = LoginWorker(self.moodle_api, username, password)
        self.login_worker.moveToThread(self.login_thread)
        self.login_thread.started.connect(self.login_worker.run)
        self.login_worker.finished.connect(self.on_login_finished)
        self.login_worker.finished.connect(self.login_thread.quit)
        self.login_worker.finished.connect(self.login_worker.deleteLater)
        self.login_thread.finished.connect(self.login_thread.deleteLater)
        self.login_thread.start()

    def on_login_finished(self, success, message):
        self.login_button.setEnabled(True)
        self.login_button.setText("Login")
        if success:
            QtWidgets.QMessageBox.information(self, "Success", "Login successful!")
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", f"Login failed: {message}")

class LoginWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(bool, str)

    def __init__(self, moodle_api, username, password):
        super().__init__()
        self.moodle_api = moodle_api
        self.username = username
        self.password = password

    def run(self):
        try:
            success = self.moodle_api.login(self.username, self.password)
            if success:
                self.finished.emit(True, "Login successful.")
            else:
                self.finished.emit(False, "Invalid credentials.")
        except Exception as e:
            self.finished.emit(False, str(e))
