# gui/course_detail.py

from PyQt6 import QtWidgets, QtCore, QtGui
from .widgets import ImageLoader
from .download_item_widget import DownloadItemWidget  # Ensure this import is correct
import requests
import webbrowser
import threading
from urllib.parse import urljoin


class CourseDetail(QtWidgets.QWidget):
    back_requested = QtCore.pyqtSignal()

    def __init__(self, moodle_api, course, token, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.course = course
        self.token = token
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Back Button
        back_button = QtWidgets.QPushButton("← Back to Dashboard")
        back_button.clicked.connect(self.back_requested.emit)
        layout.addWidget(back_button)

        # Course Header with Image
        header = QtWidgets.QHBoxLayout()

        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(100, 100)
        self.image_label.setStyleSheet("border-radius: 10px;")
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.image_label)

        if self.course.get("overviewfiles"):
            image_url = self.course["overviewfiles"][0].get("fileurl", "")
            if image_url:
                self.loader = ImageLoader(image_url, self.moodle_api.token)
                self.loader.image_loaded.connect(self.set_course_image)
                self.loader.start()
            else:
                self.set_default_image()
        else:
            self.set_default_image()

        # Course Information
        info_layout = QtWidgets.QVBoxLayout()
        shortname = QtWidgets.QLabel(f"<b>{self.course.get('shortname', '')}</b>")
        shortname.setStyleSheet("font-size: 16px;")
        fullname = QtWidgets.QLabel(self.course.get("fullname", ""))
        fullname.setStyleSheet("font-size: 12px;")
        enrolled = QtWidgets.QLabel(
            f"Enrolled Users: {self.course.get('enrolledusercount', 0)}"
        )
        enrolled.setStyleSheet("font-size: 12px;")
        info_layout.addWidget(shortname)
        info_layout.addWidget(fullname)
        info_layout.addWidget(enrolled)
        header.addLayout(info_layout)

        layout.addLayout(header)

        # Tab Widget
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
        layout.addWidget(self.tabs)

        # Overview Tab
        self.overview_tab = QtWidgets.QWidget()
        self.overview_layout = QtWidgets.QVBoxLayout()
        self.overview_layout.setContentsMargins(0, 0, 0, 0)
        self.overview_tab.setLayout(self.overview_layout)
        self.tabs.addTab(self.overview_tab, "Overview")

        # Downloads Tab
        self.downloads_tab = QtWidgets.QWidget()
        self.downloads_layout = QtWidgets.QVBoxLayout()
        self.downloads_layout.setContentsMargins(0, 0, 0, 0)
        self.downloads_tab.setLayout(self.downloads_layout)
        self.tabs.addTab(self.downloads_tab, "Downloads")

        # Course Overview Content
        self.content_area = QtWidgets.QTextBrowser()
        self.content_area.setOpenExternalLinks(True)  # Allow opening links in browser
        self.overview_layout.addWidget(self.content_area)

        # Populate Content and Downloads
        self.populate_content_and_downloads()

        self.setLayout(layout)

    def populate_content_and_downloads(self):
        # Fetch course content
        contents = self.moodle_api.get_course_content(self.course["id"])
        html = ""

        # Include course summary if it's not empty or minimal
        summary = self.course.get("summary", "")
        if summary.strip() and summary.strip() != "<p><br></p>":
            html += f"{summary}<br><hr>"

        # Prepare a list to hold downloadable items
        self.downloadable_items = []

        if contents:
            for section in contents:
                section_name = section.get("name", "").strip()
                section_summary = section.get("summary", "").strip()

                if section_name:
                    html += f"<h2>{section_name}</h2>"

                if section_summary and section_summary != "<p><br></p>":
                    html += f"{section_summary}<br>"

                modules = section.get("modules", [])
                for module in modules:
                    module_name = module.get("name", "").strip()
                    module_description = module.get("description", "").strip()
                    module_url = module.get("url", "")

                    if module_name:
                        if module_url:
                            html += f"<h3><a href='{module_url}'>{module_name}</a></h3>"
                        else:
                            html += f"<h3>{module_name}</h3>"

                    if module_description and module_description != "<p><br></p>":
                        html += f"{module_description}<br><br>"

                    # Extract downloadable content
                    contents_info = module.get("contents", [])
                    for content in contents_info:
                        if content.get("type") == "file":
                            filename = content.get("filename")
                            fileurl = content.get("fileurl")
                            if filename and fileurl:
                                # Append the token to the file URL for authentication
                                authenticated_url = f"{fileurl}&token={self.token}"
                                self.downloadable_items.append(
                                    {
                                        "name": filename,
                                        "url": authenticated_url,
                                        "size": content.get("filesize", 0),
                                    }
                                )
                        elif content.get("type") == "url":
                            # Optional: Handle downloadable URLs if necessary
                            pass  # Currently, URLs are handled in the Overview

                html += "<hr>"

        else:
            html += "Could not load course content."

        # Set the HTML content in the Overview tab
        if html:
            self.content_area.setHtml(html)
        else:
            self.content_area.setText("Could not load course content.")

        # Populate the Downloads tab
        if self.downloadable_items:
            self.populate_downloads_tab()
        else:
            no_downloads_label = QtWidgets.QLabel("No downloadable content available.")
            self.downloads_layout.addWidget(no_downloads_label)

    def populate_downloads_tab(self):
        # Create a scroll area to hold all download items
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.downloads_layout.addWidget(scroll_area)

        # Create a widget to contain the download items
        container = QtWidgets.QWidget()
        scroll_area.setWidget(container)

        # Use a vertical layout for the container
        v_layout = QtWidgets.QVBoxLayout()
        container.setLayout(v_layout)

        # Add a DownloadItemWidget for each downloadable item
        for item in self.downloadable_items:
            filename = item["name"]
            fileurl = item["url"]
            filesize = item.get("size", 0)

            download_widget = DownloadItemWidget(filename, filesize, fileurl)
            download_widget.download_requested.connect(self.handle_download_requested)
            v_layout.addWidget(download_widget)

            # Add the "Open in Browser" button
            open_button = QtWidgets.QPushButton("Open in Browser")
            open_button.clicked.connect(lambda _, url=fileurl: self.open_in_browser(url))
            v_layout.addWidget(open_button)

        # Add stretch to push items to the top
        v_layout.addStretch()

    def handle_download_requested(self, filename, fileurl):
        # Open a standard file dialog to choose the download location
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save File",
            filename,
            "All Files (*);;PDF Files (*.pdf);;ZIP Files (*.zip)",
        )
        if save_path:
            # Start the download in a separate thread
            thread = threading.Thread(
                target=self.download_file, args=(fileurl, save_path)
            )
            thread.start()

    def download_file(self, url, save_path):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            # Notify the user upon successful download
            QtCore.QMetaObject.invokeMethod(
                self,
                "show_download_success",
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(str, save_path),
            )
        except requests.exceptions.RequestException as e:
            # Notify the user about the download failure
            QtCore.QMetaObject.invokeMethod(
                self,
                "show_download_error",
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(str, str(e)),
            )

    @QtCore.pyqtSlot(str)
    def show_download_success(self, save_path):
        QtWidgets.QMessageBox.information(
            self, "Download Complete", f"File successfully downloaded to:\n{save_path}"
        )

    @QtCore.pyqtSlot(str)
    def show_download_error(self, error_message):
        QtWidgets.QMessageBox.critical(
            self,
            "Download Failed",
            f"An error occurred during download:\n{error_message}",
        )

    def human_readable_size(self, size, decimal_places=2):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024.0
        return f"{size:.{decimal_places}f} PB"

    def set_course_image(self, pixmap):
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                100,
                100,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(pixmap)
        else:
            self.set_default_image()

    def set_default_image(self):
        pixmap = QtGui.QPixmap(100, 100)
        pixmap.fill(QtGui.QColor("gray"))
        self.image_label.setPixmap(pixmap)

    def open_in_browser(self, url):
        webbrowser.open(url)