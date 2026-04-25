import pygame
import random
import time
from pygame.locals import *

# ── Screen / lane geometry ─────────────────────────────────────────────────────
SW = 400
SH = 600
LANE_COUNT  = 3
LANE_XS     = [80, 200, 320]   # center x of each lane
TOOLBAR_H   = 0                # game uses full surface

# ── Difficulty presets ────────────────────────────────────────────────────────
DIFF = {
    "easy":   {"enemy_speed": 3,  "spawn_enemy": 4000, "spawn_obs": 6000, "base_inc": 0.15},
    "normal": {"enemy_speed": 5,  "spawn_enemy": 3000, "spawn_obs": 4000, "base_inc": 0.25},
    "hard":   {"enemy_speed": 7,  "spawn_enemy": 2000, "spawn_obs": 2500, "base_inc": 0.40},
}

# ── Colors ────────────────────────────────────────────────────────────────────
C_WHITE  = (255, 255, 255)
C_BLACK  = (0,   0,   0)
C_YELLOW = (255, 215,   0)
C_GOLD   = (255, 215,   0)
C_SILVER = (192, 192, 192)
C_BRONZE = (205, 127,  50)
C_RED    = (220,  60,  60)
C_GREEN  = (80,  200, 100)
C_BLUE   = (80,  140, 220)
C_ORANGE = (255, 140,   0)
C_PURPLE = (160,  60, 220)
C_CYAN   = (0,   220, 220)
C_GREY   = (120, 120, 130)
C_DKGREY = (40,   40,  50)
C_OIL    = (30,   30,  40)
C_NITRO  = (0,   240, 200)

CAR_COLOR_MAP = {
    "blue":   C_BLUE,
    "red":    C_RED,
    "green":  C_GREEN,
    "yellow": C_YELLOW,
}

# ── Coin types (inherited from Practice 11) ────────────────────────────────────
COIN_TYPES = [
    {"color": C_BRONZE, "value": 1, "weight": 60, "label": "B", "radius": 12},
    {"color": C_SILVER, "value": 3, "weight": 30, "label": "S", "radius": 14},
    {"color": C_GOLD,   "value": 5, "weight": 10, "label": "G", "radius": 16},
]
_COIN_W = [c["weight"] for c in COIN_TYPES]


def _rnd_coin():
    return random.choices(COIN_TYPES, weights=_COIN_W, k=1)[0]


def _lane_x():
    return random.choice(LANE_XS)


# ══════════════════════════════════════════════════════════════════════════════
# Sprite classes
# ══════════════════════════════════════════════════════════════════════════════

