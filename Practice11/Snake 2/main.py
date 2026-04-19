# Snake Game — Extended from Practice 10
import pygame
import sys
import random
import math

pygame.init()
 
CELL   = 20          # Size of one grid cell in pixels
COLS   = 25          # Number of columns in the playable grid
ROWS   = 23          # Number of rows in the playable grid
GRID_W = COLS * CELL
GRID_H = ROWS * CELL
HUD_H  = 40          # Height of the top HUD bar
WIN_W  = GRID_W
WIN_H  = GRID_H + HUD_H

# --- Colors -------------------------------------------------------------------
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GRAY  = (40,  40,  40)
GRAY       = (80,  80,  80)
GREEN      = (50,  200, 80)
DARK_GREEN = (30,  140, 50)
WALL_COLOR = (100, 100, 120)
HUD_BG     = (20,  20,  20)
YELLOW     = (255, 215, 0)

# --- Directions ---------------------------------------------------------------
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

# --- Level settings -----------------------------------------------------------
BASE_DELAY      = 16   # Frames between snake moves at level 1
DELAY_STEP      = 1    # Reduce delay by this per level
MIN_DELAY       = 6    # Fastest the snake can go
FOODS_PER_LEVEL = 3    # Foods eaten before levelling up
POINTS_PER_FOOD = 10   # Base points (multiplied by food value)

# =============================================================================
# FOOD TYPE DEFINITIONS
# =============================================================================
# Each food type has:
#   symbol    — letter drawn on the food circle
#   color     — RGB fill color
#   value     — score multiplier (points = POINTS_PER_FOOD * value)
#   weight    — relative spawn probability (higher = more common)
#   lifetime  — seconds before food disappears if not eaten (None = permanent)
#   radius    — pixel radius of the drawn circle

FOOD_TYPES = [
    {
        "symbol":   "A",            # Apple — most common, low value, generous timer
        "color":    (220, 50, 50),
        "value":    1,
        "weight":   60,
        "lifetime": 8.0,
        "radius":   8,
    },
    {
        "symbol":   "C",            # Cherry — moderately rare, medium value
        "color":    (180, 0, 120),
        "value":    3,
        "weight":   30,
        "lifetime": 5.0,
        "radius":   10,
    },
    {
        "symbol":   "S",            # Star — rare, high value, disappears fast
        "color":    (255, 200, 0),
        "value":    5,
        "weight":   10,
        "lifetime": 3.0,
        "radius":   12,
    },
]

# Pre-compute weights list used by random.choices()
_FOOD_WEIGHTS = [ft["weight"] for ft in FOOD_TYPES]


def random_food_type():
    """Return a randomly chosen food-type dict, respecting spawn weights."""
    return random.choices(FOOD_TYPES, weights=_FOOD_WEIGHTS, k=1)[0]


# =============================================================================
# WALL / BORDER HELPERS
# =============================================================================

def all_wall_cells():
    """
    Return a set of (col, row) grid positions that form the border wall.
    The wall is one cell thick along all four edges of the grid.
    """
    walls = set()
    for c in range(COLS):
        walls.add((c, 0))           # Top edge
        walls.add((c, ROWS - 1))    # Bottom edge
    for r in range(ROWS):
        walls.add((0, r))           # Left edge
        walls.add((COLS - 1, r))    # Right edge
    return walls


# Pre-compute wall positions once — they never change
WALLS = all_wall_cells()


def random_food_position(snake_body, existing_food_positions):
    """
    Pick a random empty cell for a new food item.

    Avoids walls, snake body segments, and cells already occupied by food.

    Parameters
    ----------
    snake_body             : list of (col, row)
    existing_food_positions: list of (col, row)

    Returns
    -------
    (col, row) tuple, or None if the board is completely full
    """
    forbidden = WALLS | set(snake_body) | set(existing_food_positions)
    inner     = {(c, r) for c in range(1, COLS - 1) for r in range(1, ROWS - 1)}
    available = list(inner - forbidden)
    if not available:
        return None
    return random.choice(available)


# =============================================================================
# FOOD ITEM CLASS
# =============================================================================

class FoodItem:
    """
    Represents one piece of food on the board.

    Tracks when the food was spawned so we can calculate how much lifetime
    remains and draw an appropriate warning ring around it.
    """

    def __init__(self, pos, ftype):
        self.pos      = pos                         # (col, row) grid position
        self.ftype    = ftype                       # Reference to FOOD_TYPES entry
        self.value    = ftype["value"]              # Score multiplier
        self.lifetime = ftype["lifetime"]           # Seconds until expiry (or None)
        self.born_at  = pygame.time.get_ticks()     # Spawn timestamp in ms

    def age(self):
        """Return how many seconds have passed since this food was created."""
        return (pygame.time.get_ticks() - self.born_at) / 1000.0

    def is_expired(self):
        """Return True if the food has been on the board longer than its lifetime."""
        if self.lifetime is None:
            return False
        return self.age() >= self.lifetime

    def time_fraction(self):
        """
        Return a fraction between 1.0 (just spawned) and 0.0 (about to expire).
        Used to draw the timer ring: a full arc at 1.0, no arc at 0.0.
        Returns 1.0 for permanent food so no ring is drawn.
        """
        if self.lifetime is None:
            return 1.0
        return max(0.0, 1.0 - self.age() / self.lifetime)


