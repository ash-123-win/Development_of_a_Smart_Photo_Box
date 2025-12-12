# Smart Photo Box

## Project Description

The **Smart Photo Box** is an autonomous photo booth system designed to capture, process, and instantly print photos at events such as graduation parties. The system uses a Raspberry Pi to control a camera, display, and printer, providing a simple user workflow from photo capture to printing.

All image processing and control are performed locally without any cloud dependency.

---

## What This Project Does

* Captures photos using a connected camera
* Displays the photo preview on a screen
* Applies basic image processing (e.g. crop, brightness, overlay)
* Prints the photo instantly
* Runs fully offline on a Raspberry Pi

---

## Requirements

* Raspberry Pi 4
* Pi Camera 
* Pi display
* Photo printer
* Python 3.0

---

## How to Run the Project

1. Set up the Raspberry Pi 4
2. Connect the camera, display, and printer
3. Open **PyCharm** or any Python IDE on the Raspberry Pi
4. Clone or copy this project into your workspace
5. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   *(The `requirements.txt` file will be generated later using `pip freeze`.)*
6. Run the main Python script to start the Smart Photo Box

---

## Author

* Ashwin K Joy
* Akhi Jose

---

## Notes

This project is intended for educational purposes and uses open-source libraries only.
