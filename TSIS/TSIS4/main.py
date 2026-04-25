import pygame
import sys
import json
import os
from pygame.locals import *

import db
from game import run_game, load_settings, save_settings
from config import SW, SH, CELL, COLS, ROWS

# ── Palette (local to UI) ──────────────────────────────────────────────────────
C_BG     = (15,  20,  30)
C_PANEL  = (22,  28,  42)
C_ACCENT = (80,  200, 140)
C_YELLOW = (255, 200,  50)
C_WHITE  = (255, 255, 255)
C_GREY   = (140, 150, 165)
C_DGREY  = (50,  55,  70)
C_RED    = (220,  60,  60)
C_BLACK  = (0,   0,   0)

SNAKE_COLOR_OPTIONS = [
    (80,  200, 140),   # green
    (80,  140, 220),   # blue
    (220,  80,  80),   # red
    (255, 200,  50),   # yellow
    (200,  80, 220),   # purple
]


def _font(size, bold=False):
    return pygame.font.SysFont("Verdana", size, bold=bold)


def _draw_bg(surf):
    surf.fill(C_BG)
    # Subtle grid lines for atmosphere
    for x in range(0, SW, CELL*3):
        pygame.draw.line(surf, (22, 28, 42), (x, 0), (x, SH))
    for y in range(0, SH, CELL*3):
        pygame.draw.line(surf, (22, 28, 42), (0, y), (SW, y))


