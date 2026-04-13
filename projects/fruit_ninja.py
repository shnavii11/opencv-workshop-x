
# ═══════════════════════════════════════════════════════════════════════════════
# Fruit Ninja Clone — OpenCV + MediaPipe 
# ═══════════════════════════════════════════════════════════════════════════════
# Install: pip install opencv-python mediapipe numpy
# ═══════════════════════════════════════════════════════════════════════════════

import cv2
import mediapipe as mp
import numpy as np
import random
import math

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
SWIPE_THRESHOLD = 2
GRAVITY = 0.8
SPAWN_RATE = 55
LIVES = 3
WIN_W, WIN_H = 640, 360

# ═══════════════════════════════════════════════════════════════════════════════
# HAND TRACKER
# ═══════════════════════════════════════════════════════════════════════════════
class HandTracker:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.trail = []
        
    def process(self, rgb_frame):
        """Returns (x, y, velocity) of index fingertip"""
        result = self.hands.process(rgb_frame)
        
        if result.multi_hand_landmarks:
            landmarks = result.multi_hand_landmarks[0].landmark
            tip = landmarks[8]  # index fingertip
            x = int(tip.x * WIN_W)
            y = int(tip.y * WIN_H)
            
            # Track trail
            self.trail.append((x, y))
            if len(self.trail) > 6:
                self.trail.pop(0)
            
            # Calculate velocity
            velocity = 0
            if len(self.trail) >= 2:
                dx = self.trail[-1][0] - self.trail[-2][0]
                dy = self.trail[-1][1] - self.trail[-2][1]
                velocity = math.sqrt(dx*dx + dy*dy)
            
            return x, y, velocity
        
        self.trail.clear()
        return None, None, 0
    
    def draw_trail(self, frame):
        """Draw white trail behind fingertip"""
        for i in range(1, len(self.trail)):
            cv2.line(frame, self.trail[i-1], self.trail[i], 
                    (255, 255, 255), 3, cv2.LINE_AA)

# ═══════════════════════════════════════════════════════════════════════════════
# FRUIT
# ═══════════════════════════════════════════════════════════════════════════════
class Fruit:
    def __init__(self, is_bomb=False):
        self.is_bomb = is_bomb
        self.is_sliced = False
        
        # Setup colors & size
        if is_bomb:
            self.radius = 35
            self.color = (50, 50, 60)
        else:
            # Random fruit type
            if random.random() < 0.5:
                self.radius = 40
                self.color = (60, 60, 200)  # red watermelon
            else:
                self.radius = 30
                self.color = (0, 140, 255)  # orange
        
        # Spawn from left or right edge
        if random.random() < 0.5:
            self.x = float(-self.radius)
            self.vx = random.uniform(6, 12)
        else:
            self.x = float(WIN_W + self.radius)
            self.vx = -random.uniform(6, 12)
        
        self.y = float(random.randint(int(WIN_H * 0.3), int(WIN_H * 0.8)))
        self.vy = -random.uniform(10, 16)
    
    def update(self):
        """Apply gravity and movement"""
        if not self.is_sliced:
            self.vy += GRAVITY
            self.x += self.vx
            self.y += self.vy
    
    def is_off_screen(self):
        """Check if fruit left screen"""
        return (self.y > WIN_H + 100 or 
                self.x < -100 or 
                self.x > WIN_W + 100)
    
    def fell_off(self):
        """Check if fell off bottom without being sliced"""
        return not self.is_sliced and self.y > WIN_H + 100
    
    def draw(self, frame):
        cx, cy = int(self.x), int(self.y)
        
        if self.is_bomb:
            # Draw bomb as dark circle
            cv2.circle(frame, (cx, cy), self.radius, self.color, -1, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), self.radius, (30, 30, 40), 2, cv2.LINE_AA)
            # Fuse
            fuse_x = cx - int(self.radius * 0.7)
            fuse_y = cy - int(self.radius * 0.7)
            cv2.line(frame, (cx, cy), (fuse_x, fuse_y), (100, 100, 100), 3)
            cv2.circle(frame, (fuse_x, fuse_y), 4, (0, 100, 255), -1)
        else:
            # Draw fruit as colored circle
            cv2.circle(frame, (cx, cy), self.radius, self.color, -1, cv2.LINE_AA)
            # Darker outline
            darker = tuple(int(c * 0.7) for c in self.color)
            cv2.circle(frame, (cx, cy), self.radius, darker, 3, cv2.LINE_AA)
    
    def distance_to(self, x, y):
        """Distance from point to fruit center"""
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx*dx + dy*dy)

