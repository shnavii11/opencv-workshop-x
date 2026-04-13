# Shield: Reactive geometric overlay that follows your hand.
# Make a V sign (peace gesture) to toggle the shield on/off.
#
# Requires: pip install mediapipe==0.10.9
# Requires: Python 3.10

try:
    import mediapipe as mp
except ImportError:
    print("mediapipe not found. Install it with:")
    print("    pip install mediapipe==0.10.9")
    print("This requires Python 3.10.")
    raise SystemExit(1)

import cv2
import numpy as np
import math
import random
import time
import warnings
from collections import deque

# Suppress Protobuf warnings for cleaner console output
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')

# --- HAND DETECTION SETUP ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    model_complexity=0,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- GLOBAL STATE ---
shields_active = False                    # Shield is off by default
gesture_timers = {'Left': 0, 'Right': 0} # Tracks how long the V sign has been held
last_toggle_time = 0                      # Prevents rapid flickering on toggle
particles = []                            # Active spark particles

# Stores the last 6 hand positions to draw faded motion-blur ghost shields
hand_trails = {'Right': deque(maxlen=6), 'Left': deque(maxlen=6)}


def is_v_gesture(hand_landmarks):
    """Returns True if the hand is making a V/peace sign (index and middle extended, ring and pinky curled)."""
    wrist = hand_landmarks.landmark[0]

    def get_dist(idx):
        tip = hand_landmarks.landmark[idx]
        return math.sqrt((tip.x - wrist.x)**2 + (tip.y - wrist.y)**2)

    # Landmark indices: 8=Index tip, 12=Middle tip, 16=Ring tip, 20=Pinky tip
    if get_dist(8) > 0.15 and get_dist(12) > 0.15:   # Index and middle are extended
        if get_dist(16) < 0.18 and get_dist(20) < 0.18:  # Ring and pinky are curled
            return True
    return False


def draw_detailed_mandala(img, center, base_radius, hand_angle, hand_label, alpha=1.0):
    """Draws the rotating geometric shield: outer ring, octagon, hexagon, and pulsing core."""
    if base_radius < 30:
        return   # Do not draw if the hand is too far from the camera

    overlay = np.zeros_like(img)   # Transparent layer to draw on before blending

    # Colors scaled by alpha so ghost trails appear faded
    amber  = (0, int(140 * alpha), int(255 * alpha))
    gold   = (0, int(210 * alpha), int(255 * alpha))
    core_w = (int(255 * alpha), int(255 * alpha), int(255 * alpha))

    spin_base = time.time() * 35                          # Rotation speed in degrees per second
    direction = 1 if hand_label == 'Right' else -1        # Left hand spins in opposite direction

    # Outer static rings
    cv2.circle(overlay, center, int(base_radius), amber, 2 if alpha < 1 else 4)
    cv2.circle(overlay, center, int(base_radius * 0.92), (0, int(100 * alpha), int(210 * alpha)), 2)

    # Outer octagon (8 points, rotates slowly)
    pts_oct = []
    for i in range(8):
        angle = np.deg2rad((spin_base * 0.5 * direction) + hand_angle + (i * 45))
        px = int(center[0] + base_radius * 0.88 * math.cos(angle))
        py = int(center[1] + base_radius * 0.88 * math.sin(angle))
        pts_oct.append((px, py))
    for i in range(8):
        cv2.line(overlay, pts_oct[i], pts_oct[(i + 1) % 8], amber, 2 if alpha < 1 else 3)

    # Inner hexagon (6 points, rotates in opposite direction)
    pts_hex = []
    for i in range(6):
        angle = np.deg2rad(-(spin_base * 1.5 * direction) + hand_angle + (i * 60))
        px = int(center[0] + base_radius * 0.75 * math.cos(angle))
        py = int(center[1] + base_radius * 0.75 * math.sin(angle))
        pts_hex.append((px, py))
    for i in range(6):
        cv2.line(overlay, pts_hex[i], pts_hex[(i + 1) % 6], gold, 1 if alpha < 1 else 2)

    # Pulsing core dot: sin(time) produces a smooth oscillating radius
    pulse = math.sin(time.time() * 6) * 4
    cv2.circle(overlay, center, max(1, int(base_radius * 0.1 + pulse)), core_w, -1)

    # Glow effect: blur the overlay layer then blend it onto the frame
    blur_val = 65 if alpha > 0.8 else 31
    if blur_val % 2 == 0:
        blur_val += 1   # GaussianBlur requires an odd kernel size
    glow = cv2.GaussianBlur(overlay, (blur_val, blur_val), 0)

    cv2.addWeighted(img, 1.0, glow, 0.7 * alpha, 0, img)     # Add soft glow
    cv2.addWeighted(img, 1.0, overlay, 1.0 * alpha, 0, img)  # Add sharp lines on top


