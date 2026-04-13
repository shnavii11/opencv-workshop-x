# Concept: Hand Tracking with MediaPipe
# MediaPipe detects 21 landmark points on each hand in real time.
# This file draws those landmarks and connections on the webcam feed.
# Requires: pip install mediapipe==0.10.21
# Requires: Python 3.12 or lesser 

try:
    import mediapipe as mp
except ImportError:
    print("mediapipe not found. Install it with:")
    print("    pip install mediapipe==0.10.21")
    print("This requires Python 3.12.")
    raise SystemExit(1)

import cv2

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Create the hand detector: detects up to 2 hands, minimum 50% confidence
hands = mp_hands.Hands(
    model_complexity=0,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open the default webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Mirror horizontally so the feed feels like looking in a mirror
    frame = cv2.flip(frame, 1)

    # MediaPipe expects RGB, but OpenCV gives BGR: convert before processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run hand detection on the RGB frame
    results = hands.process(rgb_frame)

    # Draw landmarks if any hands were detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw all 21 landmark points and their skeletal connections
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

    cv2.imshow("Hand Landmarks", frame)

    if cv2.waitKey(1) & 0xFF == 27:   # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
