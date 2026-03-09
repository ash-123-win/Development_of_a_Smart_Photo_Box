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

import os
from pathlib import Path

# If launched from SSH/VS Code, attach to the Pi's local display.
if os.environ.get("DISPLAY", "") == "":
    os.environ["DISPLAY"] = ":0"
    xa = Path.home() / ".Xauthority"
    if xa.exists():
        os.environ.setdefault("XAUTHORITY", str(xa))

from app import PhotoBoothApp


def main() -> int:
    app = PhotoBoothApp()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

