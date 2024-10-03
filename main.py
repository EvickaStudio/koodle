import sys
import os
import pickle
from PyQt6 import QtWidgets, QtCore
from src.gui.main_window import MainWindow
from src.gui.login_dialog import LoginDialog
from src.moodle import MoodleAPI

# Function to save token
def save_token(token):
    with open("token.pkl", "wb") as f:
        pickle.dump(token, f)

# Function to load token
def load_token():
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as f:
            return pickle.load(f)
    return None

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Load stylesheet
    with open("src/gui/styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    moodle_api = MoodleAPI("https://lernraum.th-luebeck.de/")

    token = load_token()
    if token:
        moodle_api.token = token
        moodle_api.userid = moodle_api.get_user_id()
    else:
        login_dialog = LoginDialog(moodle_api)
        if login_dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            sys.exit(app.exec())
        save_token(moodle_api.token)

    main_window = MainWindow(moodle_api, token)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
