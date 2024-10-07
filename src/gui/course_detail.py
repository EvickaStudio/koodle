# Filename: course_detail.py
from PyQt6 import QtWidgets, QtCore, QtGui
from .widgets import ImageLoader
from .download_item_widget import DownloadItemWidget
import requests
import webbrowser
from concurrent.futures import ThreadPoolExecutor


class CourseDetail(QtWidgets.QWidget):
    back_requested = QtCore.pyqtSignal()

    def __init__(self, moodle_api, course, token, parent=None):
        super().__init__(parent)
        self.moodle_api = moodle_api
        self.course = course
        self.token = token
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Back Button
        back_button = QtWidgets.QPushButton("← Back to Dashboard")
        back_button.setFixedHeight(40)
        back_button.setStyleSheet(
            """
            QPushButton {
                background-color: #d32121;
                color: white;
                border-radius: 10px;
                padding: 5px 10px;
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
        back_button.clicked.connect(self.back_requested.emit)
        layout.addWidget(back_button)

        # Main Content Layout (Image on Left, Text on Right)
        main_content = QtWidgets.QHBoxLayout()
        main_content.setSpacing(20)
        layout.addLayout(main_content)

        # Image Section
        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(250, 250)
        self.image_label.setStyleSheet("border-radius: 15px;")
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_content.addWidget(self.image_label)

        if self.course.get("overviewfiles"):
            image_url = self.course["overviewfiles"][0].get("fileurl", "")
            if image_url:
                self.loader = ImageLoader(image_url, self.moodle_api.token)
                self.loader.image_loaded.connect(self.set_course_image)
                self.loader.load()
            else:
                self.set_default_image()
        else:
            self.set_default_image()

        # Text Information Section
        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(10)

        shortname = QtWidgets.QLabel(f"<b>{self.course.get('shortname', '')}</b>")
        shortname.setStyleSheet("color: white; font-size: 22px;")
        fullname = QtWidgets.QLabel(self.course.get("fullname", ""))
        fullname.setStyleSheet("color: #d4d4d4; font-size: 16px;")
        enrolled = QtWidgets.QLabel(
            f"Enrolled Users: {self.course.get('enrolledusercount', 0)}"
        )
        enrolled.setStyleSheet("color: #d4d4d4; font-size: 16px;")
        info_layout.addWidget(shortname)
        info_layout.addWidget(fullname)
        info_layout.addWidget(enrolled)
        info_layout.addStretch()
        main_content.addLayout(info_layout)

        # Tab Widget
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane { 
                border: 1px solid #444; 
                background-color: #1e1e1e; 
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #2c2c2c;
                color: white;
                padding: 10px;
                margin: 2px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #007acc;
            }
        """
        )
        layout.addWidget(self.tabs)

        # Overview Tab
        self.overview_tab = QtWidgets.QWidget()
        self.overview_layout = QtWidgets.QVBoxLayout()
        self.overview_layout.setContentsMargins(15, 15, 15, 15)
        self.overview_tab.setLayout(self.overview_layout)
        self.tabs.addTab(self.overview_tab, "Overview")

        # Downloads Tab
        self.downloads_tab = QtWidgets.QWidget()
        self.downloads_layout = QtWidgets.QVBoxLayout()
        self.downloads_layout.setContentsMargins(15, 15, 15, 15)
        self.downloads_tab.setLayout(self.downloads_layout)
        self.tabs.addTab(self.downloads_tab, "Downloads")

        # Course Overview Content
        self.content_area = QtWidgets.QTextBrowser()
        self.content_area.setOpenExternalLinks(True)
        self.content_area.setStyleSheet(
            """
            QTextBrowser {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 10px;
                padding: 10px;
            }
        """
        )
        self.overview_layout.addWidget(self.content_area)

        # Populate Content and Downloads
        self.populate_content_and_downloads()

        self.setLayout(layout)

    def populate_content_and_downloads(self):
        # Fetch course content asynchronously
        self.executor.submit(self.fetch_course_content)

    def fetch_course_content(self):
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
            QtCore.QMetaObject.invokeMethod(
                self.content_area,
                "setHtml",
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(str, html),
            )
        else:
            QtCore.QMetaObject.invokeMethod(
                self.content_area,
                "setText",
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(str, "Could not load course content."),
            )

        # Populate the Downloads tab
        if self.downloadable_items:
            QtCore.QMetaObject.invokeMethod(
                self,
                "populate_downloads_tab",
                QtCore.Qt.ConnectionType.QueuedConnection,
            )
        else:
            QtCore.QMetaObject.invokeMethod(
                self, "show_no_downloads", QtCore.Qt.ConnectionType.QueuedConnection
            )

    @QtCore.pyqtSlot()
    def show_no_downloads(self):
        no_downloads_label = QtWidgets.QLabel("No downloadable content available.")
        no_downloads_label.setStyleSheet("color: #d4d4d4; font-size: 14px;")
        self.downloads_layout.addWidget(no_downloads_label)

    @QtCore.pyqtSlot()
    def populate_downloads_tab(self):
        # Create a scroll area to hold all download items
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #1e1e1e; border: none;")

        # Create a widget to contain the download items
        container = QtWidgets.QWidget()
        scroll_area.setWidget(container)

        # Use a vertical layout for the container
        v_layout = QtWidgets.QVBoxLayout()
        v_layout.setSpacing(10)
        container.setLayout(v_layout)

        # Add a DownloadItemWidget for each downloadable item
        for item in self.downloadable_items:
            filename = item["name"]
            fileurl = item["url"]
            filesize = item.get("size", 0)
            # add one space before filename
            filename = "   " + filename
            download_widget = DownloadItemWidget(filename, filesize, fileurl)
            download_widget.download_requested.connect(self.handle_download_requested)
            v_layout.addWidget(download_widget)

        # Add stretch to push items to the top
        v_layout.addStretch()
        self.downloads_layout.addWidget(scroll_area)

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
            self.executor.submit(self.download_file, fileurl, save_path)

    def download_file(self, url, save_path):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_length = response.headers.get("content-length")

            with open(save_path, "wb") as f:
                if total_length is None:
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            dl += len(chunk)
                            done = int(100 * dl / total_length)
                            self.update_download_progress(done)

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

    def update_download_progress(self, percent):
        # Could implement a progress bar update here
        pass  # Placeholder for progress update

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
                250,
                250,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(pixmap)
        else:
            self.set_default_image()

    def set_default_image(self):
        pixmap = QtGui.QPixmap(250, 250)
        pixmap.fill(QtGui.QColor("gray"))
        self.image_label.setPixmap(pixmap)

    def open_in_browser(self, url):
        webbrowser.open(url)
