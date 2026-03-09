"""
Smart Photo Box
Main entry point for the application.

This project runs on a Raspberry Pi and controls:
- Camera
- Display
- Image processing
- Photo printing

"""
from __future__ import annotations

import logging
from Devices.camera_handler import CameraHandler, CaptureConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main() -> int:
    logging.info("Starting camera capture program...")

    camera = CameraHandler(
        CaptureConfig(
            warmup_seconds=5.0,
            photos_dir_name="photos",   # under project root
            file_prefix="arducam",
        )
    )

    try:
        logging.info("Opening camera...")
        camera.open()

        logging.info("Waiting 5 seconds, then capturing one photo...")
        photo_path = camera.capture_one()

        logging.info("Saved photo to: %s", photo_path)

    except Exception as e:
        logging.exception("Failed: %s", e)
        return 1
    finally:
        logging.info("Closing camera...")
        camera.close()
        logging.info("Done. Exiting.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
