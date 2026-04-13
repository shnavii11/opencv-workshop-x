import cv2
import numpy as np

# Global variables
selected_hsv = None
tolerance = np.array([10, 80, 80])  # HSV tolerance


def pick_color(event, x, y, flags, param):
    global selected_hsv

    if event == cv2.EVENT_LBUTTONDOWN:
        frame = param
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        selected_hsv = hsv_frame[y, x]
        print("Selected HSV:", selected_hsv)


# Start camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera not accessible")
    exit()

# Capture the background before the subject enters frame
print("Capturing background... Move out of frame!")

background = None
for i in range(60):
    ret, frame = cap.read()
    if not ret:
        continue
    background = frame

if background is None:
    print("ERROR: Background capture failed")
    cap.release()
    exit()

background = np.flip(background, axis=1)
print("Background captured!")

WINDOW_NAME = "Invisible Cloak"
cv2.namedWindow(WINDOW_NAME)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = np.flip(frame, axis=1)

    if selected_hsv is not None:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Build the color range from the sampled pixel plus/minus tolerance
        lower = np.maximum(selected_hsv - tolerance, [0, 0, 0])
        upper = np.minimum(selected_hsv + tolerance, [179, 255, 255])

        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)

        # Mask: white where the cloak color is detected
        mask = cv2.inRange(hsv, lower, upper)

        # Clean up the mask: remove noise and fill gaps
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.dilate(mask, kernel, iterations=1)

        mask_inv = cv2.bitwise_not(mask)

        # Cloak pixels: show the background through
        res1 = cv2.bitwise_and(background, background, mask=mask)
        # Non-cloak pixels: show the live camera feed
        res2 = cv2.bitwise_and(frame, frame, mask=mask_inv)

        final_output = cv2.addWeighted(res1, 1, res2, 1, 0)
    else:
        final_output = frame

    cv2.imshow(WINDOW_NAME, final_output)
    cv2.setMouseCallback(WINDOW_NAME, pick_color, frame)

    key = cv2.waitKey(10) & 0xFF
    if key == 27 or key == ord('q'):
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
