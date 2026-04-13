# Concept: Particle Systems
# A particle system simulates many small objects (particles) to create effects
# like explosions, fire, or smoke. Each particle has position, velocity, and lifespan.
# Click on the webcam feed to trigger an explosion.

import cv2
import numpy as np
import random
import math

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # Random direction and speed for a spread-out explosion
        angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
        speed = random.uniform(2, 8)             # Random speed in pixels per frame

        # Convert polar velocity to x/y components using trig
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # Lifespan: frames the particle will live before being removed
        self.life = random.randint(20, 50)

    def update(self):
        self.vy += 0.2   # Gravity: increases downward velocity each frame
        self.x += self.vx
        self.y += self.vy
        self.life -= 1   # Count down lifespan

    def draw(self, frame):
        if self.life > 0:
            # Yellow-to-red color scheme for fire/explosion look
            color = (
                0,                          # Blue channel: off
                random.randint(150, 255),   # Green: gives yellow-orange range
                random.randint(200, 255)    # Red: always high for warmth
            )
            cv2.circle(frame, (int(self.x), int(self.y)), 3, color, -1)

    def alive(self):
        return self.life > 0


# Global list of all active particles
particles = []

def mouse_callback(event, x, y, flags, param):
    global particles
    if event == cv2.EVENT_LBUTTONDOWN:
        # Spawn 120 particles at the click position
        for _ in range(120):
            particles.append(Particle(x, y))


cap = cv2.VideoCapture(0)

cv2.namedWindow('Explosion System')
cv2.setMouseCallback('Explosion System', mouse_callback)  # Register click handler

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)   # Mirror the webcam feed

    # Update and draw each live particle
    for p in particles:
        p.update()
        p.draw(frame)

    # Remove dead particles to keep the list small
    particles = [p for p in particles if p.alive()]

    cv2.imshow('Explosion System', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):   # Press Q to quit
        break

cap.release()
cv2.destroyAllWindows()
