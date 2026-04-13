# Concept: Bitwise Operations and Thresholding
# Bitwise ops treat each pixel like a binary number and apply logic (NOT, AND, OR).
# Thresholding converts a grayscale image into pure black-and-white based on a cutoff value.

import cv2
import numpy as np
from constants import input_img

img = cv2.imread(input_img)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# --- BITWISE NOT ---
# Inverts every pixel: 0 becomes 255, 255 becomes 0 (photo negative effect)
inverted_img = cv2.bitwise_not(img)
cv2.imshow('Original', img)
cv2.imshow('NOT (Inverted)', inverted_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# --- MASKING WITH BITWISE AND ---
# A mask is a grayscale image where white (255) = keep and black (0) = discard
mask = np.zeros(img.shape[:2], dtype="uint8")   # Start with a fully black mask
cv2.circle(mask, (250, 250), 200, 255, -1)       # Draw white circle: only this area shows

mask_inv = cv2.bitwise_not(mask)                 # Invert the mask (everything outside shows)

# bitwise_and keeps only pixels where the mask is white (255)
masked_img = cv2.bitwise_and(img, img, mask=mask)

# bitwise_or passes through any non-zero pixel from either source
masked_img_or = cv2.bitwise_or(img, img, mask=mask)

cv2.imshow("Original", img)
cv2.imshow("The Mask", mask)
cv2.imshow("Mask NOT (Inverted)", mask_inv)
cv2.imshow("Masked Output (bitwise_and)", masked_img)
cv2.imshow("Masked image using OR (bitwise_or)", masked_img_or)
cv2.waitKey(0)
cv2.destroyAllWindows()

# --- GEOMETRY ---
cropped = img[100:400, 100:400]     # Slice the array: [y_start:y_end, x_start:x_end]
flipped = cv2.flip(img, 1)          # 1 = horizontal flip, 0 = vertical flip

# --- THRESHOLDING ---
# Simple Binary: if pixel > 127, set to 255 (white); otherwise 0 (black)
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Adaptive: uses a local neighborhood average instead of one global value
# Handles uneven lighting better than simple thresholding
adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)

cv2.imshow('Cropped', cropped)
cv2.imshow('Flipped', flipped)
cv2.imshow('Binary Threshold', thresh)
cv2.imshow('Adaptive Threshold', adaptive)
cv2.waitKey(0)
cv2.destroyAllWindows()

# --- LIVE THRESHOLD TRACKBAR ---
# A trackbar lets you drag a slider to change the threshold value in real time.
# Otsu's method automatically picks the best threshold value for comparison.

# Compute Otsu threshold once to use as a reference label
otsu_val, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

window_name = "Live Threshold (drag slider) vs Otsu"
cv2.namedWindow(window_name)
cv2.createTrackbar("Threshold", window_name, 127, 255, lambda x: None)  # Slider from 0 to 255

while True:
    # Read the current slider position
    t = cv2.getTrackbarPos("Threshold", window_name)

    # Apply manual threshold at slider value
    _, manual = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)

    # Apply Otsu threshold (always the same, shown as a static comparison)
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Convert single-channel results to BGR so they can be stacked next to each other
    manual_bgr = cv2.cvtColor(manual, cv2.COLOR_GRAY2BGR)
    otsu_bgr   = cv2.cvtColor(otsu,   cv2.COLOR_GRAY2BGR)

    # Label each panel
    cv2.putText(manual_bgr, f"Manual: {t}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0), 2)
    cv2.putText(otsu_bgr, f"Otsu: {int(otsu_val)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 255), 2)

    # Place the two panels side by side in one window
    combined = np.hstack([manual_bgr, otsu_bgr])
    cv2.imshow(window_name, combined)

    if cv2.waitKey(30) & 0xFF != 255:  # Any key press exits
        break

cv2.destroyAllWindows()
