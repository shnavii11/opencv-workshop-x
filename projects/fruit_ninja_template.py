# ═══════════════════════════════════════════════════════════════════════════════
# Fruit Ninja Clone — Workshop Template (Students Fill This In!)
# ═══════════════════════════════════════════════════════════════════════════════
# Install: pip install opencv-python mediapipe numpy
# ═══════════════════════════════════════════════════════════════════════════════

import cv2
import mediapipe as mp
import numpy as np
import random
import math

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG - Let's set some game rules!
# ═══════════════════════════════════════════════════════════════════════════════
SWIPE_THRESHOLD = 2      # TODO: How fast should finger move to slice?
GRAVITY = 0.8             # TODO: How strong is gravity?
SPAWN_RATE = 55           # TODO: Frames between fruit spawns
LIVES = 3                 # TODO: Starting lives
WIN_W, WIN_H = 640, 360   # Window size

# ═══════════════════════════════════════════════════════════════════════════════
# HAND TRACKER - Detects your fingertip position
# ═══════════════════════════════════════════════════════════════════════════════
class HandTracker:
    def __init__(self):
        # TODO: Initialize MediaPipe Hands
        # HINT: mp.solutions.hands.Hands(...)
        self.hands = None  # FIX ME!
        self.trail = []    # Stores recent fingertip positions
        
    def process(self, rgb_frame):
        """
        TODO: Process frame and return fingertip position + velocity
        Returns: (x, y, velocity) or (None, None, 0) if no hand
        
        Steps:
        1. Run MediaPipe on rgb_frame
        2. If hand detected, get index fingertip (landmark 8)
        3. Convert normalized coords to pixel coords
        4. Add to trail, keep only last 6 points
        5. Calculate velocity from last 2 trail points
        """
        # TODO: Process the frame
        result = None  # FIX ME!
        
        # TODO: Check if hand detected
        
        # TODO: Get fingertip landmark (index 8)
        
        # TODO: Convert to pixel coordinates (tip.x * WIN_W, tip.y * WIN_H)
        x, y = None, None
        
        # TODO: Update trail
        
        # TODO: Calculate velocity (distance between last 2 points)
        velocity = 0
        
        # TODO: Clear trail if no hand detected
        
        return x, y, velocity
    
    def draw_trail(self, frame):
        """
        TODO: Draw white line connecting trail points
        HINT: cv2.line() for each pair of consecutive points
        """
        pass  # FIX ME!

# ═══════════════════════════════════════════════════════════════════════════════
# FRUIT - Flies across screen waiting to be sliced
# ═══════════════════════════════════════════════════════════════════════════════
class Fruit:
    def __init__(self, is_bomb=False):
        self.is_bomb = is_bomb
        self.is_sliced = False
        
        # TODO: Setup fruit properties
        # If bomb: radius=35, color=(50,50,60)
        # If fruit: radius=30-40, color red or orange (random)
        self.radius = 0     # FIX ME!
        self.color = (0,0,0)  # FIX ME!
        
        # TODO: Random spawn from left or right edge
        # Left: x = -radius, vx = positive (6 to 12)
        # Right: x = WIN_W + radius, vx = negative (-6 to -12)
        self.x = 0.0    # FIX ME!
        self.vx = 0.0   # FIX ME!
        
        # TODO: Random y position (between 30% and 80% of screen height)
        self.y = 0.0    # FIX ME!
        
        # TODO: Upward velocity (negative, between -10 and -16)
        self.vy = 0.0   # FIX ME!
    
    def update(self):
        """
        TODO: Apply physics
        Steps:
        1. Add GRAVITY to vy (makes it fall)
        2. Add vx to x (horizontal movement)
        3. Add vy to y (vertical movement)
        Only if not sliced!
        """
        pass  # FIX ME!
    
    def is_off_screen(self):
        """TODO: Check if fruit left the visible area"""
        return False  # FIX ME!
    
    def fell_off(self):
        """TODO: Check if fell off bottom without being sliced"""
        return False  # FIX ME!
    
    def draw(self, frame):
        """
        TODO: Draw the fruit
        Steps:
        1. Get center position (int(self.x), int(self.y))
        2. If bomb: draw dark circle + fuse line
        3. If fruit: draw colored circle + darker outline
        HINT: cv2.circle(frame, (cx, cy), radius, color, thickness, cv2.LINE_AA)
        """
        cx, cy = int(self.x), int(self.y)
        
        if self.is_bomb:
            # TODO: Draw bomb
            pass
        else:
            # TODO: Draw fruit
            pass
    
    def distance_to(self, x, y):
        """
        TODO: Calculate distance from (x,y) to fruit center
        HINT: math.sqrt(dx*dx + dy*dy)
        """
        return 0  # FIX ME!

