# OpenCV Workshop

A hands-on introduction to computer vision for first-year engineering students.

## Folder Structure

```
opencv-workshop-local-v2/
├── assets/                          # Input images used by the scripts
├── basics/                          # All workshop files, run in order
│   ├── constants.py                 # Shared file paths
│   ├── 1io.py                       # Reading, writing, and webcam capture
│   ├── 2shape_colours.py            # Image dimensions and color spaces
│   ├── 3bitwise_threshhold.py       # Bitwise ops, masking, thresholding, live trackbar
│   ├── 4drawing_shapes.py           # Drawing shapes and text on images
│   ├── 5convulation_kernel.py       # Kernels, filters, and padding
│   ├── 6contours.py                 # Edge detection and contour analysis
│   ├── 7morphology.py               # Erosion, dilation, and morphological ops
│   ├── 8rotating_hexagon_maths.py   # Animated hexagon using trigonometry
│   ├── 9rotating_cube_maths.py      # 3D cube with rotation matrices
│   ├── 10mediapipe_hand_tracking.py # Hand detection and tracking with MediaPipe
│   ├── 11filtering.py               # All filters side by side in one window
│   ├── 12particle_systems.py        # Interactive particle explosion on click
│   ├── video_pipeline.py            # Live webcam with FPS display and clip recording
│   └── histogram_demo.py            # Histogram viewer with live brightness trackbar
├── projects/                        # Workshop project files
│   └── fruit_ninja_template.py      # Fruit Ninja starter template
├── setup_check.py                   # Run this first to verify your environment
├── requirements.txt                 # Pinned Python dependencies
└── README.md
```

## File Reference

### Day 1

| File | Concept | Description |
|------|---------|-------------|
| `1io.py` | Image and Video I/O | Load an image, show it, save it, capture from webcam |
| `2shape_colours.py` | Shapes and Color Spaces | Images are NumPy arrays; color depends on the color space |
| `3bitwise_threshhold.py` | Bitwise Ops and Thresholding | Combine or isolate image regions; live threshold trackbar |
| `4drawing_shapes.py` | Drawing | Paint rectangles, circles, text, and polygons on any image |
| `5convulation_kernel.py` | Convolution Kernels | Slide a small matrix over the image to sharpen, blur, or emboss |
| `6contours.py` | Contours and Edges | Find object outlines and describe their shape |
| `7morphology.py` | Morphological Ops | Shrink or grow white regions to clean up binary images |
| `8rotating_hexagon_maths.py` | Trig Animation | Use sin and cos to spin a hexagon on the webcam feed |
| `9rotating_cube_maths.py` | 3D Projection | Rotate a 3D cube and project it onto a 2D screen |

### Day 2

| File | Concept | Description |
|------|---------|-------------|
| `10mediapipe_hand_tracking.py` | Hand Tracking | Detect and track hand landmarks using MediaPipe |
| `11filtering.py` | Image Filtering | Gaussian, Median, Bilateral, and Sharpened filters side by side |
| `12particle_systems.py` | Particle Systems | Click to trigger particle explosions on the webcam feed |

### Day 3

| File | Concept | Description |
|------|---------|-------------|
| `video_pipeline.py` | Video Pipeline | Live webcam with FPS counter; press R to record a 5-second clip |
| `histogram_demo.py` | Histogram | Side-by-side image and histogram with live brightness trackbar |
| `fruit_ninja_template.py` | Project: Fruit Ninja | Starter template to build the Fruit Ninja game |

## Setup (Windows)

### 1. Download and install Python 3.12

Open PowerShell as Administrator and run:

```powershell
winget install -e --id Python.Python.3.12
```

### 2. Open the repo in VS Code and navigate to the folder

Clone the repo, open it in VS Code, then in the terminal run:

```powershell
cd opencv-workshop-local-v2
```

### 3. Create a virtual environment and activate it

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### 4. Install dependencies

```powershell
pip install mediapipe==0.10.21
pip install opencv-python==4.8.0.74
```

### 5. Verify the installation

```powershell
python -c "import cv2; import mediapipe as mp; import numpy; print('OpenCV:', cv2.__version__); print('MediaPipe:', mp.__version__); print('NumPy:', numpy.__version__)"
```

Or run the environment checker:

```powershell
python setup_check.py
```

### 6. Verify MediaPipe is working

Run file 10 from inside the `basics/` folder:

```powershell
cd basics
python 10mediapipe_hand_tracking.py
```

A window should open showing your webcam feed with hand landmarks drawn on it.

## How to Run

All scripts in `basics/` import from `constants.py`. Run them from inside the `basics/` folder:

```powershell
cd basics
python 1io.py
```

### Quick Reference

| Script | Key to Exit | Notes |
|--------|-------------|-------|
| `1io.py` | Q | Opens webcam and saves a clip |
| `2shape_colours.py` | any key | Shows color space conversions |
| `3bitwise_threshhold.py` | any key | Multiple windows; ends with live trackbar |
| `4drawing_shapes.py` | any key | Static drawing demo |
| `5convulation_kernel.py` | any key | Kernel application demo |
| `6contours.py` | any key | Contour detection on an image |
| `7morphology.py` | any key | Multiple windows for each morphological op |
| `8rotating_hexagon_maths.py` | ESC | Live webcam, spinning hexagon |
| `9rotating_cube_maths.py` | ESC | Live webcam, spinning 3D cube |
| `10mediapipe_hand_tracking.py` | ESC | Live hand landmark detection |
| `11filtering.py` | any key | All filters in one side-by-side window |
| `12particle_systems.py` | Q | Click on webcam feed to spawn particles |
| `video_pipeline.py` | Q | R to record a 5-second clip |
| `histogram_demo.py` | any key | Trackbar adjusts brightness live |

> If a window seems frozen, click on it and press a key. OpenCV needs window focus to register keypresses.

## Webcam Note

Scripts that open the webcam: `1io.py`, `8rotating_hexagon_maths.py`, `9rotating_cube_maths.py`, `10mediapipe_hand_tracking.py`, `12particle_systems.py`, `video_pipeline.py`. Make sure the webcam is connected and not in use by another app.

## Prerequisites

- Basic Python: variables, loops, functions
- Some familiarity with NumPy arrays is helpful but not required