def update_sparks(frame, center, radius):
    """Spawns and animates spark particles flying out from the shield edge."""
    global particles
    s_layer = np.zeros_like(frame)

    if radius > 30:
        for _ in range(2):   # Add 2 new sparks per frame
            angle = random.uniform(0, 2 * math.pi)
            px = int(center[0] + radius * math.cos(angle))
            py = int(center[1] + radius * math.sin(angle))
            vx = math.cos(angle) * 4 + random.uniform(-1, 1)
            vy = math.sin(angle) * 4 + random.uniform(-1, 1)
            particles.append([px, py, vx, vy, 180])   # [x, y, vx, vy, lifespan]

    new_p = []
    for p in particles:
        p[0], p[1], p[4] = p[0] + int(p[2]), p[1] + int(p[3]), p[4] - 15
        if p[4] > 0:
            if 0 <= p[0] < frame.shape[1] and 0 <= p[1] < frame.shape[0]:
                cv2.circle(s_layer, (int(p[0]), int(p[1])), 1,
                           (0, int(p[4] * 0.6), int(p[4])), -1)
                new_p.append(p)

    particles = new_p
    cv2.addWeighted(frame, 1.0, s_layer, 1.0, 0, frame)


# --- MAIN LOOP ---
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)   # Mirror so the feed looks natural
    h, w, _ = frame.shape

    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    active_labels = []

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            lbl = results.multi_handedness[idx].classification[0].label   # 'Left' or 'Right'
            active_labels.append(lbl)

            wrist = hand_landmarks.landmark[0]
            mcp   = hand_landmarks.landmark[9]
            thumb = hand_landmarks.landmark[4]
            pinky = hand_landmarks.landmark[20]

            # Place shield center between wrist and palm knuckle
            cx = int(((wrist.x + mcp.x) / 2) * w)
            cy = int(((wrist.y + mcp.y) / 2) * h)

            # Toggle shield when V sign is held for 0.5 seconds
            if is_v_gesture(hand_landmarks):
                if gesture_timers[lbl] == 0:
                    gesture_timers[lbl] = time.time()
                elif (time.time() - gesture_timers[lbl]) > 0.5:
                    if (time.time() - last_toggle_time) > 1.2:   # Debounce to prevent flicker
                        shields_active = not shields_active
                        last_toggle_time = time.time()
            else:
                gesture_timers[lbl] = 0

            if shields_active:
                # Scale shield radius by hand depth and finger spread
                depth   = math.sqrt((wrist.x - mcp.x)**2 + (wrist.y - mcp.y)**2)
                stretch = math.sqrt((thumb.x - pinky.x)**2 + (thumb.y - pinky.y)**2)
                radius  = int((depth * 0.8 + stretch * 0.6) * w)

                # Tilt angle of the hand determines shield orientation
                angle = np.degrees(math.atan2(mcp.y - wrist.y, mcp.x - wrist.x))

                hand_trails[lbl].append((cx, cy, radius, angle))

                # Draw faded ghost versions from the position history
                history = list(hand_trails[lbl])
                for i, (tx, ty, tr, ta) in enumerate(history[:-1]):
                    draw_detailed_mandala(frame, (tx, ty), tr, ta, lbl,
                                          alpha=(i + 1) / len(history) * 0.4)

                # Draw the live sharp shield and sparks on top
                draw_detailed_mandala(frame, (cx, cy), radius, angle, lbl, alpha=1.0)
                update_sparks(frame, (cx, cy), radius)

    # Clear trail memory for hands that left the frame
    for l in ['Right', 'Left']:
        if l not in active_labels:
            hand_trails[l].clear()

    status_text  = f"SHIELD: {'ACTIVE' if shields_active else 'OFF'}"
    status_color = (0, 255, 0) if shields_active else (0, 0, 255)
    cv2.putText(frame, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)

    cv2.imshow('Magic Shield', frame)

    if cv2.waitKey(1) & 0xFF == 27:   # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
