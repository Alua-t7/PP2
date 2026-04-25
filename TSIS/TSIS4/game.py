import pygame
import random
import json
import os
from pygame.locals import *
from config import *


# ── Settings helpers ───────────────────────────────────────────────────────────
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "snake_color": [80, 200, 140],
    "grid":        True,
    "sound":       True,
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            s = json.load(open(SETTINGS_FILE))
            for k, v in DEFAULT_SETTINGS.items():
                s.setdefault(k, v)
            return s
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)

def save_settings(s):
    json.dump(s, open(SETTINGS_FILE, "w"), indent=2)


# ── Direction vectors ──────────────────────────────────────────────────────────
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


# ── Helper: random free cell ───────────────────────────────────────────────────
def _free_cell(blocked: set) -> tuple:
    while True:
        c = (random.randint(1, COLS-2), random.randint(1, ROWS-2))
        if c not in blocked:
            return c


# ══════════════════════════════════════════════════════════════════════════════
# Food
# ══════════════════════════════════════════════════════════════════════════════
class Food:
    TYPES = [
        {"kind": "normal", "color": C_FOOD_NORMAL, "pts": 10, "weight": 65},
        {"kind": "bonus",  "color": C_FOOD_BONUS,  "pts": 30, "weight": 25},
        {"kind": "poison", "color": C_FOOD_POISON, "pts":  0, "weight": 10},
    ]
    _W = [t["weight"] for t in TYPES]
    DISAPPEAR_MS = 6000   # bonus food disappears after 6 s

    def __init__(self, blocked: set):
        self.pos     = _free_cell(blocked)
        t            = random.choices(self.TYPES, weights=self._W, k=1)[0]
        self.kind    = t["kind"]
        self.color   = t["color"]
        self.pts     = t["pts"]
        self.spawn_t = pygame.time.get_ticks()

    def expired(self) -> bool:
        """Bonus food disappears; others stay."""
        if self.kind == "bonus":
            return pygame.time.get_ticks() - self.spawn_t > self.DISAPPEAR_MS
        return False

    def draw(self, surf):
        x, y = self.pos
        rect = pygame.Rect(x*CELL+2, y*CELL+2, CELL-4, CELL-4)
        pygame.draw.rect(surf, self.color, rect, border_radius=5)
        if self.kind == "bonus":
            # Pulsing ring
            age = pygame.time.get_ticks() - self.spawn_t
            pulse = int(3 + 2 * abs(((age % 600) / 300) - 1))
            pygame.draw.rect(surf, C_WHITE, rect, pulse, border_radius=5)
        if self.kind == "poison":
            # Skull-ish cross
            cx, cy = x*CELL + CELL//2, y*CELL + CELL//2
            pygame.draw.line(surf, C_WHITE, (cx-5, cy-5), (cx+5, cy+5), 2)
            pygame.draw.line(surf, C_WHITE, (cx+5, cy-5), (cx-5, cy+5), 2)