# ═══════════════════════════════════════════════════════════════════════════════
# SLICE HALF (flies apart after slicing)
# ═══════════════════════════════════════════════════════════════════════════════
class SliceHalf:
    def __init__(self, x, y, radius, color, direction):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.color = color
        self.direction = direction  # -1=left, +1=right
        self.vx = direction * random.uniform(3, 6)
        self.vy = -random.uniform(4, 7)
        self.age = 0
        self.lifespan = 20
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4  # gravity
        self.age += 1
    
    def is_dead(self):
        return self.age >= self.lifespan
    
    def draw(self, frame):
        alpha = 1.0 - (self.age / self.lifespan)
        cx, cy = int(self.x), int(self.y)
        
        # Draw half-circle (left or right half)
        start_angle = 90 if self.direction == -1 else 270
        end_angle = 270 if self.direction == -1 else 450
        
        faded_color = tuple(int(c * alpha) for c in self.color)
        cv2.ellipse(frame, (cx, cy), (self.radius, self.radius), 
                   0, start_angle, end_angle, faded_color, -1, cv2.LINE_AA)

# ═══════════════════════════════════════════════════════════════════════════════
# GAME STATE
# ═══════════════════════════════════════════════════════════════════════════════
class GameState:
    def __init__(self):
        self.state = 'start'
        self.reset()
    
    def reset(self):
        self.score = 0
        self.lives = LIVES
        self.fruits = []
        self.slice_halves = []
        self.frame_count = 0
        self.flash_timer = 0
    
    def update(self, tip_x, tip_y, velocity):
        """Main game update loop"""
        self.frame_count += 1
        
        # Spawn new fruits
        if self.frame_count % SPAWN_RATE == 0:
            is_bomb = (len(self.fruits) % 5 == 4)  # every 5th is bomb
            self.fruits.append(Fruit(is_bomb=is_bomb))
        
        # Update fruits
        for fruit in list(self.fruits):
            fruit.update()
            
            # Remove if off-screen
            if fruit.is_off_screen():
                if fruit.fell_off() and not fruit.is_bomb:
                    self.lives -= 1  # lost a life
                self.fruits.remove(fruit)
                continue
            
            # Check collision with fingertip
            if tip_x and velocity > SWIPE_THRESHOLD:
                if fruit.distance_to(tip_x, tip_y) < fruit.radius:
                    self.slice_fruit(fruit)
        
        # Update slice halves
        for half in list(self.slice_halves):
            half.update()
            if half.is_dead():
                self.slice_halves.remove(half)
        
        # Flash countdown
        if self.flash_timer > 0:
            self.flash_timer -= 1
        
        # Check game over
        if self.lives <= 0:
            return 'gameover'
        return 'playing'
    
    def slice_fruit(self, fruit):
        """Handle fruit slicing"""
        fruit.is_sliced = True
        
        if fruit.is_bomb:
            # Hit bomb - lose life and flash
            self.lives -= 1
            self.flash_timer = 8
        else:
            # Sliced fruit - add score
            self.score += 1
            # Create two halves that fly apart
            self.slice_halves.append(SliceHalf(fruit.x, fruit.y, fruit.radius, fruit.color, -1))
            self.slice_halves.append(SliceHalf(fruit.x, fruit.y, fruit.radius, fruit.color, +1))
        
        self.fruits.remove(fruit)
    
    def draw_hud(self, frame):
        """Draw score and lives"""
        # Score at top center
        score_text = str(self.score)
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(score_text, font, 2.5, 4)[0]
        tx = (WIN_W - text_size[0]) // 2
        cv2.putText(frame, score_text, (tx, 70), font, 2.5, (0,0,0), 7, cv2.LINE_AA)
        cv2.putText(frame, score_text, (tx, 70), font, 2.5, (255,255,255), 4, cv2.LINE_AA)
        
        # Lives as simple text
        lives_text = f"Lives: {self.lives}"
        cv2.putText(frame, lives_text, (20, 50), font, 1.0, (255,255,255), 2, cv2.LINE_AA)
    
    def apply_flash(self, frame):
        """Red flash on bomb hit"""
        if self.flash_timer > 0:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (WIN_W, WIN_H), (0, 0, 200), -1)
            alpha = (self.flash_timer / 8) * 0.4
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

