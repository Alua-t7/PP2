# =============================================================================
# Racer Game — CodersLegacy Tutorial (Parts 1–3) + Extra Features
# Extra features added:
#   - Randomly appearing coins on the road
#   - Coin counter displayed in the top-right corner
# =============================================================================

# --- Imports ------------------------------------------------------------------
import pygame
import sys
import random
import time
from pygame.locals import *

# --- Initialize Pygame --------------------------------------------------------
pygame.init()
crash_sound = pygame.mixer.Sound("crash.wav") #add the sound when two cars collide
# --- Frames per second --------------------------------------------------------
FPS = 60
FramePerSec = pygame.time.Clock()

# --- Colors -------------------------------------------------------------------
BLUE  = (0,   0,   255)
RED   = (255, 0,   0)
GREEN = (0,   255, 0)
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
GOLD  = (255, 215, 0)     # Color used to draw the coin

# --- Game-wide constants ------------------------------------------------------
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED         = 5          # Starting speed of enemy cars
SCORE         = 0          # Tracks how long the player has survived
COIN_COUNT    = 0          # Tracks the number of coins collected

# --- Fonts --------------------------------------------------------------------
font       = pygame.font.SysFont("Verdana", 60)           # Large font for "Game Over"
font_small = pygame.font.SysFont("Verdana", 20)           # Small font for score & coins

# Pre-render static text (rendered once, outside the game loop for performance)
game_over_text = font.render("Game Over", True, BLACK)

# --- Background image ---------------------------------------------------------
# The background scrolls downward to simulate forward motion.
# Replace "AnimatedStreet.png" with your own road image file.
background = pygame.image.load("AnimatedStreet.png")

# --- Display ------------------------------------------------------------------
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer")


# =============================================================================
# SPRITE CLASSES
# =============================================================================

class Player(pygame.sprite.Sprite):
    """
    The player-controlled car.
    Moves left and right using arrow keys.
    Stays within the screen boundaries.
    """

    def __init__(self):
        super().__init__()
        # Load player image; replace with your own file if needed
        self.image = pygame.image.load("Player.png")
        self.rect  = self.image.get_rect()
        # Start the player at the bottom-center of the screen
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)

    def move(self):
        """Read keyboard input and move the player horizontally."""
        pressed_keys = pygame.key.get_pressed()

        # Move left (clamp so the car doesn't leave the screen)
        if pressed_keys[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)

        # Move right (clamp so the car doesn't leave the screen)
        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(5, 0)


class Enemy(pygame.sprite.Sprite):
    """
    An enemy car that falls from the top of the screen.
    Each enemy starts at a random horizontal position.
    When it leaves the bottom, it respawns at the top and increments the score.
    """

    def __init__(self):
        super().__init__()
        # Load enemy image; replace with your own file if needed
        self.image = pygame.image.load("Enemy.png")
        self.rect  = self.image.get_rect()
        # Spawn at a random x position, just above the screen
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        """Move the enemy downward; respawn at top when it exits the bottom."""
        global SCORE
        self.rect.move_ip(0, SPEED)

        # If the enemy has scrolled off the bottom, give a point and respawn
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


