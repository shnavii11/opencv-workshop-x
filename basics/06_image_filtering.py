# Concept: Image Filtering
# Filtering modifies every pixel based on its neighbors.
# Each filter below has a different goal: smoothing, noise removal, or edge-aware blurring.
# All five results are displayed side by side in one window.

import cv2
import numpy as np
from constants import filtering_input_img

img = cv2.imread(filtering_input_img)   # Load the source image

# Gaussian Blur: replaces each pixel with a weighted average of its neighbors.
# The weights follow a bell curve (Gaussian): closer neighbors matter more.
# Best for: general smoothing and pre-processing before edge detection.
gaussian = cv2.GaussianBlur(img, (5, 5), 0)

# Median Blur: replaces each pixel with the median value of its neighborhood.
# Resistant to extreme values (salt-and-pepper noise) that would skew an average.
# Best for: removing random black or white speckle noise.
median = cv2.medianBlur(img, 5)

# Bilateral Filter: blurs the image while keeping edges sharp.
# It weighs neighbors by both distance and color similarity, so edges are preserved.
# Best for: noise removal where you still need clear object boundaries.
bilateral = cv2.bilateralFilter(img, 9, 75, 75)

# Sharpening via custom kernel: amplifies differences between a pixel and its neighbors.
# The center value (10) boosts the pixel; the -1 values subtract surrounding influence.
# Best for: making blurry images look crisper.
sharpen_kernel = np.array([[0, -1, 0],
                            [-1, 10, -1],
                            [0, -1, 0]])
sharpened = cv2.filter2D(img, -1, sharpen_kernel)

# Resize all images to the same height before stacking (they may differ slightly)
h = img.shape[0]
def resize_to_height(im, target_h):
    ratio = target_h / im.shape[0]
    return cv2.resize(im, (int(im.shape[1] * ratio), target_h))

# Stack all five panels horizontally into one wide window
panels = [resize_to_height(x, h) for x in [img, gaussian, median, bilateral, sharpened]]
combined = np.hstack(panels)

# Add a label at the top of each panel
labels = ["Original", "Gaussian", "Median", "Bilateral", "Sharpened"]
panel_w = panels[0].shape[1]
for i, label in enumerate(labels):
    cv2.putText(combined, label, (i * panel_w + 8, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

cv2.imshow("Filters: Original | Gaussian | Median | Bilateral | Sharpened", combined)
cv2.waitKey(0)
cv2.destroyAllWindows()
