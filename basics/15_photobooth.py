"""
AR Snapchat-Style Photo Booth 
"""
 
import cv2
import numpy as np
import os
from datetime import datetime

DOG_SCALE    = 1.3  # size relative to face width
DOG_OFFSET_Y = -0.28 # shift up by 25% of face height (ears above head)

SUNGLASSES_SCALE    = 1.1   # slightly wider than face
SUNGLASSES_OFFSET_Y = 0.08   # eyes sit ~20% down from top of face box

CROWN_SCALE    = 1.3  # wider arc
CROWN_OFFSET_Y = 0.5 # float above the head


#  HAAR CASCADE

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

#  LOAD PNG (with alpha channel)

def load_png(filename):
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"'{filename}' not found — put it in the same folder as this script.")
    return img

dog_img        = load_png("assets/dog.png")
sunglasses_img = load_png("assets/sunglasses.png")
crown_img    = load_png("assets/crown.png")


# ─────────────────────────────────────────────────────────────────
#  overlay_png  — the core AR compositing function
#
#  We preserve the PNG's original aspect ratio.
#  Instead of stretching to fill (w × h), we fit the PNG
#  inside the box keeping its proportions, then centre it.
#
#  Alpha blending formula (per pixel, per channel):
#    out = png_pixel × (alpha/255)  +  bg_pixel × (1 − alpha/255)
# ─────────────────────────────────────────────────────────────────
def overlay_png(bg, png, cx, cy, target_w):
    """
    Draw `png` centred at (cx, cy) with width `target_w`,
    height auto-calculated to keep the original aspect ratio.

    bg       : webcam frame (BGR)
    png      : loaded BGRA image
    cx, cy   : centre point where overlay should appear on the face
    target_w : desired pixel width of the overlay
    """
    if png is None:
        return

    ph, pw = png.shape[:2]                    # original PNG size
    aspect   = pw / ph                        # width-to-height ratio
    new_w    = max(target_w, 1)
    new_h    = max(int(new_w / aspect), 1)    # height follows the ratio

    resized = cv2.resize(png, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # ── 2. Compute top-left from the centre point ───────────────
    x = cx - new_w // 2
    y = cy - new_h // 2

    # ── 3. Clamp to frame boundaries ────────────────────────────
    H, W = bg.shape[:2]
    x1, y1 = max(x, 0),     max(y, 0)
    x2, y2 = min(x + new_w, W), min(y + new_h, H)

    # Matching slice inside the (possibly cropped) resized PNG
    px1 = x1 - x
    py1 = y1 - y
    px2 = px1 + (x2 - x1)
    py2 = py1 + (y2 - y1)

    if x2 <= x1 or y2 <= y1:
        return   # completely off-screen

    # ── 4. Alpha blend ──────────────────────────────────────────
    roi   = bg[y1:y2, x1:x2]
    chunk = resized[py1:py2, px1:px2]

    if chunk.shape[2] == 4:
        bgr   = chunk[:, :, :3]
        alpha = chunk[:, :,  3].astype(float) / 255.0
    else:
        bg[y1:y2, x1:x2] = chunk[:, :, :3]
        return

    beta = 1.0 - alpha
    for c in range(3):
        roi[:, :, c] = (bgr[:, :, c] * alpha + roi[:, :, c] * beta).astype(np.uint8)

    bg[y1:y2, x1:x2] = roi


# ─────────────────────────────────────────────────────────────────
#  FILTER HELPERS
#
#  For each face (x, y, w, h) returned by detectMultiScale:
#    • face centre x  = x + w//2
#    • eye level y    ≈ y + h*0.38   (eyes are ~38% down the face box)
#    • nose level y   ≈ y + h*0.60
#    • forehead top   = y  (Haar box starts at forehead, not top of skull)
# ─────────────────────────────────────────────────────────────────

def apply_dog(frame, faces):
    for (x, y, w, h) in faces:
        cx = x + w // 2                     # horizontal centre of face
        cy = y + int(h * (0.5 + DOG_OFFSET_Y))  # vertical anchor
        overlay_png(frame, dog_img, cx, cy, int(w * DOG_SCALE))


def apply_sunglasses(frame, faces):
    for (x, y, w, h) in faces:
        cx = x + w // 2
        # Eye level is roughly 38% from top of Haar face box
        eye_y = y + int(h * 0.38)
        # Apply user offset on top of the anatomical estimate
        cy = eye_y + int(h * SUNGLASSES_OFFSET_Y)
        overlay_png(frame, sunglasses_img, cx, cy, int(w * SUNGLASSES_SCALE))


def apply_crown(frame, faces):
    for (x, y, w, h) in faces:
        cx = x + w // 2
        cy = y + int(h * CROWN_OFFSET_Y)
        overlay_png(frame, crown_img, cx, cy, int(w * CROWN_SCALE))


def apply_pixelate(frame, faces):
    BLOCKS = 12
    for (x, y, w, h) in faces:
        x2 = min(x + w, frame.shape[1])
        y2 = min(y + h, frame.shape[0])
        x, y = max(x, 0), max(y, 0)
        face  = frame[y:y2, x:x2]
        small = cv2.resize(face, (BLOCKS, BLOCKS), interpolation=cv2.INTER_LINEAR)
        frame[y:y2, x:x2] = cv2.resize(small, (x2-x, y2-y), interpolation=cv2.INTER_NEAREST)
        cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 200), 2)
        cv2.putText(frame, "CENSORED", (x + 4, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 2, cv2.LINE_AA)


def apply_raw(frame, faces):
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(frame, "Face", (x, y - 8),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)


NAMES = {"0":"Raw","1":"Dog","2":"Sunglasses","3":"Crown","4":"Censor"}
 
def draw_hud(frame, active, flash_timer):
    h, w = frame.shape[:2]
    cv2.putText(frame,
        "[1]Dog  [2]Shades  [3]Crown  [4]Censor  [0]Raw  |  [S]Snap  [Q]Quit",
        (8+30, h-110), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 3, cv2.LINE_AA)
    cv2.putText(frame, f"Filter: {NAMES[active]}", (8+30, h-20),cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 220, 255), 3, cv2.LINE_AA)
    if flash_timer > 0:
        cv2.putText(frame, "SNAP!", (w//2-60, h//2),cv2.FONT_HERSHEY_TRIPLEX, 1.6, (0,255,180), 3, cv2.LINE_AA)
        
        
#  MAIN

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Webcam not found.")
        return

    print("AR Photo Booth running!  1-4 = filters | S = snap | Q = quit")
    active, flash_timer = "0", 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        cv2.putText(frame,"X Photobooth",(200+400,100),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,4,(0,255,255), 14, cv2.LINE_AA)
        cv2.putText(frame,"X Photobooth",(200+400,100),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,4,(246,33,156), 5, cv2.LINE_AA)
        
        gray  = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

        if   active == "1": apply_dog       (frame, faces)
        elif active == "2": apply_sunglasses(frame, faces)
        elif active == "3": apply_crown(frame, faces)
        elif active == "4": apply_pixelate  (frame, faces)
        else:               apply_raw       (frame, faces)

        draw_hud(frame, active, flash_timer)
        if flash_timer > 0:
            flash_timer -= 1

        cv2.imshow("AR Photo Booth", frame)

        key = cv2.waitKey(1) & 0xFF
        if   key == ord('q'): break
        elif key == ord('s'):
            os.makedirs("snapshots", exist_ok=True)
            name = f"snapshots/snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cv2.imwrite(name, frame)
            print(f"📸 Saved → {name}")
            flash_timer = 25
        elif key in [ord('0'),ord('1'),ord('2'),ord('3'),ord('4')]:
            active = chr(key)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