# =============================================================================
# GAME STATE
# =============================================================================

def get_move_delay(level):
    """Frames between snake steps for the given level (clamped to MIN_DELAY)."""
    return max(MIN_DELAY, BASE_DELAY - (level - 1) * DELAY_STEP)


def new_game():
    """Return a freshly initialized game-state dictionary."""
    start_col = COLS // 2
    start_row = ROWS // 2
    # Snake starts as 3 segments moving right
    snake      = [(start_col - i, start_row) for i in range(3)]

    # Place one random food item to start the game
    food_pos   = random_food_position(snake, [])
    first_food = FoodItem(food_pos, random_food_type()) if food_pos else None

    return {
        "snake":       snake,
        "direction":   RIGHT,
        "next_dir":    RIGHT,
        "score":       0,
        "level":       1,
        "foods_eaten": 0,
        # foods is a list of FoodItem objects (multiple can exist at once)
        "foods":       [first_food] if first_food else [],
        "alive":       True,
        "frame_count": 0,
    }


# =============================================================================
# DRAWING FUNCTIONS
# =============================================================================

def draw_cell(surface, col, row, color, offset_y=0):
    """Draw one grid cell as a filled rounded rectangle."""
    rect = pygame.Rect(col * CELL, row * CELL + offset_y, CELL - 1, CELL - 1)
    pygame.draw.rect(surface, color, rect, border_radius=3)