class Player(pygame.sprite.Sprite):
    def __init__(self, img, car_color):
        super().__init__()
        if img:
            self.image = img
        else:
            self.image = pygame.Surface((36, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.image, car_color, (0, 0, 36, 60), border_radius=8)
        self.rect        = self.image.get_rect(center=(SW // 2, SH - 80))
        self.shield      = False
        self.nitro       = False
        self.nitro_boost = 0   # extra speed px/frame

    def move(self, enemy_speed):
        keys = pygame.key.get_pressed()
        spd  = 6 + (3 if self.nitro else 0)
        if keys[K_LEFT]  and self.rect.left  > 20:  self.rect.x -= spd
        if keys[K_RIGHT] and self.rect.right < SW-20: self.rect.x += spd


class Enemy(pygame.sprite.Sprite):
    def __init__(self, img, speed, player_rect):
        super().__init__()
        if img:
            self.image = img
        else:
            self.image = pygame.Surface((36, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.image, C_RED, (0, 0, 36, 60), border_radius=8)
        # Safe spawn — not directly on top of player
        for _ in range(20):
            x = _lane_x()
            if abs(x - player_rect.centerx) > 60 or player_rect.top > 100:
                break
        self.rect  = self.image.get_rect(center=(x, -40))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > SH   # True = off screen


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self._pick()

    def _pick(self):
        ct     = _rnd_coin()
        self.value = ct["value"]
        r      = ct["radius"]
        self.image = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ct["color"], (r+1, r+1), r)
        f  = pygame.font.SysFont("Verdana", r, bold=True)
        ls = f.render(ct["label"], True, C_BLACK)
        self.image.blit(ls, ls.get_rect(center=(r+1, r+1)))
        self.rect = self.image.get_rect(center=(_lane_x(), -20))

    def update(self):
        self.rect.y += 3
        if self.rect.top > SH:
            self._pick()
            self.rect.top = -20


class Obstacle(pygame.sprite.Sprite):
    """Oil spill, pothole, or barrier."""
    KIND_PROPS = {
        "oil":     {"color": C_OIL,    "size": (50, 30), "slow": True,  "label": "OIL"},
        "pothole": {"color": C_DKGREY, "size": (30, 30), "slow": False, "label": "⚠"},
        "barrier": {"color": C_ORANGE, "size": (60, 20), "slow": False, "label": "|||"},
    }

    def __init__(self, speed, player_rect):
        super().__init__()
        self.kind  = random.choice(list(self.KIND_PROPS.keys()))
        props      = self.KIND_PROPS[self.kind]
        self.slow  = props["slow"]
        w, h       = props["size"]
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.image, props["color"], (0, 0, w, h), border_radius=6)
        f  = pygame.font.SysFont("Verdana", 11, bold=True)
        ls = f.render(props["label"], True, C_WHITE)
        self.image.blit(ls, ls.get_rect(center=(w//2, h//2)))
        # Safe spawn
        for _ in range(20):
            x = _lane_x()
            if abs(x - player_rect.centerx) > 50 or player_rect.top > 120:
                break
        self.rect  = self.image.get_rect(center=(x, -30))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > SH


class PowerUp(pygame.sprite.Sprite):
    KINDS = {
        "nitro":  {"color": C_NITRO,  "label": "NIT", "duration": 4},
        "shield": {"color": C_CYAN,   "label": "SHD", "duration": 0},   # until hit
        "repair": {"color": C_GREEN,  "label": "REP", "duration": 0},   # instant
    }
    TIMEOUT = 8000   # ms before it disappears uncollected

    def __init__(self, speed):
        super().__init__()
        self.kind     = random.choice(list(self.KINDS.keys()))
        props         = self.KINDS[self.kind]
        self.duration = props["duration"]
        self.spawn_t  = pygame.time.get_ticks()
        r             = 18
        self.image    = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, props["color"], (r, r), r)
        pygame.draw.circle(self.image, C_WHITE, (r, r), r, 2)
        f  = pygame.font.SysFont("Verdana", 11, bold=True)
        ls = f.render(props["label"], True, C_BLACK)
        self.image.blit(ls, ls.get_rect(center=(r, r)))
        self.rect  = self.image.get_rect(center=(_lane_x(), -20))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SH:
            return True
        if pygame.time.get_ticks() - self.spawn_t > self.TIMEOUT:
            return True
        return False


class NitroStrip(pygame.sprite.Sprite):
    """Road event: a green nitro boost strip crossing a lane."""
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((SW, 18), pygame.SRCALPHA)
        self.image.fill((0, 240, 120, 160))
        f  = pygame.font.SysFont("Verdana", 11, bold=True)
        ls = f.render("◀ NITRO STRIP ▶", True, C_BLACK)
        self.image.blit(ls, ls.get_rect(center=(SW//2, 9)))
        self.rect  = self.image.get_rect(topleft=(0, -20))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > SH


class SpeedBump(pygame.sprite.Sprite):
    """Road event: a full-width speed bump that briefly slows enemies."""
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((SW, 14), pygame.SRCALPHA)
        self.image.fill((180, 120, 40, 200))
        f  = pygame.font.SysFont("Verdana", 10, bold=True)
        ls = f.render("SPEED BUMP", True, C_WHITE)
        self.image.blit(ls, ls.get_rect(center=(SW//2, 7)))
        self.rect  = self.image.get_rect(topleft=(0, -20))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > SH


# ══════════════════════════════════════════════════════════════════════════════
# HUD helpers
# ══════════════════════════════════════════════════════════════════════════════

def _hud(surf, score, distance, coins, enemy_speed, active_pu, pu_end_t, shield):
    f_sm = pygame.font.SysFont("Verdana", 15, bold=True)
    f_ti = pygame.font.SysFont("Verdana", 12)

    # Score / coins / distance
    surf.blit(f_sm.render(f"Score: {score}", True, C_WHITE), (8, 8))
    surf.blit(f_sm.render(f"Coins: {coins}", True, C_YELLOW), (8, 28))
    surf.blit(f_sm.render(f"Dist:  {distance}m", True, C_WHITE), (8, 48))

    # Speed (top-right)
    spd = f_ti.render(f"Spd:{enemy_speed:.1f}", True, C_GREY)
    surf.blit(spd, (SW - spd.get_width() - 6, 8))

    # Active power-up
    if active_pu:
        now    = pygame.time.get_ticks()
        remain = max(0, (pu_end_t - now) / 1000) if pu_end_t else 0
        col    = {"nitro": C_NITRO, "shield": C_CYAN, "repair": C_GREEN}.get(active_pu, C_WHITE)
        label  = active_pu.upper()
        if pu_end_t:
            label += f" {remain:.1f}s"
        pu_s = f_sm.render(label, True, col)
        surf.blit(pu_s, pu_s.get_rect(centerx=SW//2, top=8))

    # Shield indicator
    if shield:
        sh_s = f_ti.render("🛡 SHIELD", True, C_CYAN)
        surf.blit(sh_s, sh_s.get_rect(centerx=SW//2, top=30))


# ══════════════════════════════════════════════════════════════════════════════
# Main game function
# ══════════════════════════════════════════════════════════════════════════════

def run_game(surf, clock, settings, player_name):
    """
    Run one full race. Returns (score, distance, coins).
    """
    diff_key  = settings.get("difficulty", "normal")
    d         = DIFF[diff_key]
    sound_on  = settings.get("sound", True)
    car_color = CAR_COLOR_MAP.get(settings.get("car_color", "blue"), C_BLUE)

    # Load assets
    try:
        bg_img     = pygame.image.load("assets/AnimatedStreet.png").convert()
        player_img = pygame.image.load("assets/Player.png").convert_alpha()
        enemy_img  = pygame.image.load("assets/Enemy.png").convert_alpha()
    except Exception:
        bg_img = player_img = enemy_img = None

    try:
        crash_snd = pygame.mixer.Sound("assets/crash.wav") if sound_on else None
    except Exception:
        crash_snd = None

    # Mutable game state
    enemy_speed      = d["enemy_speed"]
    score            = 0
    coins_collected  = 0
    distance         = 0
    crash_count      = 0      # how many crashes survived (via shield/repair)
    active_pu        = None   # "nitro" | "shield" | "repair" | None
    pu_end_time      = None
    slowed           = False  # oil spill slow effect
    slow_until       = 0

    # Sprites
    all_sprites = pygame.sprite.Group()
    enemies     = pygame.sprite.Group()
    coins_grp   = pygame.sprite.Group()
    obstacles   = pygame.sprite.Group()
    powerups    = pygame.sprite.Group()
    events_grp  = pygame.sprite.Group()

    player = Player(player_img, car_color)
    all_sprites.add(player)

    # Spawn initial enemies and coins
    for _ in range(2):
        e = Enemy(enemy_img, enemy_speed, player.rect)
        enemies.add(e); all_sprites.add(e)
    for _ in range(3):
        c = Coin()
        coins_grp.add(c); all_sprites.add(c)

    # Custom timer events
    EV_INC_SPEED  = pygame.USEREVENT + 1
    EV_ADD_ENEMY  = pygame.USEREVENT + 2
    EV_ADD_OBS    = pygame.USEREVENT + 3
    EV_ADD_PU     = pygame.USEREVENT + 4
    EV_ROAD_EVENT = pygame.USEREVENT + 5
    EV_ADD_COIN   = pygame.USEREVENT + 6

    pygame.time.set_timer(EV_INC_SPEED,  1000)
    pygame.time.set_timer(EV_ADD_ENEMY,  d["spawn_enemy"])
    pygame.time.set_timer(EV_ADD_OBS,    d["spawn_obs"])
    pygame.time.set_timer(EV_ADD_PU,     7000)
    pygame.time.set_timer(EV_ROAD_EVENT, 5000)
    pygame.time.set_timer(EV_ADD_COIN,   4000)

    # Scrolling background
    bg_y1, bg_y2 = 0, -SH
    BG_SCROLL    = 2

    running = True
    while running:
        now = pygame.time.get_ticks()

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); raise SystemExit
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False   # bail to game-over

            if event.type == EV_INC_SPEED:
                enemy_speed += d["base_inc"]
                distance    += 5

            if event.type == EV_ADD_ENEMY:
                e = Enemy(enemy_img, enemy_speed, player.rect)
                enemies.add(e); all_sprites.add(e)

            if event.type == EV_ADD_OBS:
                o = Obstacle(enemy_speed * 0.7, player.rect)
                obstacles.add(o); all_sprites.add(o)

            if event.type == EV_ADD_PU and active_pu is None:
                p = PowerUp(enemy_speed * 0.6)
                powerups.add(p); all_sprites.add(p)

            if event.type == EV_ROAD_EVENT:
                if random.random() < 0.5:
                    ev = NitroStrip(enemy_speed * 0.5)
                else:
                    ev = SpeedBump(enemy_speed * 0.5)
                events_grp.add(ev); all_sprites.add(ev)

            if event.type == EV_ADD_COIN:
                c = Coin()
                coins_grp.add(c); all_sprites.add(c)

        # ── Power-up expiry ───────────────────────────────────────────────────
        if active_pu == "nitro" and pu_end_time and now > pu_end_time:
            active_pu      = None
            pu_end_time    = None
            player.nitro   = False

        # ── Oil slow expiry ───────────────────────────────────────────────────
        if slowed and now > slow_until:
            slowed = False

        # ── Move player ───────────────────────────────────────────────────────
        player.move(enemy_speed)

        # ── Update enemies ────────────────────────────────────────────────────
        for e in list(enemies):
            gone = e.update()
            if gone:
                score += 1
                enemies.remove(e); all_sprites.remove(e)

        # ── Update coins ──────────────────────────────────────────────────────
        for c in list(coins_grp):
            c.update()

        # ── Update obstacles ──────────────────────────────────────────────────
        for o in list(obstacles):
            gone = o.update()
            if gone:
                obstacles.remove(o); all_sprites.remove(o)

        # ── Update power-ups ──────────────────────────────────────────────────
        for p in list(powerups):
            gone = p.update()
            if gone:
                powerups.remove(p); all_sprites.remove(p)

        # ── Update road events ────────────────────────────────────────────────
        for ev in list(events_grp):
            gone = ev.update()
            if gone:
                events_grp.remove(ev); all_sprites.remove(ev)

        # ── Coin collection ───────────────────────────────────────────────────
        for c in pygame.sprite.spritecollide(player, coins_grp, False):
            coins_collected += c.value
            score           += c.value * 2
            c._pick()

        # ── Power-up collection ───────────────────────────────────────────────
        for p in pygame.sprite.spritecollide(player, powerups, True):
            all_sprites.remove(p)
            if active_pu != p.kind:   # only one at a time
                active_pu = p.kind
                if p.kind == "nitro":
                    player.nitro = True
                    pu_end_time  = now + p.duration * 1000
                elif p.kind == "shield":
                    player.shield = True
                    pu_end_time   = None
                elif p.kind == "repair":
                    # Clears one obstacle near the player
                    near = pygame.sprite.spritecollide(player, obstacles, True)
                    for n in near:
                        all_sprites.discard(n)
                    active_pu = None   # instant

        # ── Obstacle collision ────────────────────────────────────────────────
        for o in pygame.sprite.spritecollide(player, obstacles, True):
            all_sprites.remove(o)
            if o.slow:
                slowed     = True
                slow_until = now + 2000
            else:
                if player.shield:
                    player.shield = False
                    active_pu     = None
                else:
                    running = False   # crash

        # ── Road-event collision ──────────────────────────────────────────────
        for ev in pygame.sprite.spritecollide(player, events_grp, False):
            if isinstance(ev, NitroStrip) and active_pu is None:
                active_pu    = "nitro"
                player.nitro = True
                pu_end_time  = now + 3000
            # SpeedBump: visual only — handled by obstacle logic

        # ── Enemy collision → Game Over ───────────────────────────────────────
        if pygame.sprite.spritecollideany(player, enemies):
            if player.shield:
                player.shield = False
                active_pu     = None
                # Remove that enemy
                for e in pygame.sprite.spritecollide(player, enemies, True):
                    all_sprites.remove(e)
            else:
                if crash_snd:
                    crash_snd.play()
                time.sleep(0.3)
                running = False

        # ── Scrolling background ──────────────────────────────────────────────
        bg_y1 += BG_SCROLL + (1 if slowed else 0)
        bg_y2 += BG_SCROLL + (1 if slowed else 0)
        if bg_y1 >= SH: bg_y1 = -SH
        if bg_y2 >= SH: bg_y2 = -SH

        if bg_img:
            surf.blit(bg_img, (0, bg_y1))
            surf.blit(bg_img, (0, bg_y2))
        else:
            surf.fill((50, 50, 60))
            for lx in LANE_XS:
                pygame.draw.rect(surf, (80, 80, 90), (lx - 2, 0, 4, SH))

        # ── Draw road events first (under cars) ───────────────────────────────
        for ev in events_grp:
            surf.blit(ev.image, ev.rect)
        for o in obstacles:
            surf.blit(o.image, o.rect)
        for c in coins_grp:
            surf.blit(c.image, c.rect)
        for p in powerups:
            surf.blit(p.image, p.rect)
        for e in enemies:
            surf.blit(e.image, e.rect)

        # Shield glow around player
        if player.shield:
            pygame.draw.circle(surf, C_CYAN,
                               player.rect.center,
                               max(player.rect.width, player.rect.height) // 2 + 8, 3)
        surf.blit(player.image, player.rect)

        # ── HUD ───────────────────────────────────────────────────────────────
        _hud(surf, score, distance, coins_collected,
             enemy_speed, active_pu, pu_end_time, player.shield)

        # Slow warning
        if slowed:
            w_s = pygame.font.SysFont("Verdana", 14, bold=True).render(
                "OIL — SLOWED!", True, C_OIL)
            surf.blit(w_s, w_s.get_rect(centerx=SW//2, top=SH - 40))

        pygame.display.flip()
        clock.tick(60)

    # ── Clean up timers ───────────────────────────────────────────────────────
    for ev in (EV_INC_SPEED, EV_ADD_ENEMY, EV_ADD_OBS,
               EV_ADD_PU, EV_ROAD_EVENT, EV_ADD_COIN):
        pygame.time.set_timer(ev, 0)

    return score, distance, coins_collected