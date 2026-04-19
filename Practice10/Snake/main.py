import pygame
import sys
import random

# --- Initialize Pygame --------------------------------------------------------
pygame.init()

# Cell size in pixels — the entire grid is built on this unit
CELL = 20

# Number of cells horizontally and vertically (playable area)
COLS = 25
ROWS = 23

# Pixel dimensions of the playable grid
GRID_W = COLS * CELL   # 600 px
GRID_H = ROWS * CELL   # 560 px

# Height of the top HUD bar (score + level display)
HUD_H = 40

# Total window size
WIN_W = GRID_W           # 600 px
WIN_H = GRID_H + HUD_H  # 600 px

# --- Colors -------------------------------------------------------------------
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GRAY  = (40,  40,  40)   # Background fill
GRAY       = (80,  80,  80)   # Grid lines
GREEN      = (50,  200, 80)   # Snake body
DARK_GREEN = (30,  140, 50)   # Snake head
RED        = (220, 50,  50)   # Food
YELLOW     = (255, 215, 0)    # HUD text / level flash
WALL_COLOR = (100, 100, 120)  # Border wall tiles
HUD_BG     = (20,  20,  20)   # Top bar background

# --- Directions (dx, dy) ------------------------------------------------------
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

# --- Level settings -----------------------------------------------------------
# Base frames-per-move: how many game frames pass before the snake takes a step.
# Lower = faster snake.  Decreases with each level.
BASE_DELAY = 18      # Frames between moves at level 1
DELAY_STEP = 1           # Reduce delay by this many frames per level
MIN_DELAY  = 6          # Never go faster than this (prevents unplayable speed)

# Foods eaten per level-up
FOODS_PER_LEVEL = 3

# Points awarded per food eaten
POINTS_PER_FOOD = 10


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def all_wall_cells():
    """
    Return a set of (col, row) tuples that represent the border wall tiles.
    The wall is one cell thick along all four edges of the grid.
    """
    walls = set()
    for c in range(COLS):
        walls.add((c, 0))           # Top row
        walls.add((c, ROWS - 1))    # Bottom row
    for r in range(ROWS):
        walls.add((0, r))           # Left column
        walls.add((COLS - 1, r))    # Right column
    return walls


WALLS = all_wall_cells()  # Pre-compute once; walls never change


def random_food_position(snake_body):
    """
    Pick a random grid cell for the food that is:
      - Not on any wall tile
      - Not occupied by any part of the snake's body

    Parameters
    ----------
    snake_body : list of (col, row)
        Current positions of all snake segments.

    Returns
    -------
    (col, row) : tuple
        A valid food position.
    """
    # Build the set of forbidden cells (walls + snake)
    forbidden = WALLS | set(snake_body)

    # All possible cells inside the border
    inner = {(c, r) for c in range(1, COLS - 1) for r in range(1, ROWS - 1)}

    # Available cells = inner area minus forbidden
    available = list(inner - forbidden)

    if not available:
        # Edge case: no room left (snake fills the whole board → player wins)
        return None

    return random.choice(available)


def draw_cell(surface, col, row, color, offset_y=0):
    """
    Draw a filled rectangle for a single grid cell.

    Parameters
    ----------
    surface  : pygame.Surface
    col, row : int   Grid coordinates
    color    : tuple RGB color
    offset_y : int   Pixel offset for the HUD bar above the grid
    """
    rect = pygame.Rect(col * CELL, row * CELL + offset_y, CELL - 1, CELL - 1)
    pygame.draw.rect(surface, color, rect, border_radius=3)


def get_move_delay(level):
    """
    Calculate how many frames to wait between snake moves for a given level.
    Clamped to MIN_DELAY so the game never becomes unplayable.
    """
    return max(MIN_DELAY, BASE_DELAY - (level - 1) * DELAY_STEP)


# GAME STATE INITIALIZER

def new_game():
    """
    Return a fresh game-state dictionary.
    Call this at startup and after every Game Over to reset everything.
    """
    # Snake starts as 3 segments in the middle of the board, moving right
    start_col = COLS // 2
    start_row = ROWS // 2
    snake = [(start_col - i, start_row) for i in range(3)]  # head first

    state = {
        "snake":      snake,
        "direction":  RIGHT,      # Current movement direction
        "next_dir":   RIGHT,      # Queued direction (applied each move tick)
        "score":      0,
        "level":      1,
        "foods_eaten": 0,         # Foods eaten on the current level
        "food":       random_food_position(snake),
        "alive":      True,
        "frame_count": 0,         # Counts frames to control move timing
    }
    return state


# =============================================================================
# DRAWING FUNCTIONS
# =============================================================================