def draw_hud(surface, score, level, font):
    """Render the top HUD bar showing score (left) and level (right)."""
    pygame.draw.rect(surface, HUD_BG, (0, 0, WIN_W, HUD_H))
    score_surf = font.render(f"Score: {score}", True, WHITE)
    level_surf = font.render(f"Level: {level}", True, YELLOW)
    surface.blit(score_surf, (10, HUD_H // 2 - score_surf.get_height() // 2))
    surface.blit(level_surf, (WIN_W - level_surf.get_width() - 10,
                               HUD_H // 2 - level_surf.get_height() // 2))


def draw_walls(surface):
    """Draw the border wall tiles."""
    for (c, r) in WALLS:
        draw_cell(surface, c, r, WALL_COLOR, offset_y=HUD_H)


def draw_snake(surface, snake):
    """Draw the snake body; the head uses a darker green shade."""
    for i, (c, r) in enumerate(snake):
        color = DARK_GREEN if i == 0 else GREEN
        draw_cell(surface, c, r, color, offset_y=HUD_H)


def draw_foods(surface, foods, font_tiny):
    """
    Draw all active food items on the canvas.

    Each food shows:
      - A filled circle in its type color
      - A letter label (A / C / S) in the center
      - A shrinking arc ring that warns the player the food is about to vanish.
        The ring starts white and turns red as the remaining time runs out.
    """
    for food in foods:
        # Pixel center of this food's grid cell
        cx = food.pos[0] * CELL + CELL // 2
        cy = food.pos[1] * CELL + CELL // 2 + HUD_H
        r  = food.ftype["radius"]

        # Filled circle
        pygame.draw.circle(surface, food.ftype["color"], (cx, cy), r)

        # Letter label centered on the circle
        label = font_tiny.render(food.ftype["symbol"], True, BLACK)
        surface.blit(label, (cx - label.get_width()  // 2,
                              cy - label.get_height() // 2))

        # Timer ring — only drawn for food with a finite lifetime
        if food.lifetime is not None:
            frac = food.time_fraction()   # 1.0 → fresh, 0.0 → expired

            # Ring color: white when plenty of time, red when almost gone
            ring_color = (255, int(255 * frac), int(255 * frac))

            # Arc spans from 12 o'clock clockwise, shrinking as time runs out
            arc_rect    = pygame.Rect(cx - r - 4, cy - r - 4,
                                      (r + 4) * 2, (r + 4) * 2)
            start_angle = math.pi / 2                        # Top (12 o'clock)
            end_angle   = start_angle + 2 * math.pi * frac  # Shrinks toward start

            if frac > 0.02:   # Don't draw a nearly-invisible sliver
                pygame.draw.arc(surface, ring_color, arc_rect,
                                start_angle, end_angle, 2)


def draw_legend(surface, font_tiny):
    """Draw a small food key at the bottom of the screen."""
    entries = [
        ((220, 50,  50), "A=Apple  +10pts  8s"),
        ((180, 0,  120), "C=Cherry +30pts  5s"),
        ((255, 200,  0), "S=Star   +50pts  3s"),
    ]
    x = 8
    y = WIN_H - 18
    for color, text in entries:
        surf = font_tiny.render(text, True, color)
        surface.blit(surf, (x, y))
        x += surf.get_width() + 14


def draw_game_over(surface, score, level, font_big, font_small):
    """Overlay a semi-transparent Game Over screen."""
    overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    go_surf = font_big.render("Game Over", True, (220, 50, 50))
    surface.blit(go_surf, (WIN_W // 2 - go_surf.get_width() // 2, WIN_H // 2 - 80))

    stat1 = font_small.render(f"Score: {score}   Level: {level}", True, WHITE)
    stat2 = font_small.render("R = restart   Q = quit", True, YELLOW)
    surface.blit(stat1, (WIN_W // 2 - stat1.get_width() // 2, WIN_H // 2))
    surface.blit(stat2, (WIN_W // 2 - stat2.get_width() // 2, WIN_H // 2 + 40))


# =============================================================================
# MAIN
# =============================================================================

def main():
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    font_big   = pygame.font.SysFont("Verdana", 52, bold=True)
    font_small = pygame.font.SysFont("Verdana", 18, bold=True)
    font_tiny  = pygame.font.SysFont("Verdana", 11)

    state = new_game()

    # =========================================================================
    # GAME LOOP
    # =========================================================================
    while True:

        # --- Events -----------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if not state["alive"]:
                    if event.key == pygame.K_r:
                        state = new_game()
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                # Direction change — prevent the snake from reversing into itself
                if event.key == pygame.K_UP    and state["direction"] != DOWN:
                    state["next_dir"] = UP
                if event.key == pygame.K_DOWN  and state["direction"] != UP:
                    state["next_dir"] = DOWN
                if event.key == pygame.K_LEFT  and state["direction"] != RIGHT:
                    state["next_dir"] = LEFT
                if event.key == pygame.K_RIGHT and state["direction"] != LEFT:
                    state["next_dir"] = RIGHT

        # --- Game logic -------------------------------------------------------
        if state["alive"]:
            state["frame_count"] += 1

            # --- Expire old food items ----------------------------------------
            # Remove any food whose lifetime has elapsed
            state["foods"] = [f for f in state["foods"] if not f.is_expired()]

            # Ensure there is always at least one food on the board
            if len(state["foods"]) == 0:
                food_positions = [f.pos for f in state["foods"]]
                new_pos = random_food_position(state["snake"], food_positions)
                if new_pos:
                    state["foods"].append(FoodItem(new_pos, random_food_type()))

            # --- Move the snake every N frames --------------------------------
            if state["frame_count"] >= get_move_delay(state["level"]):
                state["frame_count"] = 0
                state["direction"]   = state["next_dir"]

                dx, dy   = state["direction"]
                hc, hr   = state["snake"][0]
                new_head = (hc + dx, hr + dy)

                # Wall collision → Game Over
                if new_head in WALLS:
                    state["alive"] = False

                # Self collision → Game Over
                elif new_head in state["snake"]:
                    state["alive"] = False

                else:
                    state["snake"].insert(0, new_head)

                    # Check if the snake's new head landed on any food item
                    eaten = next(
                        (f for f in state["foods"] if f.pos == new_head), None)

                    if eaten:
                        # Award weighted points and remove the eaten food
                        state["score"]       += POINTS_PER_FOOD * eaten.value
                        state["foods_eaten"] += 1
                        state["foods"].remove(eaten)

                        # Level up when enough foods have been eaten
                        if state["foods_eaten"] >= FOODS_PER_LEVEL:
                            state["level"]       += 1
                            state["foods_eaten"]  = 0

                        # Spawn a replacement food item
                        food_positions = [f.pos for f in state["foods"]]
                        new_pos = random_food_position(state["snake"], food_positions)
                        if new_pos:
                            state["foods"].append(
                                FoodItem(new_pos, random_food_type()))

                        # From level 2 onward, keep up to 3 foods on the board
                        # so there is always variety for the player to choose from
                        if state["level"] >= 2:
                            while len(state["foods"]) < 3:
                                food_positions = [f.pos for f in state["foods"]]
                                bonus_pos = random_food_position(
                                    state["snake"], food_positions)
                                if not bonus_pos:
                                    break
                                state["foods"].append(
                                    FoodItem(bonus_pos, random_food_type()))

                    else:
                        # No food eaten → remove tail to keep length constant
                        state["snake"].pop()

        # --- Drawing ----------------------------------------------------------
        screen.fill(DARK_GRAY)

        # Subtle grid lines across the canvas
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.rect(screen, GRAY,
                                 pygame.Rect(c * CELL, r * CELL + HUD_H, CELL, CELL), 1)

        draw_walls(screen)
        draw_snake(screen, state["snake"])
        draw_foods(screen, state["foods"], font_tiny)
        draw_hud(screen, state["score"], state["level"], font_small)
        draw_legend(screen, font_tiny)

        if not state["alive"]:
            draw_game_over(screen, state["score"], state["level"],
                           font_big, font_small)

        pygame.display.flip()
        clock.tick(60)


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    main()