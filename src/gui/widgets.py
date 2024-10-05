# Filename: widgets.py
from PyQt6 import QtWidgets, QtGui, QtCore
import requests
import random

class ImageCache:
    _cache = {}

    @classmethod
    def get(cls, url):
        return cls._cache.get(url)

    @classmethod
    def add(cls, url, pixmap):
        cls._cache[url] = pixmap

class ImageLoaderSignals(QtCore.QObject):
    image_loaded = QtCore.pyqtSignal(QtGui.QPixmap)

class ImageLoaderRunnable(QtCore.QRunnable):
    def __init__(self, url, token):
        super().__init__()
        self.url = f"{url}?token={token}"
        self.signals = ImageLoaderSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            pixmap = QtGui.QPixmap()
            if pixmap.loadFromData(response.content):
                ImageCache.add(self.url, pixmap)
                self.signals.image_loaded.emit(pixmap)
            else:
                pixmap = QtGui.QPixmap(180, 130)
                pixmap.fill(QtGui.QColor("gray"))
                self.signals.image_loaded.emit(pixmap)
        except Exception as e:
            print(f"Failed to load image from {self.url}: {e}")
            pixmap = QtGui.QPixmap(180, 130)
            pixmap.fill(QtGui.QColor("gray"))
            self.signals.image_loaded.emit(pixmap)

class ImageLoader(QtCore.QObject):
    image_loaded = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, url, token):
        super().__init__()
        self.url = url
        self.token = token
        self.threadpool = QtCore.QThreadPool.globalInstance()

    def load(self):
        cached_pixmap = ImageCache.get(f"{self.url}?token={self.token}")
        if cached_pixmap:
            self.image_loaded.emit(cached_pixmap)
            return

        runnable = ImageLoaderRunnable(self.url, self.token)
        runnable.signals.image_loaded.connect(self.image_loaded.emit)
        self.threadpool.start(runnable)

class CourseTile(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(dict)

    def __init__(self, course, token, parent=None):
        super().__init__(parent)
        self.course = course
        self.token = token
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(300, 200)  # Increased width for better name visibility
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        # Create layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Background Label
        self.background = QtWidgets.QLabel()
        self.background.setFixedSize(300, 200)
        self.background.setStyleSheet("border-radius: 10px; background-color: #2c2c2c;")
        self.background.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.background)

        # Start image loading thread
        if self.course.get("overviewfiles"):
            image_url = self.course["overviewfiles"][0].get("fileurl", "")
            if image_url:
                self.loader = ImageLoader(image_url, self.token)
                self.loader.image_loaded.connect(self.set_background_image)
                self.loader.load()
            else:
                self.set_random_background()
        else:
            self.set_random_background()

        # Overlay for text
        self.overlay = QtWidgets.QWidget(self.background)
        self.overlay.setGeometry(0, 0, 300, 200)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150); border-radius: 10px;")

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
            pixmap = pixmap.scaled(
                300,
                200,
                QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            # Apply rounded corners to pixmap
            rounded_pixmap = self.apply_rounded_corners(pixmap, 10)
            self.background.setPixmap(rounded_pixmap)
            self.background.setStyleSheet("border-radius: 10px;")  # Ensure border-radius is applied
        else:
            self.set_random_background()

    def apply_rounded_corners(self, pixmap, radius):
        size = pixmap.size()
        rounded = QtGui.QPixmap(size)
        rounded.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(rounded)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(0, 0, size.width(), size.height()), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded

    def set_random_background(self):
        pixmap = QtGui.QPixmap(300, 200)
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