# ═══════════════════════════════════════════════════════════════════════════════
# SLICE HALF - Half of a sliced fruit that flies away
# ═══════════════════════════════════════════════════════════════════════════════
class SliceHalf:
    def __init__(self, x, y, radius, color, direction):
        """
        direction: -1 for left half, +1 for right half
        TODO: Setup initial position and velocity
        """
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.color = color
        self.direction = direction
        
        # TODO: Set horizontal velocity based on direction
        self.vx = 0  # FIX ME!
        
        # TODO: Set upward velocity (negative, random 4-7)
        self.vy = 0  # FIX ME!
        
        self.age = 0
        self.lifespan = 20
    
    def update(self):
        """TODO: Move the half and apply gravity"""
        pass  # FIX ME!
    
    def is_dead(self):
        """TODO: Check if reached end of lifespan"""
        return False  # FIX ME!
    
    def draw(self, frame):
        """
        TODO: Draw half-circle that fades out
        Steps:
        1. Calculate alpha (1.0 - age/lifespan)
        2. Fade the color using alpha
        3. Draw ellipse arc (90-270° for left, 270-450° for right)
        HINT: cv2.ellipse() with start_angle and end_angle
        """
        pass  # FIX ME!

# ═══════════════════════════════════════════════════════════════════════════════
# GAME STATE - Manages score, lives, fruits
# ═══════════════════════════════════════════════════════════════════════════════
class GameState:
    def __init__(self):
        self.state = 'start'
        self.reset()
    
    def reset(self):
        """TODO: Reset game to initial state"""
        self.score = 0
        self.lives = LIVES
        self.fruits = []
        self.slice_halves = []
        self.frame_count = 0
        self.flash_timer = 0
    
    def update(self, tip_x, tip_y, velocity):
        """
        TODO: Main game logic
        Steps:
        1. Increment frame_count
        2. Spawn fruit every SPAWN_RATE frames (every 5th is bomb)
        3. Update all fruits
        4. Check if fruit fell off bottom (lose life)
        5. Check collision with fingertip (slice if fast enough)
        6. Update slice halves
        7. Return 'gameover' if lives <= 0, else 'playing'
        """
        self.frame_count += 1
        
        # TODO: Spawn fruits
        
        # TODO: Update fruits
        for fruit in list(self.fruits):
            pass  # FIX ME!
        
        # TODO: Update slice halves
        
        # TODO: Flash countdown
        
        # TODO: Check game over
        return 'playing'
    
    def slice_fruit(self, fruit):
        """
        TODO: Handle fruit being sliced
        Steps:
        1. Mark fruit as sliced
        2. If bomb: lose life, set flash_timer = 8
        3. If fruit: add score, create 2 slice halves (left and right)
        4. Remove fruit from list
        """
        pass  # FIX ME!
    
    def draw_hud(self, frame):
        """
        TODO: Draw score (center top) and lives (top left)
        HINT: cv2.putText()
        """
        pass  # FIX ME!
    
    def apply_flash(self, frame):
        """
        TODO: Red flash when bomb hit
        Steps:
        1. Check if flash_timer > 0
        2. Create red overlay
        3. Blend with frame using cv2.addWeighted()
        """
        pass  # FIX ME!

# ═══════════════════════════════════════════════════════════════════════════════
# SCREENS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_start_screen(frame):
    """
    TODO: Draw start screen
    Steps:
    1. Darken frame with overlay
    2. Draw "FRUIT NINJA" title (large, white, centered)
    3. Draw subtitle "raise your hand to start"
    """
    pass  # FIX ME!

def draw_gameover_screen(frame, score):
    """
    TODO: Draw game over screen
    Steps:
    1. Darken frame
    2. Draw "GAME OVER" (large, red)
    3. Draw score
    4. Draw "Press R to restart | Q to quit"
    """
    pass  # FIX ME!

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GAME LOOP
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    # TODO: Initialize webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, WIN_W)
    cap.set(4, WIN_H)
    
    # TODO: Create tracker and game
    tracker = None  # FIX ME!
    game = None     # FIX ME!
    
    # TODO: Create window
    
    while True:
        # TODO: Read frame from camera
        ret, frame = cap.read()
        if not ret:
            break
        
        # TODO: Flip frame horizontally (mirror effect)
        
        # TODO: Resize to target size
        
        # TODO: Convert to RGB and get hand position
        # rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # tip_x, tip_y, velocity = tracker.process(rgb)
        
        # ═══════════════════════════════════════════════════════════════════════
        # TODO: STATE MACHINE
        # ═══════════════════════════════════════════════════════════════════════
        
        # if game.state == 'start':
        #     draw_start_screen(frame)
        #     if tip_x is not None:  # hand detected
        #         game.state = 'playing'
        #         game.reset()
        
        # elif game.state == 'playing':
        #     result = game.update(tip_x, tip_y, velocity)
        #     if result == 'gameover':
        #         game.state = 'gameover'
        #     
        #     # Draw game elements
        #     # 1. Draw all fruits
        #     # 2. Draw all slice halves
        #     # 3. Draw fingertip trail
        #     # 4. Draw fingertip dot (green circle)
        #     # 5. Draw HUD
        #     # 6. Apply flash
        
        # elif game.state == 'gameover':
        #     draw_gameover_screen(frame, game.score)
        
        # TODO: Show frame
        # cv2.imshow("Fruit Ninja", frame)
        
        # TODO: Handle keyboard input
        # key = cv2.waitKey(1) & 0xFF
        # if key == ord('q') or key == 27:  # Q or Escape
        #     break
        # if key == ord('r') and game.state == 'gameover':  # R to restart
        #     game.state = 'playing'
        #     game.reset()
        
        pass  # Remove this when you add your code!
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
