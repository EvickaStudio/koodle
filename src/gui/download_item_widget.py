# gui/download_item_widget.py

from PyQt6 import QtWidgets, QtCore, QtGui
import os


class DownloadItemWidget(QtWidgets.QWidget):
    download_requested = QtCore.pyqtSignal(str, str)  # filename, fileurl

    def __init__(self, filename, filesize, fileurl, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.filesize = filesize
        self.fileurl = fileurl
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # File Icon
        icon_label = QtWidgets.QLabel()
        icon = self.get_icon_for_file(self.filename)
        icon_label.setPixmap(icon.pixmap(24, 24))
        layout.addWidget(icon_label)

        # File Name Label
        self.name_label = QtWidgets.QLabel(self.filename)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.name_label, stretch=3)

        # File Size Label
        readable_size = self.human_readable_size(self.filesize)
        self.size_label = QtWidgets.QLabel(readable_size)
        self.size_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.size_label, stretch=1)

        # Download Button
        self.download_button = QtWidgets.QPushButton("Download")
        self.download_button.clicked.connect(self.on_download_clicked)
        layout.addWidget(self.download_button, stretch=1)

        self.setLayout(layout)

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
        # Determine the icon based on the file extension
        extension = os.path.splitext(filename)[1].lower()
        if extension == ".pdf":
            icon_path = "icons/pdf_icon.png"
        elif extension == ".zip":
            icon_path = "icons/zip_icon.png"
        else:
            icon_path = "icons/file_icon.png"  # Generic file icon

        if os.path.exists(icon_path):
            return QtGui.QIcon(icon_path)
        else:
            return QtGui.QIcon()  # Return an empty icon if not found
