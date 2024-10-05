# Filename: download_item_widget.py
from PyQt6 import QtWidgets, QtCore, QtGui
import os

class DownloadItemWidget(QtWidgets.QWidget):
    download_requested = QtCore.pyqtSignal(str, str)

    def __init__(self, filename, filesize, fileurl, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.filesize = filesize
        self.fileurl = fileurl

        # Check if the file size is 0 bytes
        if filesize == 0:
            return  # Skip creating the widget if the file size is 0

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

        # File Name and Size
        name_size_layout = QtWidgets.QVBoxLayout()
        self.name_label = QtWidgets.QLabel(self.filename)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("color: white; font-weight: bold;")
        readable_size = self.human_readable_size(self.filesize)
        self.size_label = QtWidgets.QLabel(readable_size)
        self.size_label.setStyleSheet("color: #d4d4d4;")
        name_size_layout.addWidget(self.name_label)
        name_size_layout.addWidget(self.size_label)
        layout.addLayout(name_size_layout)

        # Action Buttons
        buttons_layout = QtWidgets.QVBoxLayout()
        self.download_button = QtWidgets.QPushButton("Download")
        self.download_button.setFixedSize(120, 40)
        self.download_button.setStyleSheet(
            """
            QPushButton {
                background-color: #d32121;
                color: white;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b12c1c;
            }
            QPushButton:pressed {
                background-color: #b12c1c;
            }
        """
        )
        self.download_button.clicked.connect(self.on_download_clicked)

        self.open_button = QtWidgets.QPushButton("Open in Browser")
        self.open_button.setFixedSize(120, 40)
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
            QPushButton:pressed {
                background-color: #0063b1;
            }
        """)
        self.open_button.clicked.connect(
            lambda _, url=self.fileurl: self.open_in_browser(url)
        )

        buttons_layout.addWidget(self.download_button)
        buttons_layout.addWidget(self.open_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #2c2c2c; border-radius: 10px;")
        self.setMaximumHeight(100)

    def on_download_clicked(self):
        self.download_requested.emit(self.filename, self.fileurl)

    @staticmethod
    def human_readable_size(size, decimal_places=2):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"   {size:.{decimal_places}f} {unit}"
            size /= 1024.0
        return f"   {size:.{decimal_places}f} PB"

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

    def open_in_browser(self, url):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
