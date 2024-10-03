from PyQt6 import QtWidgets, QtGui, QtCore
import requests
import random


class ImageLoader(QtCore.QThread):
    image_loaded = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, url, token):
        super().__init__()
        self.url = f"{url}?token={token}"

    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()  # Ensure we notice bad responses
            pixmap = QtGui.QPixmap()
            if pixmap.loadFromData(response.content):
                print(f"Image loaded successfully from {self.url}")
                self.image_loaded.emit(pixmap)
            else:
                print(f"Failed to load image data from {self.url}")
                # Emit a default pixmap if loading fails
                pixmap = QtGui.QPixmap(180, 130)
                pixmap.fill(QtGui.QColor("gray"))
                self.image_loaded.emit(pixmap)
        except Exception as e:
            print(f"Failed to load image from {self.url}: {e}")
            pixmap = QtGui.QPixmap(180, 130)
            pixmap.fill(QtGui.QColor("gray"))
            self.image_loaded.emit(pixmap)


class CourseTile(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(dict)

    def __init__(self, course, token, parent=None):
        super().__init__(parent)
        self.course = course
        self.token = token
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(200, 150)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        # Create layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

        # Background Label
        self.background = QtWidgets.QLabel()
        self.background.setFixedSize(180, 130)
        self.background.setStyleSheet("border-radius: 10px; background-color: transparent;")
        self.background.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Start image loading thread
        if self.course.get("overviewfiles"):
            image_url = self.course["overviewfiles"][0].get("fileurl", "")
            if image_url:
                print(f"Loading image from {image_url}")
                self.loader = ImageLoader(image_url, self.token)
                self.loader.image_loaded.connect(self.set_background_image)
                self.loader.start()
            else:
                print("No image URL found in overviewfiles")
                self.set_random_background()
        else:
            print("No overviewfiles found for course")
            self.set_random_background()

        # Semi-transparent overlay to darken the background image
        self.overlay = QtWidgets.QWidget(self.background)
        self.overlay.setGeometry(0, 0, 180, 130)
        self.overlay.setStyleSheet(
            "background-color: rgba(0, 0, 0, 60); border-radius: 10px;"
        )

        # Overlay for text
        self.text_overlay = QtWidgets.QWidget(self.overlay)
        self.text_overlay.setGeometry(0, 0, 180, 130)
        self.text_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120); border-radius: 10px;")  # Increased opacity and added border-radius
        overlay_layout = QtWidgets.QVBoxLayout()
        overlay_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        )
        overlay_layout.setContentsMargins(10, 10, 10, 10)

        # Course Shortname
        self.shortname = QtWidgets.QLabel(self.course.get("shortname", ""))
        self.shortname.setStyleSheet(
            "color: white; font-weight: bold; font-size: 14px; background-color: transparent;"
        )
        # Course Fullname
        self.fullname = QtWidgets.QLabel(self.course.get("fullname", ""))
        # make background transparent
        self.fullname.setStyleSheet(
            "color: white; font-size: 10px; background-color: transparent;"
        )
        # Enrolled User Count
        self.enrolled = QtWidgets.QLabel(
            f"Enrolled: {self.course.get('enrolledusercount', 0)}"
        )
        self.enrolled.setStyleSheet(
            "color: white; font-size: 10px; background-color: transparent;"
        )

        # Add labels to overlay layout
        overlay_layout.addWidget(self.shortname)
        overlay_layout.addWidget(self.fullname)
        overlay_layout.addWidget(self.enrolled)

        self.text_overlay.setLayout(overlay_layout)

        # Add background to main layout
        main_layout.addWidget(self.background)

    def set_background_image(self, pixmap):
        if not pixmap.isNull():
            print("Setting background image")
            pixmap = pixmap.scaled(
                180,
                130,
                QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )

            # Apply blur effect
            blurred_pixmap = self.apply_blur_effect(pixmap)
            self.background.setPixmap(blurred_pixmap)
            self.background.setStyleSheet("border-radius: 10px;")  # Apply border-radius to the image
        else:
            print("Received null pixmap, setting default background")
            self.set_random_background()

    def apply_blur_effect(self, pixmap):
        # Create a QGraphicsScene to apply the blur effect
        scene = QtWidgets.QGraphicsScene()
        item = QtWidgets.QGraphicsPixmapItem(pixmap)
        scene.addItem(item)

        # Apply blur effect
        blur_effect = QtWidgets.QGraphicsBlurEffect()
        blur_effect.setBlurRadius(1.5)  # Reduced blur radius
        item.setGraphicsEffect(blur_effect)

        # Render the scene to a new pixmap
        blurred_pixmap = QtGui.QPixmap(pixmap.size())
        blurred_pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(blurred_pixmap)
        scene.render(painter)
        painter.end()

        return blurred_pixmap

    def set_random_background(self):
        print("Setting random background")
        pixmap = QtGui.QPixmap(180, 130)
        random_color = QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pixmap.fill(random_color)
        self.background.setPixmap(pixmap)
        self.background.setStyleSheet("border-radius: 10px;")  # Apply border-radius to the random background

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        path = QtGui.QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        painter.setClipPath(path)
        super().paintEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit(self.course)