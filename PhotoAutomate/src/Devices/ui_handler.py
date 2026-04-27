from pathlib import Path

from PIL import Image
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QSizePolicy,
)


class PhotoBoothUI(QWidget):
    def __init__(
        self,
        on_start_session,
        on_capture_requested,
        on_delete_requested,
        on_print_requested,
    ):
        super().__init__()

        self.on_start_session = on_start_session
        self.on_capture_requested = on_capture_requested
        self.on_delete_requested = on_delete_requested
        self.on_print_requested = on_print_requested

        self.camera = None
        self._preview_running = False
        self._current_pixmap = None

        self.countdown_value = 5
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._update_countdown)

        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self._update_preview)

        self._build_base()
        self.show_welcome()

    def _build_base(self):
        self.setWindowTitle("Photo Automate")
        self.setStyleSheet("""
            QWidget {
                background-color: black;
                color: white;
            }

            QPushButton {
                background-color: black;
                color: white;
                border: 2px solid white;
                border-radius: 14px;
                padding: 12px 28px;
                font-size: 24px;
                min-width: 180px;
            }

            QPushButton:hover {
                background-color: #111111;
            }

            QPushButton:pressed {
                background-color: #222222;
            }
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.preview_container = QWidget()
        self.preview_stack = QStackedLayout()
        self.preview_stack.setStackingMode(QStackedLayout.StackAll)
        self.preview_container.setLayout(self.preview_stack)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_label.setStyleSheet("background-color: black;")
        self.preview_stack.addWidget(self.preview_label)

        self.overlay_label = QLabel()
        self.overlay_label.setAlignment(Qt.AlignCenter)
        self.overlay_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.overlay_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 160);
            color: white;
            font-size: 160px;
            font-weight: bold;
        """)
        self.overlay_label.hide()
        self.preview_stack.addWidget(self.overlay_label)

        root_layout.addWidget(self.preview_container, stretch=1)

        self.bottom = QWidget()
        self.bottom.setStyleSheet("background-color: black;")
        self.bottom_layout = QHBoxLayout(self.bottom)
        self.bottom_layout.setContentsMargins(20, 16, 20, 16)
        self.bottom_layout.setSpacing(20)
        self.bottom_layout.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(self.bottom, stretch=0)

    def _clear_bottom(self):
        while self.bottom_layout.count():
            item = self.bottom_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _pil_to_qpixmap(self, pil_img: Image.Image) -> QPixmap:
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        w, h = pil_img.size
        data = pil_img.tobytes("raw", "RGB")
        qimage = QImage(data, w, h, 3 * w, QImage.Format_RGB888)
        return QPixmap.fromImage(qimage)

    def _set_scaled_pixmap(self, pixmap: QPixmap):
        if pixmap.isNull():
            return

        self._current_pixmap = pixmap
        scaled = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)

    def _set_pixmap_from_pil(self, pil_img: Image.Image):
        pixmap = self._pil_to_qpixmap(pil_img)
        self._set_scaled_pixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._current_pixmap is not None:
            self._set_scaled_pixmap(self._current_pixmap)

    def show_welcome(self):
        self._stop_preview()
        self._clear_bottom()
        self._current_pixmap = None
        self.preview_label.clear()
        self.overlay_label.hide()

        self.preview_label.setText("Photo Automate\n\nTap to start your session")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFont(QFont("DejaVu Sans", 28, QFont.Bold))

        start_btn = QPushButton("START SESSION")
        start_btn.setFont(QFont("DejaVu Sans", 26, QFont.Bold))
        start_btn.clicked.connect(self.on_start_session)
        self.bottom_layout.addWidget(start_btn)

    def show_live_preview(self, camera):
        self._clear_bottom()
        self.camera = camera
        self._preview_running = True
        self.preview_label.clear()
        self.overlay_label.hide()
        self._current_pixmap = None

        capture_btn = QPushButton("📷")
        capture_btn.setFont(QFont("DejaVu Sans", 34))
        capture_btn.clicked.connect(self.start_countdown)
        self.bottom_layout.addWidget(capture_btn)

        self.preview_timer.start(33)

    def show_captured_image(self, image_path: Path):
        self._stop_preview()
        self._clear_bottom()
        self.overlay_label.hide()

        img = Image.open(image_path)
        img.thumbnail((1600, 900))
        self._set_pixmap_from_pil(img)

        print_btn = QPushButton("🖨 Print")
        print_btn.setFont(QFont("DejaVu Sans", 22, QFont.Bold))
        print_btn.clicked.connect(self.on_print_requested)

        delete_btn = QPushButton("🗑 Delete")
        delete_btn.setFont(QFont("DejaVu Sans", 22, QFont.Bold))
        delete_btn.clicked.connect(self.on_delete_requested)

        self.bottom_layout.addWidget(print_btn)
        self.bottom_layout.addWidget(delete_btn)

    def start_countdown(self):
        if self.countdown_timer.isActive():
            return

        self.countdown_value = 5
        self.overlay_label.setText(str(self.countdown_value))
        self.overlay_label.raise_()
        self.overlay_label.show()
        self.countdown_timer.start(1000)

    def _update_countdown(self):
        self.countdown_value -= 1

        if self.countdown_value > 0:
            self.overlay_label.setText(str(self.countdown_value))
            self.overlay_label.raise_()
        else:
            self.countdown_timer.stop()
            self.overlay_label.hide()
            self._stop_preview()
            self.on_capture_requested()

    def _update_preview(self):
        if not self._preview_running or self.camera is None:
            return

        try:
            frame = self.camera.get_preview_frame_rgb()
            img = Image.fromarray(frame)
            self._set_pixmap_from_pil(img)
        except Exception as exc:
            print(f"Preview error: {exc}")

    def _stop_preview(self):
        self._preview_running = False
        self.preview_timer.stop()