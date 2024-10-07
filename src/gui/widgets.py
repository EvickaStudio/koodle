# Filename: widgets.py
from PyQt6 import QtWidgets, QtGui, QtCore
import requests
import random
import os


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
    favorite_changed = QtCore.pyqtSignal()

    def __init__(self, course, token, config, parent=None):
        super().__init__(parent)
        self.course = course
        self.token = token
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(300, 200)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        # Create main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Background Frame
        self.background = QtWidgets.QFrame()
        self.background.setStyleSheet(
            """
            QFrame {
                background-color: #2c2c2c;
                border-radius: 10px;
                border: 2px solid #444;
            }
        """
        )
        self.background.setFixedSize(300, 200)
        main_layout.addWidget(self.background)

        # Image Label
        self.image_label = QtWidgets.QLabel(self.background)
        self.image_label.setFixedSize(300, 130)
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            "border-top-left-radius: 10px; border-top-right-radius: 10px;"
        )

        # Overlay for Data Block
        self.data_block = QtWidgets.QFrame(self.background)
        self.data_block.setGeometry(0, 130, 300, 70)
        self.data_block.setStyleSheet(
            """
            QFrame {
                background-color: #3c3c3c;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                border: 1px solid #444;
            }
        """
        )

        data_layout = QtWidgets.QVBoxLayout()
        data_layout.setContentsMargins(10, 5, 10, 5)
        data_layout.setSpacing(5)
        self.data_block.setLayout(data_layout)

        # Course Shortname
        self.shortname = QtWidgets.QLabel(self.course.get("shortname", ""))
        self.shortname.setStyleSheet(
            """
            color: white; 
            font-weight: bold; 
            font-size: 16px; 
            background-color: #3c3c3c; 
            margin: 0px;
            padding: 0px;
            border: none;
            """
        )
        # Course Fullname
        self.fullname = QtWidgets.QLabel(self.course.get("fullname", ""))
        self.fullname.setStyleSheet(
            """
            color: #d4d4d4; 
            font-size: 12px; 
            background-color: #3c3c3c; 
            margin: 0px; 
            padding: 0px;
            border: none;
            """
        )
        # Enrolled User Count
        self.enrolled = QtWidgets.QLabel(
            f"Enrolled: {self.course.get('enrolledusercount', 0)}"
        )
        self.enrolled.setStyleSheet(
            """
            color: #d4d4d4; 
            font-size: 12px; 
            background-color: #3c3c3c; 
            margin: 0px; 
            padding: 0px;
            border: none;
            """
        )

        # Add labels to data layout
        data_layout.addWidget(self.shortname)
        data_layout.addWidget(self.fullname)
        data_layout.addWidget(self.enrolled)

        # Favorite button
        self.favorite_button = QtWidgets.QPushButton(self.background)
        self.favorite_button.setFixedSize(24, 24)
        self.favorite_button.move(self.width() - 34, 10)
        self.favorite_button.setStyleSheet(
            "background-color: transparent; border: none;"
        )
        self.favorite_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.update_favorite_status()
        self.favorite_button.clicked.connect(self.toggle_favorite)

        # Update indicator
        if self.course.get("has_update"):
            self.update_icon = QtWidgets.QLabel(self.background)
            self.update_icon.setFixedSize(24, 24)
            self.update_icon.move(10, 10)
            self.update_icon.setAttribute(
                QtCore.Qt.WidgetAttribute.WA_TranslucentBackground
            )
            icon_path = "icons/update.png"
            if os.path.exists(icon_path):
                icon = QtGui.QIcon(icon_path)
                pixmap = icon.pixmap(24, 24)
                self.update_icon.setPixmap(pixmap)
            else:
                self.update_icon.setPixmap(QtGui.QPixmap())
        else:
            self.update_icon = None

        # Load image or apply gradient/background
        if self.course.get("overviewfiles"):
            image_url = self.course["overviewfiles"][0].get("fileurl", "")
            if image_url:
                self.loader = ImageLoader(image_url, self.token)
                self.loader.image_loaded.connect(self.set_background_image)
                self.loader.load()
            else:
                self.apply_gradient_background()
        else:
            self.apply_gradient_background()

        # Event filter to capture clicks
        self.background.installEventFilter(self)

    def apply_gradient_background(self):
        # Apply a random gradient from two matching colors
        color1, color2 = self.generate_matching_colors()
        gradient_style = f"""
            QFrame {{
                background: qlineargradient(
                    spread:pad, 
                    x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {color1.name()}, 
                    stop:1 {color2.name()}
                );
                border-radius: 10px;
                border: 2px solid #444;
            }}
        """
        self.background.setStyleSheet(gradient_style)

    def generate_matching_colors(self):
        # Generate two random but matching colors for gradient
        base_color = QtGui.QColor(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )
        hue = base_color.hue()
        saturation = base_color.saturation()
        value = base_color.value()

        # Generate a second color with a slight hue shift
        hue_shift = random.randint(10, 30)
        new_hue = (hue + hue_shift) % 360
        color1 = QtGui.QColor.fromHsv(new_hue, saturation, value)
        color2 = QtGui.QColor.fromHsv(hue, saturation, value)

        return color1, color2

    def set_background_image(self, pixmap):
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            # Apply rounded corners to pixmap
            rounded_pixmap = self.apply_rounded_corners(pixmap, 10)
            self.image_label.setPixmap(rounded_pixmap)
            self.image_label.setStyleSheet(
                "border-top-left-radius: 10px; border-top-right-radius: 10px;"
            )
        else:
            self.apply_gradient_background()

    def apply_rounded_corners(self, pixmap, radius):
        size = pixmap.size()
        rounded = QtGui.QPixmap(size)
        rounded.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(rounded)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        path = QtGui.QPainterPath()
        path.addRoundedRect(
            QtCore.QRectF(0, 0, size.width(), size.height()), radius, radius
        )
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded

    def eventFilter(self, source, event):
        if (
            source is self.background
            and event.type() == QtCore.QEvent.Type.MouseButtonPress
        ):
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                # Check if click was on favorite button
                if not self.favorite_button.geometry().contains(event.pos()):
                    self.clicked.emit(self.course)
            return True
        return super().eventFilter(source, event)

    def update_favorite_status(self):
        if self.course["id"] in self.config.favorites:
            icon_path = "icons/star_filled_yellow.png"
        else:
            icon_path = "icons/star_outline_yellow.png"

        if os.path.exists(icon_path):
            icon = QtGui.QIcon(icon_path)
            self.favorite_button.setIcon(icon)
            self.favorite_button.setIconSize(QtCore.QSize(24, 24))
        else:
            self.favorite_button.setIcon(QtGui.QIcon())

    def toggle_favorite(self):
        if self.course["id"] in self.config.favorites:
            self.config.remove_favorite(self.course["id"])
        else:
            self.config.add_favorite(self.course["id"])
        self.update_favorite_status()
        self.favorite_changed.emit()
