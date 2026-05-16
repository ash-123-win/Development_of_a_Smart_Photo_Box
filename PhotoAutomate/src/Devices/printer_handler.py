from __future__ import annotations

import subprocess
import time
from pathlib import Path


class PrinterHandler:
    def __init__(self, printer_name: str = "Canon_CP1500") -> None:
        self.printer_name = printer_name

    def print_photo(self, image_path: Path) -> None:
        if not image_path.exists():
            raise FileNotFoundError(f"Photo not found: {image_path}")

        result = subprocess.run(
            ["lp", "-d", self.printer_name, str(image_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        self.wait_until_done()

    def wait_until_done(self) -> None:
        while True:
            result = subprocess.run(
                ["lpstat", "-o", self.printer_name],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0 or result.stdout.strip() == "":
                break

            time.sleep(5)