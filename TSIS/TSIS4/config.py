# config.py — shared constants for the Snake game

CELL        = 20          # px per grid cell
COLS        = 30          # grid columns
ROWS        = 28          # grid rows
SW          = COLS * CELL # screen width  (600)
SH          = ROWS * CELL # screen height (560)

FPS_BASE    = 8           # starting snake speed (frames/sec)
FPS_PER_LVL = 1           # extra fps per level
FOOD_PER_LVL= 5           # food eaten to advance a level
OBSTACLE_START_LVL = 3    # obstacles appear from this level

# Power-up field lifetime (ms)
POWERUP_FIELD_TTL = 8000
# Power-up effect duration (ms)
POWERUP_EFFECT_TTL = 5000

# Database — edit these to match your PostgreSQL setup
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "snake_db"
DB_USER = "postgres"
DB_PASS = "postgres"

# ── Colors ─────────────────────────────────────────────────────────────────────
C_BG       = (15,  20,  30)
C_GRID     = (25,  32,  45)
C_BORDER   = (60,  80, 110)
C_WHITE    = (255, 255, 255)
C_BLACK    = (0,   0,   0)
C_GREY     = (140, 150, 165)
C_DGREY    = (50,  55,  70)
C_ACCENT   = (80,  200, 140)   # green accent
C_ACCENT2  = (255, 200,  50)   # yellow
C_RED      = (220,  60,  60)
C_PANEL    = (22,  28,  42)

# Food colors
C_FOOD_NORMAL = (255, 100,  80)
C_FOOD_BONUS  = (255, 215,   0)
C_FOOD_POISON = (100,   0,  20)

# Power-up colors
C_PU_SPEED  = (0,   220, 255)
C_PU_SLOW   = (180, 100, 255)
C_PU_SHIELD = (255, 180,  50)

# Obstacle color
C_OBSTACLE  = (70,  80,  95)