def draw_hud(surface, score, level, font):
    """Draw the top HUD bar showing score and level."""
    # Dark background strip
    pygame.draw.rect(surface, HUD_BG, (0, 0, WIN_W, HUD_H))

    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, YELLOW)

    surface.blit(score_text, (10, HUD_H // 2 - score_text.get_height() // 2))
    surface.blit(level_text, (WIN_W - level_text.get_width() - 10,
                               HUD_H // 2 - level_text.get_height() // 2))


def draw_grid(surface):
    """Draw subtle grid lines to help the player judge distances."""
    for c in range(COLS):
        for r in range(ROWS):
            rect = pygame.Rect(c * CELL, r * CELL + HUD_H, CELL, CELL)
            pygame.draw.rect(surface, GRAY, rect, 1)


def draw_walls(surface):
    """Draw the border wall tiles."""
    for (c, r) in WALLS:
        draw_cell(surface, c, r, WALL_COLOR, offset_y=HUD_H)


def draw_snake(surface, snake):
    """Draw all snake segments; the head is a darker shade."""
    for i, (c, r) in enumerate(snake):
        color = DARK_GREEN if i == 0 else GREEN
        draw_cell(surface, c, r, color, offset_y=HUD_H)


def draw_food(surface, food):
    """Draw the food as a red circle inside its cell."""
    if food is None:
        return
    cx = food[0] * CELL + CELL // 2
    cy = food[1] * CELL + CELL // 2 + HUD_H
    pygame.draw.circle(surface, RED, (cx, cy), CELL // 2 - 2)


def draw_game_over(surface, score, level, font_big, font_small):
    """Overlay a semi-transparent Game Over panel on the screen."""
    # Dim the background
    overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    # "Game Over" heading
    go_surf = font_big.render("Game Over", True, RED)
    surface.blit(go_surf, (WIN_W // 2 - go_surf.get_width() // 2, WIN_H // 2 - 80))

    # Final stats
    stat1 = font_small.render(f"Score: {score}   Level: {level}", True, WHITE)
    stat2 = font_small.render("Press R to restart or Q to quit", True, YELLOW)

    surface.blit(stat1, (WIN_W // 2 - stat1.get_width() // 2, WIN_H // 2))
    surface.blit(stat2, (WIN_W // 2 - stat2.get_width() // 2, WIN_H // 2 + 40))


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    # --- Window & Clock -------------------------------------------------------
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    # --- Fonts ----------------------------------------------------------------
    font_small = pygame.font.SysFont("Verdana", 18, bold=True)
    font_big   = pygame.font.SysFont("Verdana", 52, bold=True)

    # --- Initial game state ---------------------------------------------------
    state = new_game()

    # =========================================================================
    # GAME LOOP
    # =========================================================================
    while True:

        # --- Event handling ---------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # --- Restart / Quit after Game Over ---------------------------
                if not state["alive"]:
                    if event.key == pygame.K_r:
                        state = new_game()
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                # --- Direction input (prevent reversing into yourself) --------
                if event.key == pygame.K_UP    and state["direction"] != DOWN:
                    state["next_dir"] = UP
                if event.key == pygame.K_DOWN  and state["direction"] != UP:
                    state["next_dir"] = DOWN
                if event.key == pygame.K_LEFT  and state["direction"] != RIGHT:
                    state["next_dir"] = LEFT
                if event.key == pygame.K_RIGHT and state["direction"] != LEFT:
                    state["next_dir"] = RIGHT

        # --- Update game logic (only when alive) ------------------------------
        if state["alive"]:
            state["frame_count"] += 1

            # Only move the snake every `move_delay` frames
            move_delay = get_move_delay(state["level"])
            if state["frame_count"] >= move_delay:
                state["frame_count"] = 0

                # Apply the queued direction
                state["direction"] = state["next_dir"]
                dx, dy = state["direction"]

                # Calculate new head position
                head_col, head_row = state["snake"][0]
                new_head = (head_col + dx, head_row + dy)

                # ----- COLLISION 1: Wall / border collision --------------------
                if new_head in WALLS:
                    state["alive"] = False

                # ----- COLLISION 2: Self collision ----------------------------
                elif new_head in state["snake"]:
                    state["alive"] = False

                else:
                    # Move: prepend new head
                    state["snake"].insert(0, new_head)

                    # ----- Food eaten? ----------------------------------------
                    if new_head == state["food"]:
                        state["score"]      += POINTS_PER_FOOD
                        state["foods_eaten"] += 1

                        # Check for level-up
                        if state["foods_eaten"] >= FOODS_PER_LEVEL:
                            state["level"]      += 1
                            state["foods_eaten"] = 0  # Reset counter for new level

                        # Spawn next food at a valid empty cell
                        state["food"] = random_food_position(state["snake"])

                    else:
                        # No food eaten: remove the tail to maintain length
                        state["snake"].pop()

        # --- Drawing ----------------------------------------------------------
        # Fill background
        screen.fill(DARK_GRAY)

        # Grid lines (subtle)
        draw_grid(screen)

        # Border walls
        draw_walls(screen)

        # Snake
        draw_snake(screen, state["snake"])

        # Food
        draw_food(screen, state["food"])

        # HUD bar (score + level)
        draw_hud(screen, state["score"], state["level"], font_small)

        # Game Over overlay
        if not state["alive"]:
            draw_game_over(screen, state["score"], state["level"],
                           font_big, font_small)

        pygame.display.flip()
        clock.tick(60)   # Run the loop at 60 FPS; snake speed is controlled separately



if __name__ == "__main__":
    main()