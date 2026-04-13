"""
setup_check.py
Run this before the workshop to verify your environment is ready.
Usage: python setup_check.py
"""

import sys

PASS = "  [OK]"
FAIL = "  [FAIL]"
WARN = "  [WARN]"

print("\n---- OpenCV Workshop Environment Check ----\n")

errors = []
warnings = []


# 1. Python version
major, minor = sys.version_info[:2]
if major == 3 and minor == 12:
    print(f"{PASS} Python {major}.{minor} detected")
elif major == 3 and 9 <= minor <= 11:
    msg = f"Python {major}.{minor} detected. This workshop is tested on Python 3.12."
    print(f"{WARN} {msg}")
    warnings.append(msg)
else:
    msg = f"Python {major}.{minor} detected. Install Python 3.12 using: winget install -e --id Python.Python.3.12"
    print(f"{FAIL} {msg}")
    errors.append(msg)


# 2. opencv-python
try:
    import cv2
    print(f"{PASS} opencv-python {cv2.__version__}")
except ImportError:
    msg = "opencv-python not found. Run: pip install opencv-python==4.8.0.74"
    print(f"{FAIL} {msg}")
    errors.append(msg)


# 3. numpy
try:
    import numpy as np
    print(f"{PASS} numpy {np.__version__}")
except ImportError:
    msg = "numpy not found. Run: pip install numpy"
    print(f"{FAIL} {msg}")
    errors.append(msg)


# 4. mediapipe
try:
    import mediapipe as mp
    print(f"{PASS} mediapipe {mp.__version__}")
except ImportError:
    msg = "mediapipe not found. Run: pip install mediapipe==0.10.21"
    print(f"{FAIL} {msg}")
    errors.append("mediapipe not installed")
except Exception as e:
    msg = f"mediapipe installed but failed to import: {e}"
    print(f"{WARN} {msg}")
    warnings.append(msg)


# 5. webcam
try:
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        if ret and frame is not None:
            print(f"{PASS} Webcam opened and returned a frame")
        else:
            msg = "Webcam opened but returned no frame. Check if another app is using it."
            print(f"{WARN} {msg}")
            warnings.append(msg)
    else:
        msg = "Webcam not found or in use. Close other apps (Zoom, Teams, browser camera) and retry."
        print(f"{FAIL} {msg}")
        errors.append(msg)
except Exception as e:
    msg = f"Webcam check failed: {e}"
    print(f"{WARN} {msg}")
    warnings.append(msg)


# Summary
print("\n-------------------------------------------")
if not errors and not warnings:
    print("All checks passed. You are ready for the workshop.\n")
elif not errors:
    print(f"Ready with {len(warnings)} warning(s). See above.\n")
else:
    print(f"{len(errors)} error(s) found. Fix them before the workshop.\n")
    print("Quick fix reference:")
    print("  Install all dependencies : pip install -r requirements.txt")
    print("  Wrong Python version     : winget install -e --id Python.Python.3.12")
    print("  venv not activating      : run .venv\\Scripts\\activate from the repo folder")
    print("  No cv2 despite install   : check which Python is active: python --version")
    print("                             Then: pip install opencv-python==4.8.0.74")
    print()
