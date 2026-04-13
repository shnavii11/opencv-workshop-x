# Concept: Video Pipeline with FPS Display and Clip Recording
# This script opens the webcam, shows a live FPS counter on screen,
# and lets you press R to record a 5-second clip using the MJPG codec.
# Press Q to quit at any time.

import cv2
import time

# Open the default webcam
cap = cv2.VideoCapture(0)

# Get the frame width and height from the camera (used for the VideoWriter)
frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# MJPG is a widely supported codec that compresses each frame as a JPEG
fourcc = cv2.VideoWriter_fourcc(*'MJPG')

# State variables for recording
recording = False          # True while actively writing frames to disk
writer = None              # VideoWriter object (None when not recording)
record_start = 0.0         # Timestamp when recording started
RECORD_DURATION = 5.0      # Seconds to record per clip
clip_count = 0             # Counter used to name each saved clip

# Variables for FPS calculation
prev_time = time.time()    # Time of the previous frame
fps = 0.0                  # Calculated frames per second

print("Press R to record a 5-second clip. Press Q to quit.")

while True:
    ret, frame = cap.read()   # Grab one frame from the webcam
    if not ret:
        break

    # Flip horizontally so the feed mirrors the user
    frame = cv2.flip(frame, 1)

    # Calculate FPS: 1 divided by time elapsed since the last frame
    now = time.time()
    fps = 1.0 / (now - prev_time + 1e-9)   # Add tiny value to avoid division by zero
    prev_time = now

    # Draw the FPS value in the top-left corner of the frame
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    # If recording is active, write the current frame to the clip file
    if recording:
        writer.write(frame)   # Save this frame to the video file

        elapsed = now - record_start   # How many seconds have passed since R was pressed

        # Draw a red REC indicator with remaining time in the top-right corner
        remaining = max(0.0, RECORD_DURATION - elapsed)
        cv2.putText(frame, f"REC {remaining:.1f}s", (frame_w - 180, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        # Stop recording once 5 seconds have passed
        if elapsed >= RECORD_DURATION:
            writer.release()   # Flush and close the video file
            writer = None
            recording = False
            print(f"Saved clip_{clip_count}.avi")

    # Show the frame (with FPS and optional REC label overlaid)
    cv2.imshow("Video Pipeline", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):   # Q: quit the loop
        break

    if key == ord('r') and not recording:   # R: start a new recording
        clip_count += 1
        filename = f"clip_{clip_count}.avi"
        # Create a VideoWriter that saves at the current display frame rate, capped at 30
        writer = cv2.VideoWriter(filename, fourcc, min(fps, 30), (frame_w, frame_h))
        recording = True
        record_start = time.time()
        print(f"Recording {filename}...")

# Release camera and close any open VideoWriter before exiting
if writer is not None:
    writer.release()

cap.release()
cv2.destroyAllWindows()
