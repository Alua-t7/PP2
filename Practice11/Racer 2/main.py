# Racer Game — Extended from Practice 10
import pygame
import sys
import random
import time
from pygame.locals import *

pygame.init()
crash_sound = pygame.mixer.Sound("crash.wav")
FPS           = 60
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600

# Enemy base speed — will increase as the player collects coins
ENEMY_SPEED = 5

# How many total coin-points must be collected to trigger a speed boost
# e.g. first boost at 10 points, second at 20, etc.
SPEED_BOOST_EVERY = 10

# How much to increase ENEMY_SPEED on each milestone
SPEED_BOOST_AMOUNT = 1

# Score (survival time — incremented when an enemy passes the player)
SCORE = 0

# Total weighted coin points collected by the player
COIN_POINTS = 0

# Tracks which speed milestone we last triggered (to avoid double-triggering)
LAST_BOOST_MILESTONE = 0

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
BRONZE = (205, 127, 50)    # Bronze coin color
SILVER = (192, 192, 192)   # Silver coin color
GOLD   = (255, 215, 0)     # Gold coin color

#Fonts 

font       = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 18)
font_tiny  = pygame.font.SysFont("Verdana", 13)

# Pre-render static "Game Over" text (only needs to be done once)
game_over_text = font.render("Game Over", True, BLACK)

# BACKGROUND
background = pygame.image.load("AnimatedStreet.png")

# DISPLAY
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer")



COIN_TYPES = [
    {"color": BRONZE, "value": 1, "weight": 60, "label": "B", "radius": 12},
    {"color": SILVER, "value": 3, "weight": 30, "label": "S", "radius": 14},
    {"color": GOLD,   "value": 5, "weight": 10, "label": "G", "radius": 16},
]

# Build a weighted list for random.choices()
# e.g. if weights are [60, 30, 10]:
#   bronze appears ~60% of the time
#   silver appears ~30% of the time
#   gold   appears ~10% of the time
_COIN_WEIGHTS = [ct["weight"] for ct in COIN_TYPES]


def random_coin_type():
    """Return a random coin-type dict, respecting spawn weights."""
    return random.choices(COIN_TYPES, weights=_COIN_WEIGHTS, k=1)[0]


