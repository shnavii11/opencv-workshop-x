# Concept: Morphological Operations
#
# Morphology works on binary (black and white) images by modifying white regions.
#
# Erosion: shrinks white regions by removing pixels at their edges.
#   Use it to eliminate small noise dots or disconnect touching objects.
#
# Dilation: expands white regions by adding pixels at their edges.
#   Use it to fill small holes or connect objects that are almost touching.
#
# Combining erosion and dilation gives you Opening, Closing, and Gradient:
#   Opening  = Erode then Dilate: removes small white noise without changing large shapes.
#   Closing  = Dilate then Erode: fills small black holes inside white regions.
#   Gradient = Dilation minus Erosion: produces just the outline of white regions.
#
# Top Hat and Black Hat highlight fine detail not visible in the original:
#   Top Hat  = Original minus Opening: shows bright details smaller than the kernel.
#   Black Hat = Closing minus Original: shows dark details smaller than the kernel.

import cv2
import numpy as np
from constants import erosion_dilation_img, hat_input_img, opening_input_img, closing_input_img

# --- EROSION AND DILATION ---
img = cv2.imread(erosion_dilation_img, 0)              # Load as grayscale (single channel)
_, threshed = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)  # Convert to pure black and white

# The kernel defines the neighborhood shape: a 3x3 square
kernel = np.ones((3, 3), np.uint8)

eroded  = cv2.erode(threshed, kernel, iterations=5)    # Shrinks white areas
dilated = cv2.dilate(threshed, kernel, iterations=5)   # Grows white areas

# Morphological Gradient = Dilation - Erosion = outline of white regions only
grad = cv2.morphologyEx(threshed, cv2.MORPH_GRADIENT, kernel)

cv2.imshow('Original', img)
cv2.imshow('Thresholded (cleaner view)', threshed)
cv2.imshow('Erode', eroded)
cv2.imshow('Dilate', dilated)
cv2.imshow('Gradient (outline)', grad)
cv2.waitKey(0)
cv2.destroyAllWindows()

# --- OPENING AND CLOSING ---
# Opening = Erode then Dilate: removes small white noise dots
to_open = cv2.imread(opening_input_img)
to_open = cv2.cvtColor(to_open, cv2.COLOR_BGR2GRAY)

# Closing = Dilate then Erode: fills small black holes inside white regions
to_close = cv2.imread(closing_input_img)
to_close = cv2.cvtColor(to_close, cv2.COLOR_BGR2GRAY)

opening = cv2.morphologyEx(to_open,  cv2.MORPH_OPEN,  kernel)
closing = cv2.morphologyEx(to_close, cv2.MORPH_CLOSE, kernel)

cv2.imshow('Opening Input', to_open)
cv2.imshow('Opening Result (noise removed)', opening)
cv2.imshow('Closing Input', to_close)
cv2.imshow('Closing Result (holes filled)', closing)
cv2.waitKey(0)
cv2.destroyAllWindows()

# --- TOP HAT AND BLACK HAT ---
img = cv2.imread(hat_input_img)
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
kernel = np.ones((10, 10), np.uint8)   # Larger kernel captures bigger structures

# Top Hat: highlights bright details smaller than the kernel
tophat   = cv2.morphologyEx(gray_img, cv2.MORPH_TOPHAT,   kernel)

# Black Hat: highlights dark details smaller than the kernel
blackhat = cv2.morphologyEx(gray_img, cv2.MORPH_BLACKHAT, kernel)

cv2.imshow('Top Hat (bright details)', tophat)
cv2.imshow('Black Hat (dark details)', blackhat)
cv2.waitKey(0)
cv2.destroyAllWindows()
