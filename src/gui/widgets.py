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
            response.raise_for_status()
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
        self.setFixedSize(250, 180)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        # Create layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Background Label
        self.background = QtWidgets.QLabel()
        self.background.setFixedSize(250, 180)
        self.background.setStyleSheet("border-radius: 10px; background-color: #2c2c2c;")
        self.background.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.background)

        # Start image loading thread
        if self.course.get("overviewfiles"):
            image_url = self.course["overviewfiles"][0].get("fileurl", "")
            if image_url:
                print(f"Loading image from {image_url}")
                self.loader = ImageLoader(image_url, self.token)
                self.loader.image_loaded.connect(self.set_background_image)
                self.loader.start()
            else:
                self.set_random_background()
        else:
            self.set_random_background()

        # Overlay for text
        self.overlay = QtWidgets.QWidget(self.background)
        self.overlay.setGeometry(0, 0, 250, 180)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 80); border-radius: 10px;")

        overlay_layout = QtWidgets.QVBoxLayout()
        overlay_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        overlay_layout.setContentsMargins(10, 0, 10, 10)

        # Course Shortname
        self.shortname = QtWidgets.QLabel(self.course.get("shortname", ""))
        self.shortname.setStyleSheet(
            "color: white; font-weight: bold; font-size: 16px; background-color: transparent;"
        )
        # Course Fullname
        self.fullname = QtWidgets.QLabel(self.course.get("fullname", ""))
        self.fullname.setStyleSheet(
            "color: #d4d4d4; font-size: 12px; background-color: transparent;"
        )
        # Enrolled User Count
        self.enrolled = QtWidgets.QLabel(
            f"Enrolled: {self.course.get('enrolledusercount', 0)}"
        )
        self.enrolled.setStyleSheet(
            "color: #d4d4d4; font-size: 12px; background-color: transparent;"
        )

        # Add labels to overlay layout
        overlay_layout.addWidget(self.shortname)
        overlay_layout.addWidget(self.fullname)
        overlay_layout.addWidget(self.enrolled)

        self.overlay.setLayout(overlay_layout)

        # Add hover effect
        self.hover_animation = QtCore.QPropertyAnimation(self.overlay, b"windowOpacity")
        self.hover_animation.setDuration(300)
        self.hover_animation.setStartValue(0.8)
        self.hover_animation.setEndValue(1.0)

    def set_background_image(self, pixmap):
        if not pixmap.isNull():
            print("Setting background image")
            pixmap = pixmap.scaled(
                250,
                180,
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
        blur_effect.setBlurRadius(2.0)
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
        pixmap = QtGui.QPixmap(250, 180)
        random_color = QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pixmap.fill(random_color)
        self.background.setPixmap(pixmap)
        self.background.setStyleSheet("border-radius: 10px;")  # Apply border-radius to the random background

    def enterEvent(self, event):
        self.hover_animation.setDirection(QtCore.QAbstractAnimation.Direction.Forward)
        self.hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_animation.setDirection(QtCore.QAbstractAnimation.Direction.Backward)
        self.hover_animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit(self.course)
