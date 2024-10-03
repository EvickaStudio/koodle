from PyQt6 import QtWidgets, QtCore, QtGui
import os

class DownloadItemWidget(QtWidgets.QWidget):
    download_requested = QtCore.pyqtSignal(str, str)

    def __init__(self, filename, filesize, fileurl, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.filesize = filesize
        self.fileurl = fileurl
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # File Icon
        icon_label = QtWidgets.QLabel()
        icon = self.get_icon_for_file(self.filename)
        icon_label.setPixmap(icon.pixmap(32, 32))
        layout.addWidget(icon_label)

        # File Name Label
        self.name_label = QtWidgets.QLabel(self.filename)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.name_label, stretch=3)

        # File Size Label
        readable_size = self.human_readable_size(self.filesize)
        self.size_label = QtWidgets.QLabel(readable_size)
        self.size_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.size_label.setStyleSheet("color: #d4d4d4;")
        layout.addWidget(self.size_label, stretch=1)

        # Download Button
        self.download_button = QtWidgets.QPushButton("Download")
        self.download_button.setFixedSize(100, 30)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.download_button.clicked.connect(self.on_download_clicked)
        layout.addWidget(self.download_button, stretch=1)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #2c2c2c; border-radius: 5px;")
        self.setMaximumHeight(60)

    def on_download_clicked(self):
        self.download_requested.emit(self.filename, self.fileurl)

    @staticmethod
    def human_readable_size(size, decimal_places=2):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024.0
        return f"{size:.{decimal_places}f} PB"

    def get_icon_for_file(self, filename):
        extension = os.path.splitext(filename)[1].lower()
        if extension == ".pdf":
            icon_path = "icons/pdf_icon.png"
        elif extension == ".zip":
            icon_path = "icons/zip_icon.png"
        else:
            icon_path = "icons/file_icon.png"

        if os.path.exists(icon_path):
            return QtGui.QIcon(icon_path)
        else:
            return QtGui.QIcon()