# SPRITE CLASSES

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect  = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)

    def move(self):
        """Read arrow keys and update horizontal position."""
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]  and self.rect.left  > 0:
            self.rect.move_ip(-5, 0)
        if keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip( 5, 0)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect  = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        """Move downward at current ENEMY_SPEED; respawn at top when off-screen."""
        global SCORE
        self.rect.move_ip(0, ENEMY_SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


class Coin(pygame.sprite.Sprite):
    """
    A collectible coin with a randomly selected weight type.

    Coin types and their properties:
      Bronze (B) — most common  (60%), worth 1 point,  small
      Silver (S) — moderately rare (30%), worth 3 points, medium
      Gold   (G) — rare         (10%), worth 5 points,  large

    Collecting coins adds to COIN_POINTS.
    Every SPEED_BOOST_EVERY points, ENEMY_SPEED gets a permanent boost.
    """

    FALL_SPEED = 3   # Coins fall slower than enemies so they're catchable

    def __init__(self):
        super().__init__()
        self._pick_type()

    def _pick_type(self):
        """Select a random coin type and rebuild the sprite image."""
        self.coin_type = random_coin_type()
        self.value     = self.coin_type["value"]
        radius         = self.coin_type["radius"]

        # Draw coin as a colored circle on a transparent surface
        size       = radius * 2 + 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center     = (size // 2, size // 2)
        pygame.draw.circle(self.image, self.coin_type["color"], center, radius)

        # Overlay the type label (B / S / G) in the center
        coin_font  = pygame.font.SysFont("Verdana", radius, bold=True)
        label_surf = coin_font.render(self.coin_type["label"], True, BLACK)
        lx = center[0] - label_surf.get_width()  // 2
        ly = center[1] - label_surf.get_height() // 2
        self.image.blit(label_surf, (lx, ly))

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -20)

    def _respawn(self):
        """Respawn with a newly randomized coin type for variety."""
        self._pick_type()

    def move(self):
        """Fall downward; respawn at top if it exits the bottom uncollected."""
        self.rect.move_ip(0, self.FALL_SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn()


# SPRITE GROUPS
all_sprites = pygame.sprite.Group()
enemies     = pygame.sprite.Group()
coins       = pygame.sprite.Group()

# Create initial sprites
P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies.add(E1)
coins.add(C1)
all_sprites.add(P1, E1, C1)

# CUSTOM TIMER EVENTS

# Baseline difficulty: small speed increase every second
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Spawn an extra enemy car every 3 seconds
ADD_ENEMY = pygame.USEREVENT + 2
pygame.time.set_timer(ADD_ENEMY, 3000)

# Spawn an extra coin every 4 seconds
ADD_COIN = pygame.USEREVENT + 3
pygame.time.set_timer(ADD_COIN, 4000)

# SCROLLING BACKGROUND
bg_y1 = 0
bg_y2 = -SCREEN_HEIGHT
BG_SCROLL_SPEED = 2

# Clock — created once outside the loop
FramePerSec = pygame.time.Clock()

# MAIN GAME LOOP

while True:

    # --- Event handling ---
    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Baseline speed increase every second (independent of coin boosts)
        if event.type == INC_SPEED:
            ENEMY_SPEED += 0.3

        # Spawn an extra enemy car
        if event.type == ADD_ENEMY:
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        # Spawn an extra coin with a randomly chosen weight
        if event.type == ADD_COIN:
            new_coin = Coin()
            coins.add(new_coin)
            all_sprites.add(new_coin)

    # --- Coin milestone check: boost enemy speed ---
    # Every time COIN_POINTS crosses a multiple of SPEED_BOOST_EVERY,
    # we permanently increase ENEMY_SPEED by SPEED_BOOST_AMOUNT.
    current_milestone = (COIN_POINTS // SPEED_BOOST_EVERY) * SPEED_BOOST_EVERY
    if COIN_POINTS > 0 and current_milestone > LAST_BOOST_MILESTONE:
        ENEMY_SPEED          += SPEED_BOOST_AMOUNT
        LAST_BOOST_MILESTONE  = current_milestone

    # --- Scrolling background ---
    bg_y1 += BG_SCROLL_SPEED
    bg_y2 += BG_SCROLL_SPEED
    if bg_y1 >= SCREEN_HEIGHT:
        bg_y1 = -SCREEN_HEIGHT
    if bg_y2 >= SCREEN_HEIGHT:
        bg_y2 = -SCREEN_HEIGHT

    DISPLAYSURF.blit(background, (0, bg_y1))
    DISPLAYSURF.blit(background, (0, bg_y2))

    # --- Move and draw all sprites --------------------------------------------
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # --- Coin collection collision --------------------------------------------
    collected = pygame.sprite.spritecollide(P1, coins, False)
    for coin in collected:
        COIN_POINTS += coin.value   # Add this coin's weighted point value
        coin._respawn()             # Respawn with a new random type

    # --- HUD: Score (top-left) ------------------------------------------------
    score_surf = font_small.render(f"Score: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(score_surf, (10, 10))

    # --- HUD: Coin points (top-right) -----------------------------------------
    coin_surf = font_small.render(f"Coins: {COIN_POINTS}pts", True, GOLD)
    DISPLAYSURF.blit(coin_surf, (SCREEN_WIDTH - coin_surf.get_width() - 10, 10))

    # --- HUD: Current enemy speed (top-right, below coins) --------------------
    speed_surf = font_tiny.render(f"Speed: {ENEMY_SPEED:.1f}", True, BLACK)
    DISPLAYSURF.blit(speed_surf, (SCREEN_WIDTH - speed_surf.get_width() - 10, 34))

    # --- HUD: Next speed boost threshold (top-right) -------------------------
    next_boost = LAST_BOOST_MILESTONE + SPEED_BOOST_EVERY
    boost_surf = font_tiny.render(f"Next boost: {next_boost}pts", True, BLACK)
    DISPLAYSURF.blit(boost_surf, (SCREEN_WIDTH - boost_surf.get_width() - 10, 52))

    # --- HUD: Coin legend (bottom of screen) ---
    legend = font_tiny.render("B=1pt  S=3pts  G=5pts", True, BLACK)
    DISPLAYSURF.blit(legend, (SCREEN_WIDTH // 2 - legend.get_width() // 2,
                               SCREEN_HEIGHT - 22))

    # --- Player–Enemy collision → Game Over ---
    if pygame.sprite.spritecollideany(P1, enemies):
        crash_sound.play()
        time.sleep(0.5)

        DISPLAYSURF.fill(WHITE)
        DISPLAYSURF.blit(game_over_text, (30, 220))

        # Show final score and coin points
        final = font_small.render(
            f"Score: {SCORE}   Coins: {COIN_POINTS}pts", True, BLACK)
        DISPLAYSURF.blit(final, (SCREEN_WIDTH // 2 - final.get_width() // 2, 320))

        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # --- Refresh display ---
    pygame.display.update()
    FramePerSec.tick(FPS)