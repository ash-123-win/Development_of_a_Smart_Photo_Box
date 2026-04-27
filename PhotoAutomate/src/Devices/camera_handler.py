from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CaptureConfig:
    warmup_seconds: float = 1.0
    photos_dir_name: str = "photos"
    file_prefix: str = "arducam"
    preview_size: tuple[int, int] = (1280, 720)
    capture_size: tuple[int, int] = (2304, 1736)


class CameraHandler:
    def __init__(self, config: Optional[CaptureConfig] = None) -> None:
        self.config = config or CaptureConfig()
        self._picam2 = None
        self._photos_dir = self._resolve_photos_dir()
        self._preview_config = None
        self._still_config = None

    @property
    def is_open(self) -> bool:
        return self._picam2 is not None

    def open(self) -> None:
        from picamera2 import Picamera2  # type: ignore

        self._photos_dir.mkdir(parents=True, exist_ok=True)
        self._picam2 = Picamera2()

        self._preview_config = self._picam2.create_preview_configuration(
            main={"size": self.config.preview_size, "format": "RGB888"},
            buffer_count=3,
        )
        self._still_config = self._picam2.create_still_configuration(
            main={"size": self.config.capture_size, "format": "YUV420"},
            buffer_count=1,
        )

        self._picam2.configure(self._preview_config)
        self._picam2.start()
        self._picam2.set_controls({"AfMode": 2})
        time.sleep(float(self.config.warmup_seconds))

    def close(self) -> None:
        if self._picam2 is None:
            return
        try:
            self._picam2.stop()
        except Exception:
            pass
        try:
            self._picam2.close()
        except Exception:
            pass
        self._picam2 = None

    def get_preview_frame_rgb(self):
        if self._picam2 is None:
            raise RuntimeError("Camera is not opened.")
        return self._picam2.capture_array("main")

    def capture_photo(self) -> Path:
        if self._picam2 is None or self._still_config is None:
            raise RuntimeError("Camera is not ready.")

        time.sleep(0.25)
        out_path = self._make_output_path(ext="jpg")
        self._picam2.switch_mode_and_capture_file(self._still_config, str(out_path))
        return out_path

    def _make_output_path(self, ext: str) -> Path:
        ts = time.strftime("%Y%m%d_%H%M%S")
        return self._photos_dir / f"{self.config.file_prefix}_{ts}.{ext}"

    def _resolve_photos_dir(self) -> Path:
        project_root = Path(__file__).resolve().parents[2]
        return project_root / self.config.photos_dir_name