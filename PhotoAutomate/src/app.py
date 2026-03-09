import logging
import signal
import sys
from pathlib import Path

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from Devices.camera_handler import CameraHandler, CaptureConfig
from Devices.ui_handler import PhotoBoothUI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class PhotoBoothApp:
    def __init__(self) -> None:
        self.camera = CameraHandler(
            CaptureConfig(
                photos_dir_name="photos",
                file_prefix="arducam",
                preview_size=(1280, 720),
                capture_size=(4608, 3472),
                warmup_seconds=1.0,
            )
        )

        self.qt_app = QApplication(sys.argv)

        self.last_photo: Path | None = None

        self.ui = PhotoBoothUI(
            on_start_session=self.start_session,
            on_capture_requested=self.capture_photo,
            on_delete_requested=self.delete_photo,
            on_print_requested=self.print_photo,
        )

        self.ui.showFullScreen()

        signal.signal(signal.SIGINT, self._on_signal)
        signal.signal(signal.SIGTERM, self._on_signal)

    def _on_signal(self, signum, frame):
        logging.info("Signal %s received, shutting down", signum)
        QTimer.singleShot(0, self.shutdown)

    def run(self) -> None:
        logging.info("Starting PhotoBooth application")
        self.qt_app.exec_()

    def start_session(self) -> None:
        logging.info("Starting session")
        try:
            self.camera.open()
            self.ui.show_live_preview(self.camera)
        except Exception:
            logging.exception("Failed to open camera")

    def capture_photo(self) -> None:
        logging.info("Capture requested")
        try:
            self.last_photo = self.camera.capture_photo()
            logging.info("Saved: %s", self.last_photo)
            self.ui.show_captured_image(self.last_photo)
        except Exception:
            logging.exception("Capture failed")

    def delete_photo(self) -> None:
        logging.info("Delete requested")
        if self.last_photo and self.last_photo.exists():
            try:
                self.last_photo.unlink()
            except Exception:
                pass
        self.last_photo = None
        self.ui.show_live_preview(self.camera)

    def print_photo(self) -> None:
        logging.info("Print requested (not implemented yet)")

    def shutdown(self) -> None:
        logging.info("Shutting down")
        try:
            self.camera.close()
        except Exception:
            pass
        try:
            self.ui.close()
        except Exception:
            pass
        self.qt_app.quit()