class Coin(pygame.sprite.Sprite):
    """
    A collectible coin that appears at a random position on the road.

    Extra feature — coins give the player a bonus for skilled driving.
    Each coin:
      - Spawns at a random x position, just above the screen
      - Falls at a slightly slower speed than enemy cars
      - Disappears when collected (collision with player) → increments COIN_COUNT
      - Respawns at the top when it exits the bottom without being collected
    """

    COIN_RADIUS = 14   # Radius of the drawn circle
    COIN_SPEED  = 3    # Falls slower than enemy cars so it's easier to collect

    def __init__(self):
        super().__init__()
        # Draw the coin as a golden circle on a transparent surface
        size = self.COIN_RADIUS * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (self.COIN_RADIUS, self.COIN_RADIUS), self.COIN_RADIUS)
        # Draw a small "$" symbol in the center for visual clarity
        coin_font   = pygame.font.SysFont("Verdana", 14, bold=True)
        coin_label  = coin_font.render("$", True, BLACK)
        label_rect  = coin_label.get_rect(center=(self.COIN_RADIUS, self.COIN_RADIUS))
        self.image.blit(coin_label, label_rect)

        self.rect = self.image.get_rect()
        self._respawn()   # Set initial position

    def _respawn(self):
        """Place the coin at a random x position, just above the screen."""
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -20)

    def move(self):
        """Move the coin downward; respawn at top when it exits the bottom."""
        self.rect.move_ip(0, self.COIN_SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn()


# =============================================================================
# SPRITE GROUPS
# =============================================================================

# all_sprites — used to draw every sprite in one loop
all_sprites = pygame.sprite.Group()

# enemies — used for collision detection against the player
enemies = pygame.sprite.Group()

# coins — used for coin-collection collision detection
coins = pygame.sprite.Group()

# Create one enemy and one coin to start
E1 = Enemy()
C1 = Coin()
P1 = Player()

# Register sprites in the appropriate groups
enemies.add(E1)
coins.add(C1)
all_sprites.add(P1, E1, C1)

# =============================================================================
# CUSTOM EVENTS
# =============================================================================

# INC_SPEED — fires every 1 000 ms to gradually increase game difficulty
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# ADD_ENEMY — fires every 3 000 ms to spawn an additional enemy car
ADD_ENEMY = pygame.USEREVENT + 2
pygame.time.set_timer(ADD_ENEMY, 3000)

# ADD_COIN — fires every 5 000 ms to spawn an additional coin
ADD_COIN = pygame.USEREVENT + 3
pygame.time.set_timer(ADD_COIN, 5000)

# =============================================================================
# SCROLLING BACKGROUND SETUP
# =============================================================================

# We use two copies of the background image stacked vertically.
# Moving both copies downward and wrapping them creates an infinite scroll effect.
bg_y1 = 0                 # y position of first background copy
bg_y2 = -SCREEN_HEIGHT    # y position of second copy (directly above the first)
BG_SCROLL_SPEED = 2       # How fast the background scrolls (independent of SPEED)

# =============================================================================
# MAIN GAME LOOP
# =============================================================================

while True:

    # --- Event Handling -------------------------------------------------------
    for event in pygame.event.get():

        # Quit the game when the window is closed
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Every second, increase the falling speed of enemy cars
        if event.type == INC_SPEED:
            SPEED += 0.5

        # Every 3 seconds, spawn an extra enemy car
        if event.type == ADD_ENEMY:
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        # Every 5 seconds, spawn an extra coin on the road
        if event.type == ADD_COIN:
            new_coin = Coin()
            coins.add(new_coin)
            all_sprites.add(new_coin)

    # --- Scrolling Background -------------------------------------------------
    bg_y1 += BG_SCROLL_SPEED
    bg_y2 += BG_SCROLL_SPEED

    # When a copy scrolls fully off the bottom, wrap it back to the top
    if bg_y1 >= SCREEN_HEIGHT:
        bg_y1 = -SCREEN_HEIGHT
    if bg_y2 >= SCREEN_HEIGHT:
        bg_y2 = -SCREEN_HEIGHT

    # Draw both background copies
    DISPLAYSURF.blit(background, (0, bg_y1))
    DISPLAYSURF.blit(background, (0, bg_y2))

    # --- Move and Draw all Sprites --------------------------------------------
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # --- HUD: Score (top-left) ------------------------------------------------
    score_surf = font_small.render(f"Score: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(score_surf, (10, 10))

    # --- HUD: Coin count (top-right) — EXTRA FEATURE -------------------------
    coin_surf  = font_small.render(f"Coins: {COIN_COUNT}", True, GOLD)
    # Align the text to the right edge with a 10-pixel margin
    coin_rect  = coin_surf.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    DISPLAYSURF.blit(coin_surf, coin_rect)

    # --- Coin Collection Collision --------------------------------------------
    # spritecollide returns a list of coins that touched the player this frame
    collected = pygame.sprite.spritecollide(P1, coins, False)
    for coin in collected:
        COIN_COUNT += 1          # Increment the coin counter
        coin._respawn()          # Respawn the coin instead of removing it

    # --- Player–Enemy Collision (Game Over) -----------------------------------
    if pygame.sprite.spritecollideany(P1, enemies):
        crash_sound.play()
        # Brief pause so the player can see the collision
        time.sleep(0.5)

        # Draw the "Game Over" screen
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, (30, 250))

        # Show the final score and coin count below "Game Over"
        final_score = font_small.render(f"Score: {SCORE}   Coins: {COIN_COUNT}", True, BLACK)
        DISPLAYSURF.blit(final_score, (80, 340))

        pygame.display.update()
        time.sleep(2)            # Display "Game Over" for 2 seconds
        pygame.quit()
        sys.exit()

    # --- Refresh the Display --------------------------------------------------
    pygame.display.update()
    FramePerSec.tick(FPS)       # Cap the loop at FPS frames per second