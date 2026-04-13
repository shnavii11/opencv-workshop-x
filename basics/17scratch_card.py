import cv2
import numpy as np
from constants import masking_input_img
W, H = 900, 600

img = cv2.imread(masking_input_img)
img = cv2.resize(img, (W, H))
hidden = img.copy()

def build_cover():
    cover = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        ratio = y / H
        b = int(10 + ratio * 25)
        g = int(120 + ratio * 80)
        r = int(170 + ratio * 60)
        cover[y, :] = (b, g, r)

    noise = np.random.randint(0, 15, (H, W, 3), dtype=np.uint8)
    cover = cv2.add(cover, noise)

    for x in range(0, W, 25):
        cv2.line(cover, (x, 0), (x, H), (230, 230, 230), 1)
    for y in range(0, H, 25):
        cv2.line(cover, (0, y), (W, y), (230, 230, 230), 1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "guess who is single?? scratch here!"

    (tw, th), _ = cv2.getTextSize(text, font, 1.4, 3)
    x = (W - tw) // 2
    y = H // 2

    cv2.putText(cover, text, (x+2, y+2),
                font, 1.4, (80, 80, 80), 4, cv2.LINE_AA)
    cv2.putText(cover, text, (x, y),
                font, 1.4, (255, 255, 255), 2, cv2.LINE_AA)

    return cover
cover = build_cover()

mask = np.zeros((H, W), dtype=np.uint8)
drawing = False
prev = None
brush = 30
percent = 0

def mouse(event, x, y, flags, param):
    global drawing, prev, percent

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        prev = (x, y)
        cv2.circle(mask, (x, y), brush, 255, -1)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        cv2.line(mask, prev, (x, y), 255, brush * 2)
        cv2.circle(mask, (x, y), brush, 255, -1)
        prev = (x, y)

        percent = int((np.count_nonzero(mask) / mask.size) * 100)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        prev = None

cv2.namedWindow("Scratch Card")
cv2.setMouseCallback("Scratch Card", mouse)

font = cv2.FONT_HERSHEY_SIMPLEX
revealed_flag = False
while True:

    revealed = cv2.bitwise_and(hidden, hidden, mask=mask)
    covered  = cv2.bitwise_and(cover, cover, mask=cv2.bitwise_not(mask))
    frame = cv2.add(revealed, covered)

    blur = cv2.GaussianBlur(mask, (21, 21), 0)
    blur3 = cv2.merge([blur, blur, blur]) / 255.0
    frame = (frame * (1 - 0.3 * blur3) + hidden * (0.3 * blur3)).astype(np.uint8)

    cv2.putText(frame, f"{percent}% revealed",
                (20, 40), font, 0.8, (255, 255, 255), 2)

    cv2.putText(frame, "Drag | R reset | Q quit",
                (20, H-20), font, 0.5, (200, 200, 200), 1)

    bar_w = int((W - 40) * percent / 100)
    cv2.rectangle(frame, (20, H-50), (W-20, H-40), (50,50,50), -1)
    cv2.rectangle(frame, (20, H-50), (20+bar_w, H-40), (200,180,50), -1)

    cv2.imshow("Scratch Card", frame)

    k = cv2.waitKey(30)
    if k == ord('q'):
        break
    elif k == ord('r'):
        mask[:] = 0
        percent = 0

cv2.destroyAllWindows()