# ═══════════════════════════════════════════════════════════════════════════════
# SCREENS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_start_screen(frame):
    overlay = np.zeros_like(frame)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    title = "FRUIT NINJA"
    ts = cv2.getTextSize(title, font, 3.0, 6)[0]
    tx = (WIN_W - ts[0]) // 2
    cv2.putText(frame, title, (tx, WIN_H//2 - 40), font, 3.0, (0,0,0), 9, cv2.LINE_AA)
    cv2.putText(frame, title, (tx, WIN_H//2 - 40), font, 3.0, (255,255,255), 5, cv2.LINE_AA)
    
    sub = "raise your hand to start"
    ss = cv2.getTextSize(sub, font, 0.9, 2)[0]
    sx = (WIN_W - ss[0]) // 2
    cv2.putText(frame, sub, (sx, WIN_H//2 + 20), font, 0.9, (200,200,200), 2, cv2.LINE_AA)

def draw_gameover_screen(frame, score):
    overlay = np.zeros_like(frame)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "GAME OVER"
    ts = cv2.getTextSize(text, font, 2.5, 6)[0]
    tx = (WIN_W - ts[0]) // 2
    cv2.putText(frame, text, (tx, WIN_H//2 - 50), font, 2.5, (0,0,0), 9, cv2.LINE_AA)
    cv2.putText(frame, text, (tx, WIN_H//2 - 50), font, 2.5, (0,60,220), 5, cv2.LINE_AA)
    
    score_text = f"Score: {score}"
    ss = cv2.getTextSize(score_text, font, 1.5, 3)[0]
    sx = (WIN_W - ss[0]) // 2
    cv2.putText(frame, score_text, (sx, WIN_H//2 + 10), font, 1.5, (255,255,255), 3, cv2.LINE_AA)
    
    inst = "Press R to restart  |  Q to quit"
    ist = cv2.getTextSize(inst, font, 0.8, 2)[0]
    ix = (WIN_W - ist[0]) // 2
    cv2.putText(frame, inst, (ix, WIN_H//2 + 60), font, 0.8, (180,180,180), 2, cv2.LINE_AA)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, WIN_W)
    cap.set(4, WIN_H)
    
    tracker = HandTracker()
    game = GameState()
    
    cv2.namedWindow("Fruit Ninja", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Fruit Ninja", WIN_W, WIN_H)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (WIN_W, WIN_H))
        
        # Get hand position
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tip_x, tip_y, velocity = tracker.process(rgb)
        
        # State machine
        if game.state == 'start':
            draw_start_screen(frame)
            if tip_x is not None:
                game.state = 'playing'
                game.reset()
        
        elif game.state == 'playing':
            result = game.update(tip_x, tip_y, velocity)
            if result == 'gameover':
                game.state = 'gameover'
            
            # Draw everything
            for fruit in game.fruits:
                fruit.draw(frame)
            for half in game.slice_halves:
                half.draw(frame)
            tracker.draw_trail(frame)
            if tip_x:
                cv2.circle(frame, (tip_x, tip_y), 8, (0, 255, 0), -1, cv2.LINE_AA)
            game.draw_hud(frame)
            game.apply_flash(frame)
        
        elif game.state == 'gameover':
            draw_gameover_screen(frame, game.score)
        
        cv2.imshow("Fruit Ninja", frame)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        if key == ord('r') and game.state == 'gameover':
            game.state = 'playing'
            game.reset()
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()