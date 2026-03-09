from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CaptureConfig:
    warmup_seconds: float = 5.0
    photos_dir_name: str = "photos"
    file_prefix: str = "arducam"

    # Use a sane default to avoid CMA memory allocation failure.
    # Try 4608x3472 first (still very high quality). You can increase later.
    capture_size: tuple[int, int] = (4608, 3472)

    # If you *really* need full 64MP later, we can add a "full-res mode" path.
    jpeg_quality: int = 95


class CameraHandler:
    def __init__(self, config: Optional[CaptureConfig] = None) -> None:
        self.config = config or CaptureConfig()
        self._picam2 = None
        self._photos_dir = self._resolve_photos_dir()

    def open(self) -> None:
        from picamera2 import Picamera2  # type: ignore

        self._photos_dir.mkdir(parents=True, exist_ok=True)

        self._picam2 = Picamera2()

        # IMPORTANT:
        # Use YUV420 stream to keep buffer memory small, then encode to JPEG.
        still_config = self._picam2.create_still_configuration(
            main={"size": self.config.capture_size, "format": "YUV420"},
            buffer_count=1,
        )
        self._picam2.configure(still_config)

        self._picam2.start()

    def capture_one(self) -> Path:
        if self._picam2 is None:
            raise RuntimeError("Camera is not opened. Call open() first.")

        # Warm-up
        time.sleep(float(self.config.warmup_seconds))

        # --- AUTOFOCUS ---
        self._picam2.set_controls({"AfMode": 2})  # 2 = Continuous AF
        time.sleep(1.0)  # allow lens to settle

        out_path = self._make_output_path()
        self._picam2.capture_file(str(out_path))

        return out_path


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

    def _make_output_path(self) -> Path:
        ts = time.strftime("%Y%m%d_%H%M%S")
        return self._photos_dir / f"{self.config.file_prefix}_{ts}.jpg"

    def _resolve_photos_dir(self) -> Path:
        # <project_root>/src/Devices/camera_handler.py -> parents[2] == project_root
        project_root = Path(__file__).resolve().parents[2]
        return project_root / self.config.photos_dir_name
