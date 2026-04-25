import pygame
from pygame.locals import *
from persistence import load_leaderboard, save_settings

# ── Palette ────────────────────────────────────────────────────────────────────
C_BG       = (15,  15,  25)
C_ROAD     = (40,  40,  50)
C_WHITE    = (255, 255, 255)
C_GREY     = (160, 160, 170)
C_DGREY    = (60,  60,  75)
C_ACCENT   = (255, 200,  50)   # yellow
C_RED      = (220,  60,  60)
C_GREEN    = (80,  200, 100)
C_BLUE     = (80,  140, 220)
C_PANEL    = (25,  25,  40)

CAR_COLORS = {
    "blue":   (80,  140, 220),
    "red":    (220,  60,  60),
    "green":  (80,  200, 100),
    "yellow": (255, 200,  50),
}

DIFFICULTIES = ["easy", "normal", "hard"]


def _font(size, bold=False):
    return pygame.font.SysFont("Verdana", size, bold=bold)


def _draw_bg(surf):
    surf.fill(C_BG)
    w, h = surf.get_size()
    # Simple lane stripes for atmosphere
    for x in (w // 4, w // 2, 3 * w // 4):
        pygame.draw.rect(surf, C_ROAD, (x - 2, 0, 4, h))


def _btn(surf, rect, text, active=False, font_size=20):
    color = C_ACCENT if active else C_DGREY
    pygame.draw.rect(surf, color, rect, border_radius=8)
    pygame.draw.rect(surf, C_WHITE, rect, 2, border_radius=8)
    lbl = _font(font_size, bold=True).render(text, True, C_BG if active else C_WHITE)
    surf.blit(lbl, lbl.get_rect(center=rect.center))


def _title(surf, text, y, size=52):
    f   = _font(size, bold=True)
    img = f.render(text, True, C_ACCENT)
    surf.blit(img, img.get_rect(centerx=surf.get_width() // 2, top=y))


# ══════════════════════════════════════════════════════════════════════════════
# Username entry
# ══════════════════════════════════════════════════════════════════════════════

def screen_username(surf, clock):
    """Prompt for a player name. Returns the entered string."""
    name   = ""
    f_big  = _font(32, bold=True)
    f_med  = _font(22)
    f_hint = _font(16)
    w, h   = surf.get_size()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); raise SystemExit
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        _draw_bg(surf)
        _title(surf, "RACER", h // 4)

        box = pygame.Rect(w // 2 - 180, h // 2 - 30, 360, 56)
        pygame.draw.rect(surf, C_PANEL, box, border_radius=8)
        pygame.draw.rect(surf, C_ACCENT, box, 2, border_radius=8)

        prompt = f_big.render(name + "|", True, C_WHITE)
        surf.blit(prompt, prompt.get_rect(center=box.center))

        label = f_med.render("Enter your name", True, C_GREY)
        surf.blit(label, label.get_rect(centerx=w // 2, bottom=box.top - 12))

        hint = f_hint.render("Press Enter to continue", True, C_DGREY)
        surf.blit(hint, hint.get_rect(centerx=w // 2, top=box.bottom + 14))

        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Main Menu
# ══════════════════════════════════════════════════════════════════════════════

def screen_main_menu(surf, clock):
    """Returns: 'play' | 'leaderboard' | 'settings' | 'quit'"""
    w, h    = surf.get_size()
    labels  = ["Play", "Leaderboard", "Settings", "Quit"]
    actions = ["play", "leaderboard", "settings", "quit"]
    btn_w, btn_h = 260, 52
    gap          = 18
    total        = len(labels) * btn_h + (len(labels) - 1) * gap
    start_y      = h // 2 - total // 2 + 40

    rects = [
        pygame.Rect(w // 2 - btn_w // 2, start_y + i * (btn_h + gap), btn_w, btn_h)
        for i in range(len(labels))
    ]

    hover = -1
    while True:
        mx, my = pygame.mouse.get_pos()
        hover  = next((i for i, r in enumerate(rects) if r.collidepoint(mx, my)), -1)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); raise SystemExit
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and hover >= 0:
                return actions[hover]
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return "quit"

        _draw_bg(surf)
        _title(surf, "RACER", 60)
        sub = _font(18).render("Extended Edition", True, C_GREY)
        surf.blit(sub, sub.get_rect(centerx=w // 2, top=125))

        for i, (r, lbl) in enumerate(zip(rects, labels)):
            _btn(surf, r, lbl, active=(i == hover), font_size=22)

        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Settings
# ══════════════════════════════════════════════════════════════════════════════

def screen_settings(surf, clock, settings: dict):
    """Mutates settings in-place, saves on Back. Returns updated settings."""
    w, h   = surf.get_size()
    f      = _font(20, bold=True)
    f_lbl  = _font(18)

    def row_rect(i):
        return pygame.Rect(20, 160 + i * 90, w - 40, 56)

    back_rect = pygame.Rect(w // 2 - 100, h - 90, 200, 48)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); raise SystemExit
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                save_settings(settings); return settings
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mx, my):
                    save_settings(settings); return settings

                # Sound toggle
                if row_rect(0).collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]

                # Car color cycle
                colors = list(CAR_COLORS.keys())
                if row_rect(1).collidepoint(mx, my):
                    idx = colors.index(settings["car_color"])
                    settings["car_color"] = colors[(idx + 1) % len(colors)]

                # Difficulty cycle
                if row_rect(2).collidepoint(mx, my):
                    idx = DIFFICULTIES.index(settings["difficulty"])
                    settings["difficulty"] = DIFFICULTIES[(idx + 1) % len(DIFFICULTIES)]

        _draw_bg(surf)
        _title(surf, "SETTINGS", 60, size=42)

        rows = [
            ("Sound",      "ON" if settings["sound"] else "OFF"),
            ("Car Color",  settings["car_color"].capitalize()),
            ("Difficulty", settings["difficulty"].capitalize()),
        ]
        for i, (label, value) in enumerate(rows):
            r = row_rect(i)
            pygame.draw.rect(surf, C_PANEL, r, border_radius=8)
            pygame.draw.rect(surf, C_DGREY, r, 2, border_radius=8)
            lbl_s = f_lbl.render(label, True, C_GREY)
            val_s = f.render(value, True, C_ACCENT)
            surf.blit(lbl_s, (r.x + 16, r.centery - lbl_s.get_height() // 2))
            surf.blit(val_s, (r.right - val_s.get_width() - 16,
                              r.centery - val_s.get_height() // 2))
            hint = _font(12).render("click to change", True, C_DGREY)
            surf.blit(hint, hint.get_rect(centerx=r.centerx, top=r.bottom + 4))

        _btn(surf, back_rect, "Back", active=back_rect.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Leaderboard
# ══════════════════════════════════════════════════════════════════════════════

def screen_leaderboard(surf, clock):
    """Display top 10. Returns when Back is clicked."""
    w, h      = surf.get_size()
    lb        = load_leaderboard()
    back_rect = pygame.Rect(w // 2 - 100, h - 80, 200, 46)
    f_head    = _font(17, bold=True)
    f_row     = _font(16)
    headers   = ["#", "Name", "Score", "Distance", "Coins"]
    col_x     = [60, 110, 310, 430, 560]

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); raise SystemExit
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mx, my):
                    return

        _draw_bg(surf)
        _title(surf, "LEADERBOARD", 40, size=38)

        # Header row
        hy = 110
        for hdr, cx in zip(headers, col_x):
            s = f_head.render(hdr, True, C_ACCENT)
            surf.blit(s, (cx, hy))
        pygame.draw.line(surf, C_DGREY, (50, hy + 28), (w - 50, hy + 28), 1)

        for i, entry in enumerate(lb):
            y     = hy + 40 + i * 38
            color = C_ACCENT if i == 0 else (C_GREY if i < 3 else C_WHITE)
            vals  = [
                str(i + 1),
                entry.get("name", "?")[:12],
                str(entry.get("score", 0)),
                f"{entry.get('distance', 0)} m",
                str(entry.get("coins", 0)),
            ]
            for val, cx in zip(vals, col_x):
                s = f_row.render(val, True, color)
                surf.blit(s, (cx, y))

        if not lb:
            msg = _font(20).render("No scores yet — go race!", True, C_GREY)
            surf.blit(msg, msg.get_rect(centerx=w // 2, top=200))

        _btn(surf, back_rect, "Back", active=back_rect.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Game Over
# ══════════════════════════════════════════════════════════════════════════════

def screen_game_over(surf, clock, score, distance, coins, name):
    """Returns: 'retry' | 'menu'"""
    w, h      = surf.get_size()
    retry_r   = pygame.Rect(w // 2 - 220, h // 2 + 80, 180, 52)
    menu_r    = pygame.Rect(w // 2 + 40,  h // 2 + 80, 180, 52)
    f_big     = _font(28, bold=True)
    f_med     = _font(20)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); raise SystemExit
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if retry_r.collidepoint(mx, my): return "retry"
                if menu_r.collidepoint(mx, my):  return "menu"
            if event.type == KEYDOWN:
                if event.key == K_r: return "retry"
                if event.key == K_ESCAPE: return "menu"

        _draw_bg(surf)
        _title(surf, "GAME OVER", h // 4, size=56)

        lines = [
            f"Player:   {name}",
            f"Score:    {score}",
            f"Distance: {distance} m",
            f"Coins:    {coins}",
        ]
        for i, line in enumerate(lines):
            s = f_med.render(line, True, C_WHITE)
            surf.blit(s, s.get_rect(centerx=w // 2, top=h // 2 - 60 + i * 36))

        _btn(surf, retry_r, "Retry  (R)", active=retry_r.collidepoint(mx, my))
        _btn(surf, menu_r,  "Main Menu", active=menu_r.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)