# Concept: Image Histograms and Brightness Adjustment
# A histogram counts how many pixels exist at each brightness level (0 to 255).
# A peak on the left means the image is dark; a peak on the right means bright.
# This demo shows the original image alongside its histogram.
# A trackbar lets you shift brightness and watch the histogram move in real time.

import cv2
import numpy as np
from constants import input_img

# Load the source image
img = cv2.imread(input_img)

# Fixed display height for the histogram panel
HIST_H = img.shape[0]   # Match the source image height
HIST_W = 256            # One pixel column per brightness level (0-255)

def compute_histogram_image(gray):
    """
    Compute a grayscale histogram and return it as a BGR image of size (HIST_H x HIST_W).
    Each column x corresponds to brightness level x; the height of the column shows the count.
    """
    # cv2.calcHist returns a 256-element array of pixel counts for each brightness level
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    # Normalize so the tallest bar fills exactly HIST_H pixels
    cv2.normalize(hist, hist, 0, HIST_H, cv2.NORM_MINMAX)

    # Create a black canvas to draw the histogram bars on
    hist_img = np.zeros((HIST_H, HIST_W, 3), dtype=np.uint8)

    for x in range(256):
        bar_height = int(hist[x, 0])   # Height of this bar in pixels
        # Draw a white vertical line from the bottom up to bar_height
        cv2.line(hist_img,
                 (x, HIST_H),            # Bottom of bar
                 (x, HIST_H - bar_height),  # Top of bar
                 (200, 200, 200), 1)

    return hist_img

# Set up the display window with a trackbar
window_name = "Image | Histogram  (trackbar adjusts brightness)"
cv2.namedWindow(window_name)

# Trackbar value 100 = no change (neutral); range 0-200 maps to -100 to +100 brightness shift
cv2.createTrackbar("Brightness (+/-100)", window_name, 100, 200, lambda x: None)

while True:
    # Read the trackbar position and convert to a signed offset (-100 to +100)
    raw = cv2.getTrackbarPos("Brightness (+/-100)", window_name)
    offset = raw - 100   # 0-200 becomes -100 to +100

    # Add the offset to every pixel, clamping to valid range [0, 255]
    adjusted = cv2.add(img, offset)   # add() clips automatically

    # Convert the brightness-adjusted image to grayscale for the histogram
    gray_adjusted = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)

    # Build the histogram image
    hist_img = compute_histogram_image(gray_adjusted)

    # Resize image panel to match histogram height (keeps proportions)
    img_display = cv2.resize(adjusted, (int(img.shape[1] * HIST_H / img.shape[0]), HIST_H))

    # Label the histogram panel with the current offset value
    label = f"Offset: {offset:+d}"
    cv2.putText(hist_img, label, (4, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 1)

    # Place image and histogram side by side
    combined = np.hstack([img_display, hist_img])
    cv2.imshow(window_name, combined)

    if cv2.waitKey(30) & 0xFF != 255:   # Any key press exits
        break

cv2.destroyAllWindows()