# ══════════════════════════════════════════════════════════════════════════════
# Power-up
# ══════════════════════════════════════════════════════════════════════════════
class PowerUp:
    TYPES = [
        {"kind": "speed",  "color": C_PU_SPEED,  "label": "⚡"},
        {"kind": "slow",   "color": C_PU_SLOW,   "label": "🐢"},
        {"kind": "shield", "color": C_PU_SHIELD, "label": "🛡"},
    ]

    def __init__(self, blocked: set):
        t          = random.choice(self.TYPES)
        self.kind  = t["kind"]
        self.color = t["color"]
        self.label = t["label"]
        self.pos   = _free_cell(blocked)
        self.spawn_t = pygame.time.get_ticks()

    def expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_t > POWERUP_FIELD_TTL

    def draw(self, surf):
        x, y = self.pos
        cx, cy = x*CELL + CELL//2, y*CELL + CELL//2
        pygame.draw.circle(surf, self.color, (cx, cy), CELL//2 - 1)
        pygame.draw.circle(surf, C_WHITE,    (cx, cy), CELL//2 - 1, 2)
        f  = pygame.font.SysFont("Segoe UI Emoji", 11)
        ls = f.render(self.label, True, C_BLACK)
        surf.blit(ls, ls.get_rect(center=(cx, cy)))


# ══════════════════════════════════════════════════════════════════════════════
# Obstacle
# ══════════════════════════════════════════════════════════════════════════════
def make_obstacles(level: int, blocked: set) -> set:
    """Return a set of (col, row) obstacle cells for this level."""
    count   = min(4 + (level - OBSTACLE_START_LVL) * 2, 20)
    obs     = set()
    for _ in range(count * 10):          # try up to 10x
        if len(obs) >= count:
            break
        c = (random.randint(2, COLS-3), random.randint(2, ROWS-3))
        if c not in blocked and c not in obs:
            obs.add(c)
    return obs


# ══════════════════════════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════════════════════════
def draw_hud(surf, score, level, personal_best,
             active_effect, effect_end_t, shield_active):
    f   = pygame.font.SysFont("Verdana", 15, bold=True)
    f2  = pygame.font.SysFont("Verdana", 12)
    pad = 6

    # Left: score / level
    surf.blit(f.render(f"Score: {score}", True, C_WHITE), (pad, pad))
    surf.blit(f.render(f"Level: {level}", True, C_ACCENT), (pad, pad+20))

    # Right: personal best
    pb = f2.render(f"Best: {personal_best}", True, C_GREY)
    surf.blit(pb, (SW - pb.get_width() - pad, pad))

    # Center: active effect
    if active_effect:
        now    = pygame.time.get_ticks()
        remain = max(0.0, (effect_end_t - now) / 1000)
        col    = {"speed": C_PU_SPEED, "slow": C_PU_SLOW,
                  "shield": C_PU_SHIELD}.get(active_effect, C_WHITE)
        label  = active_effect.upper()
        if active_effect != "shield":
            label += f" {remain:.1f}s"
        s = f.render(label, True, col)
        surf.blit(s, s.get_rect(centerx=SW//2, top=pad))


# ══════════════════════════════════════════════════════════════════════════════
# Main game function
# ══════════════════════════════════════════════════════════════════════════════
def run_game(screen, clock, username: str, personal_best: int) -> tuple[int, int]:
    settings    = load_settings()
    snake_color = tuple(settings["snake_color"])
    show_grid   = settings["grid"]

    # ── Initial state ──────────────────────────────────────────────────────────
    start = (COLS//2, ROWS//2)
    body  = [start, (start[0]-1, start[1]), (start[0]-2, start[1])]
    dirn  = RIGHT
    nxt   = RIGHT

    score         = 0
    level         = 1
    food_eaten    = 0
    obstacles     = set()
    active_effect = None
    effect_end_t  = 0
    shield_active = False

    def blocked_cells():
        return set(body) | obstacles | {(0,0)}   # rough; food/pu avoid body+obs

    food_list = [Food(set(body))]
    powerup   = None
    pu_spawn_timer = pygame.time.get_ticks() + 5000  # first PU after 5 s

    # ── Move timer ─────────────────────────────────────────────────────────────
    def current_fps():
        base = FPS_BASE + (level - 1) * FPS_PER_LVL
        if active_effect == "speed": return base + 4
        if active_effect == "slow":  return max(2, base - 3)
        return base

    move_event = pygame.USEREVENT + 1
    pygame.time.set_timer(move_event, 1000 // current_fps())

    running = True
    while running:
        now = pygame.time.get_ticks()

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); raise SystemExit
            if event.type == KEYDOWN:
                key_map = {K_UP: UP, K_w: UP, K_DOWN: DOWN, K_s: DOWN,
                           K_LEFT: LEFT, K_a: LEFT, K_RIGHT: RIGHT, K_d: RIGHT}
                if event.key in key_map:
                    wanted = key_map[event.key]
                    if wanted != OPPOSITE.get(dirn):
                        nxt = wanted
                if event.key == K_ESCAPE:
                    running = False

            if event.type == move_event:
                dirn    = nxt
                head    = (body[0][0] + dirn[0], body[0][1] + dirn[1])

                # ── Collision: border ──────────────────────────────────────
                hit_border = not (0 < head[0] < COLS-1 and 0 < head[1] < ROWS-1)
                if hit_border:
                    if shield_active:
                        shield_active = False
                        active_effect = None
                        # Wrap around
                        head = (head[0] % COLS, head[1] % ROWS)
                        head = (max(1, min(COLS-2, head[0])),
                                max(1, min(ROWS-2, head[1])))
                    else:
                        running = False; break

                # ── Collision: self ────────────────────────────────────────
                if head in body[:-1]:
                    if shield_active:
                        shield_active = False
                        active_effect = None
                    else:
                        running = False; break

                # ── Collision: obstacle ────────────────────────────────────
                if head in obstacles:
                    if shield_active:
                        shield_active = False
                        active_effect = None
                        obstacles.discard(head)   # destroy that block
                    else:
                        running = False; break

                body.insert(0, head)

                # ── Food collision ─────────────────────────────────────────
                ate = False
                for f in list(food_list):
                    if head == f.pos:
                        food_list.remove(f)
                        if f.kind == "poison":
                            body = body[:-3] if len(body) > 3 else body[:1]
                            if len(body) <= 1:
                                running = False; break
                        else:
                            score      += f.pts
                            food_eaten += 1
                        ate = True
                        # Spawn replacement food
                        bk = set(body) | obstacles
                        food_list.append(Food(bk))
                        # Level up?
                        if food_eaten >= level * FOOD_PER_LVL:
                            level      += 1
                            food_eaten  = 0
                            if level >= OBSTACLE_START_LVL:
                                bk2 = set(body) | {f2.pos for f2 in food_list}
                                obstacles = make_obstacles(level, bk2)
                            pygame.time.set_timer(move_event, 1000 // current_fps())
                        break

                if not ate:
                    body.pop()

                # ── Power-up collision ─────────────────────────────────────
                if powerup and head == powerup.pos:
                    kind     = powerup.kind
                    powerup  = None
                    if kind == "shield":
                        shield_active = True
                        active_effect = "shield"
                        effect_end_t  = 0
                    else:
                        active_effect = kind
                        effect_end_t  = now + POWERUP_EFFECT_TTL
                    pygame.time.set_timer(move_event, 1000 // current_fps())

        # ── Effect expiry ──────────────────────────────────────────────────
        if active_effect and active_effect != "shield" and now > effect_end_t:
            active_effect = None
            effect_end_t  = 0
            pygame.time.set_timer(move_event, 1000 // current_fps())

        # ── Food expiry ────────────────────────────────────────────────────
        for f in list(food_list):
            if f.expired():
                food_list.remove(f)
                food_list.append(Food(set(body) | obstacles))

        # ── Power-up spawn / expiry ────────────────────────────────────────
        if powerup and powerup.expired():
            powerup = None
        if powerup is None and now >= pu_spawn_timer:
            bk = set(body) | obstacles | {f.pos for f in food_list}
            powerup       = PowerUp(bk)
            pu_spawn_timer = now + random.randint(8000, 15000)

        # ── Draw ──────────────────────────────────────────────────────────
        screen.fill(C_BG)

        # Grid
        if show_grid:
            for gx in range(COLS):
                pygame.draw.line(screen, C_GRID, (gx*CELL, 0), (gx*CELL, SH))
            for gy in range(ROWS):
                pygame.draw.line(screen, C_GRID, (0, gy*CELL), (SW, gy*CELL))

        # Border
        pygame.draw.rect(screen, C_BORDER, (0, 0, SW, SH), CELL)

        # Obstacles
        for ox, oy in obstacles:
            pygame.draw.rect(screen, C_OBSTACLE,
                             (ox*CELL, oy*CELL, CELL, CELL))
            pygame.draw.rect(screen, C_DGREY,
                             (ox*CELL, oy*CELL, CELL, CELL), 1)

        # Food
        for f in food_list:
            f.draw(screen)

        # Power-up
        if powerup:
            powerup.draw(screen)

        # Snake
        for i, (sx, sy) in enumerate(body):
            color = snake_color if i > 0 else C_WHITE
            r     = pygame.Rect(sx*CELL+1, sy*CELL+1, CELL-2, CELL-2)
            pygame.draw.rect(screen, color, r, border_radius=4)
            if i == 0 and shield_active:
                pygame.draw.rect(screen, C_PU_SHIELD, r, 2, border_radius=4)

        # HUD
        draw_hud(screen, score, level, personal_best,
                 active_effect, effect_end_t, shield_active)

        pygame.display.flip()
        clock.tick(60)

    pygame.time.set_timer(move_event, 0)
    return score, level