def _title(surf, text, y, size=48, color=None):
    color = color or C_ACCENT
    f   = _font(size, bold=True)
    img = f.render(text, True, color)
    surf.blit(img, img.get_rect(centerx=SW//2, top=y))


def _btn(surf, rect, text, active=False, size=18):
    bg  = C_ACCENT if active else C_DGREY
    fg  = C_BLACK  if active else C_WHITE
    pygame.draw.rect(surf, bg, rect, border_radius=7)
    pygame.draw.rect(surf, C_WHITE, rect, 1, border_radius=7)
    lbl = _font(size, bold=True).render(text, True, fg)
    surf.blit(lbl, lbl.get_rect(center=rect.center))


# ══════════════════════════════════════════════════════════════════════════════
# Username entry
# ══════════════════════════════════════════════════════════════════════════════
def screen_username(surf, clock) -> str:
    name  = ""
    f_big = _font(28, bold=True)
    f_med = _font(18)
    f_hint= _font(13)
    w, h  = SW, SH

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        _draw_bg(surf)
        _title(surf, "SNAKE", 60)

        lbl = f_med.render("Enter your username:", True, C_GREY)
        surf.blit(lbl, lbl.get_rect(centerx=w//2, top=h//2 - 60))

        box = pygame.Rect(w//2 - 160, h//2 - 28, 320, 52)
        pygame.draw.rect(surf, C_PANEL, box, border_radius=8)
        pygame.draw.rect(surf, C_ACCENT, box, 2, border_radius=8)
        t = f_big.render(name + "|", True, C_WHITE)
        surf.blit(t, t.get_rect(center=box.center))

        hint = f_hint.render("Press Enter to start", True, C_DGREY)
        surf.blit(hint, hint.get_rect(centerx=w//2, top=box.bottom + 12))

        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Main Menu
# ══════════════════════════════════════════════════════════════════════════════
def screen_main_menu(surf, clock) -> str:
    labels  = ["Play", "Leaderboard", "Settings", "Quit"]
    actions = ["play", "leaderboard", "settings", "quit"]
    bw, bh  = 220, 48
    gap     = 14
    total   = len(labels) * bh + (len(labels)-1) * gap
    sy      = SH//2 - total//2 + 30
    rects   = [pygame.Rect(SW//2 - bw//2, sy + i*(bh+gap), bw, bh)
               for i in range(len(labels))]

    while True:
        mx, my = pygame.mouse.get_pos()
        hover  = next((i for i, r in enumerate(rects) if r.collidepoint(mx, my)), -1)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and hover >= 0:
                return actions[hover]
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return "quit"

        _draw_bg(surf)
        _title(surf, "SNAKE", 55)
        sub = _font(15).render("Extended Edition", True, C_GREY)
        surf.blit(sub, sub.get_rect(centerx=SW//2, top=115))

        for i, (r, lbl) in enumerate(zip(rects, labels)):
            _btn(surf, r, lbl, active=(i == hover))

        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Leaderboard
# ══════════════════════════════════════════════════════════════════════════════
def screen_leaderboard(surf, clock):
    lb        = db.get_leaderboard(10)
    back_r    = pygame.Rect(SW//2 - 90, SH - 68, 180, 44)
    f_h       = _font(14, bold=True)
    f_r       = _font(13)
    headers   = ["#", "Player", "Score", "Lvl", "Date"]
    col_x     = [14, 40, 190, 270, 330]

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if back_r.collidepoint(mx, my):
                    return

        _draw_bg(surf)
        _title(surf, "LEADERBOARD", 28, size=34)

        hy = 88
        for hdr, cx in zip(headers, col_x):
            surf.blit(f_h.render(hdr, True, C_ACCENT), (cx, hy))
        pygame.draw.line(surf, C_DGREY, (10, hy+22), (SW-10, hy+22), 1)

        row_colors = [C_YELLOW, C_GREY, C_GREY] + [C_WHITE]*7
        for i, entry in enumerate(lb):
            y   = hy + 34 + i*34
            col = row_colors[i] if i < len(row_colors) else C_WHITE
            vals = [str(i+1), entry["username"][:14],
                    str(entry["score"]), str(entry["level"]), entry["date"]]
            for val, cx in zip(vals, col_x):
                surf.blit(f_r.render(val, True, col), (cx, y))

        if not lb:
            msg = _font(16).render("No scores yet — play a game!", True, C_GREY)
            surf.blit(msg, msg.get_rect(centerx=SW//2, top=200))

        db_warn = _font(11).render(
            "DB offline — showing cached data" if not lb and db._conn is None else "",
            True, C_RED)
        surf.blit(db_warn, (10, SH - 90))

        _btn(surf, back_r, "Back", active=back_r.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Settings
# ══════════════════════════════════════════════════════════════════════════════
def screen_settings(surf, clock):
    settings = load_settings()
    color_idx = next(
        (i for i, c in enumerate(SNAKE_COLOR_OPTIONS)
         if list(c) == settings["snake_color"]), 0)

    save_r  = pygame.Rect(SW//2 - 100, SH - 68, 200, 44)
    f_lbl   = _font(17, bold=True)
    f_val   = _font(17)
    f_hint  = _font(12)

    def row_r(i):
        return pygame.Rect(20, 140 + i*90, SW-40, 54)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                save_settings(settings); return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if save_r.collidepoint(mx, my):
                    save_settings(settings); return
                if row_r(0).collidepoint(mx, my):
                    color_idx = (color_idx + 1) % len(SNAKE_COLOR_OPTIONS)
                    settings["snake_color"] = list(SNAKE_COLOR_OPTIONS[color_idx])
                if row_r(1).collidepoint(mx, my):
                    settings["grid"] = not settings["grid"]
                if row_r(2).collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]

        _draw_bg(surf)
        _title(surf, "SETTINGS", 36, size=36)

        rows = [
            ("Snake Color", "●"),
            ("Grid Overlay", "ON" if settings["grid"]  else "OFF"),
            ("Sound",        "ON" if settings["sound"] else "OFF"),
        ]
        for i, (lbl, val) in enumerate(rows):
            r = row_r(i)
            pygame.draw.rect(surf, C_PANEL, r, border_radius=8)
            pygame.draw.rect(surf, C_DGREY, r, 1, border_radius=8)
            surf.blit(f_lbl.render(lbl, True, C_GREY),
                      (r.x+14, r.centery - 10))
            if i == 0:
                # Draw color swatch
                sc = tuple(settings["snake_color"])
                pygame.draw.circle(surf, sc, (r.right - 30, r.centery), 14)
                pygame.draw.circle(surf, C_WHITE, (r.right - 30, r.centery), 14, 2)
            else:
                col = C_ACCENT if val == "ON" else C_RED
                surf.blit(f_val.render(val, True, col),
                          (r.right - f_val.size(val)[0] - 14, r.centery - 10))
            hint = f_hint.render("click to change", True, C_DGREY)
            surf.blit(hint, hint.get_rect(centerx=r.centerx, top=r.bottom+4))

        _btn(surf, save_r, "Save & Back", active=save_r.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Game Over
# ══════════════════════════════════════════════════════════════════════════════
def screen_game_over(surf, clock, score, level, personal_best, username) -> str:
    retry_r = pygame.Rect(SW//2 - 190, SH//2 + 70, 160, 48)
    menu_r  = pygame.Rect(SW//2 + 30,  SH//2 + 70, 160, 48)
    f_big   = _font(24, bold=True)
    f_med   = _font(17)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if retry_r.collidepoint(mx, my): return "retry"
                if menu_r.collidepoint(mx, my):  return "menu"
            if event.type == KEYDOWN:
                if event.key == K_r:      return "retry"
                if event.key == K_ESCAPE: return "menu"

        _draw_bg(surf)
        _title(surf, "GAME OVER", SH//4, size=50, color=C_RED)

        lines = [
            (f"Player:        {username}", C_WHITE),
            (f"Score:         {score}",    C_YELLOW),
            (f"Level reached: {level}",    C_ACCENT),
            (f"Personal best: {max(score, personal_best)}", C_GREY),
        ]
        for i, (txt, col) in enumerate(lines):
            s = f_med.render(txt, True, col)
            surf.blit(s, s.get_rect(centerx=SW//2, top=SH//2 - 50 + i*34))

        _btn(surf, retry_r, "Retry  [R]", active=retry_r.collidepoint(mx, my))
        _btn(surf, menu_r,  "Main Menu",  active=menu_r.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════
def main():
    pygame.init()
    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("Snake — Extended")
    clock  = pygame.time.Clock()

    # Try to connect to DB (non-fatal if it fails)
    db_ok = db.init_db()
    if not db_ok:
        print("[main] Running without database — scores will not be saved.")

    username      = None
    personal_best = 0

    while True:
        action = screen_main_menu(screen, clock)

        if action == "quit":
            db.close()
            pygame.quit()
            sys.exit()

        elif action == "leaderboard":
            screen_leaderboard(screen, clock)

        elif action == "settings":
            screen_settings(screen, clock)

        elif action == "play":
            if username is None:
                username      = screen_username(screen, clock)
                personal_best = db.get_personal_best(username)

            while True:
                score, level = run_game(screen, clock, username, personal_best)

                # Save to DB
                if db_ok:
                    db.save_session(username, score, level)

                personal_best = max(personal_best, score)

                result = screen_game_over(
                    screen, clock, score, level, personal_best, username)

                if result == "retry":
                    continue
                else:
                    break   # back to main menu


if __name__ == "__main__":
    main()