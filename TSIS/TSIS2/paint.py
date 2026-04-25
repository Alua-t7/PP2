import pygame
import sys
from datetime import datetime
from pygame.locals import *

# Import all tool classes from tools.py
from tools import (
    BRUSH_SIZES,
    PencilTool, LineTool, RectTool, CircleTool, EraserTool,
    SquareTool, RightTriangleTool, EquilTriangleTool, RhombusTool,
    FillTool, TextTool,
)

# ─── Window / Canvas layout ────────────────────────────────────────────────────
TOOLBAR_H   = 110          # height of the top toolbar
CANVAS_W    = 900
CANVAS_H    = 600
WIN_W       = CANVAS_W
WIN_H       = CANVAS_H + TOOLBAR_H

# ─── Palette ───────────────────────────────────────────────────────────────────
PALETTE = [
    (0,   0,   0),   (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255,   0,   0), (128,   0,   0), (255, 165,   0), (255, 255,   0),
    (0,   255,   0), (0,   128,   0), (0,   255, 255), (0,   0,   255),
    (0,   0,   128), (128,   0, 128), (255,   0, 255), (255, 182, 193),
    (165,  42,  42), (255, 140,   0), (173, 255,  47), (0,   206, 209),
]

SWATCH_SIZE = 24
SWATCH_GAP  = 4
PALETTE_X   = 10
PALETTE_Y   = 10

# ─── Tool list ────────────────────────────────────────────────────────────────
TOOL_NAMES = [
    "Pencil", "Line", "Rect", "Circle", "Eraser",
    "Square", "RTriangle", "EqTriangle", "Rhombus",
    "Fill", "Text",
]

TOOL_OBJECTS = {
    "Pencil":     PencilTool(),
    "Line":       LineTool(),
    "Rect":       RectTool(),
    "Circle":     CircleTool(),
    "Eraser":     EraserTool(),
    "Square":     SquareTool(),
    "RTriangle":  RightTriangleTool(),
    "EqTriangle": EquilTriangleTool(),
    "Rhombus":    RhombusTool(),
    "Fill":       FillTool(),
    "Text":       TextTool(),
}

# Tool button layout: two rows in the toolbar
TOOLS_PER_ROW  = 6
TOOL_BTN_W     = 86
TOOL_BTN_H     = 28
TOOL_BTN_GAP   = 4
TOOLS_START_X  = PALETTE_X + (SWATCH_SIZE + SWATCH_GAP) * 10 + 16
TOOLS_START_Y  = PALETTE_Y

# Brush size button layout (right side)
BRUSH_START_X  = WIN_W - 160
BRUSH_START_Y  = PALETTE_Y

# ─── Colors ───────────────────────────────────────────────────────────────────
BG_TOOLBAR  = (45,  45,  55)
BG_CANVAS   = (255, 255, 255)
CLR_BTN_ACT = (90, 160, 255)
CLR_BTN_NRM = (70,  70,  85)
CLR_TEXT    = (230, 230, 230)
CLR_OUTLINE = (20,  20,  30)

# ──────────────────────────────────────────────────────────────────────────────
pygame.init()

screen  = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Paint — Extended")

# The canvas is a separate surface so we can save it cleanly
canvas  = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG_CANVAS)

font_ui   = pygame.font.SysFont("Segoe UI", 13, bold=True)
font_tiny = pygame.font.SysFont("Segoe UI", 11)

clock = pygame.time.Clock()

# ─── State ────────────────────────────────────────────────────────────────────
current_tool   = "Pencil"
current_color  = (0, 0, 0)
current_size   = BRUSH_SIZES[1]   # start on "small"
current_brush_key = 1             # 1 / 2 / 3


# ─── Helper: build rects for UI elements ──────────────────────────────────────

def palette_rect(i):
    col = i % 10
    row = i // 10
    x = PALETTE_X + col * (SWATCH_SIZE + SWATCH_GAP)
    y = PALETTE_Y + row * (SWATCH_SIZE + SWATCH_GAP)
    return pygame.Rect(x, y, SWATCH_SIZE, SWATCH_SIZE)


def tool_btn_rect(i):
    row = i // TOOLS_PER_ROW
    col = i %  TOOLS_PER_ROW
    x = TOOLS_START_X + col * (TOOL_BTN_W + TOOL_BTN_GAP)
    y = TOOLS_START_Y + row * (TOOL_BTN_H + TOOL_BTN_GAP)
    return pygame.Rect(x, y, TOOL_BTN_W, TOOL_BTN_H)


def brush_btn_rect(key):
    """key = 1, 2, or 3"""
    idx = key - 1
    x   = BRUSH_START_X
    y   = BRUSH_START_Y + idx * (TOOL_BTN_H + TOOL_BTN_GAP)
    return pygame.Rect(x, y, 90, TOOL_BTN_H)


# ─── Drawing helpers ──────────────────────────────────────────────────────────

def draw_toolbar(surf):
    pygame.draw.rect(surf, BG_TOOLBAR, (0, 0, WIN_W, TOOLBAR_H))

    # ── Palette ──
    for i, col in enumerate(PALETTE):
        r = palette_rect(i)
        pygame.draw.rect(surf, col, r)
        if col == current_color:
            pygame.draw.rect(surf, (255, 255, 255), r, 3)
            pygame.draw.rect(surf, CLR_OUTLINE,    r, 1)
        else:
            pygame.draw.rect(surf, CLR_OUTLINE, r, 1)

    # ── Tool buttons ──
    for i, name in enumerate(TOOL_NAMES):
        r       = tool_btn_rect(i)
        active  = (name == current_tool)
        bg      = CLR_BTN_ACT if active else CLR_BTN_NRM
        pygame.draw.rect(surf, bg, r, border_radius=5)
        pygame.draw.rect(surf, CLR_OUTLINE, r, 1, border_radius=5)
        label   = font_ui.render(name, True, CLR_TEXT)
        surf.blit(label, label.get_rect(center=r.center))

    # ── Brush size buttons ──
    size_labels = {1: "S (1px thin)", 2: "M (5px mid)", 3: "L (10px thick)"}
    for k in (1, 2, 3):
        r      = brush_btn_rect(k)
        active = (k == current_brush_key)
        bg     = CLR_BTN_ACT if active else CLR_BTN_NRM
        pygame.draw.rect(surf, bg, r, border_radius=5)
        pygame.draw.rect(surf, CLR_OUTLINE, r, 1, border_radius=5)
        lbl    = font_ui.render(size_labels[k], True, CLR_TEXT)
        surf.blit(lbl, lbl.get_rect(center=r.center))

    # ── Active color swatch ──
    swatch_r = pygame.Rect(WIN_W - 55, TOOLBAR_H - 38, 40, 30)
    pygame.draw.rect(surf, current_color, swatch_r)
    pygame.draw.rect(surf, CLR_OUTLINE, swatch_r, 2)
    hint = font_tiny.render("color", True, CLR_TEXT)
    surf.blit(hint, (swatch_r.x, swatch_r.y - 14))

    # ── Ctrl+S hint ──
    save_hint = font_tiny.render("Ctrl+S = save PNG", True, (160, 160, 170))
    surf.blit(save_hint, (BRUSH_START_X, BRUSH_START_Y + 3 * (TOOL_BTN_H + TOOL_BTN_GAP) + 4))


def canvas_pos(screen_pos):
    """Convert screen coordinate to canvas coordinate."""
    return (screen_pos[0], screen_pos[1] - TOOLBAR_H)


def in_canvas(screen_pos):
    return screen_pos[1] >= TOOLBAR_H


def save_canvas():
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"canvas_{ts}.png"
    pygame.image.save(canvas, name)
    print(f"[Paint] Canvas saved → {name}")
    return name


# ─── Main loop ────────────────────────────────────────────────────────────────
running = True

while running:
    mouse_pos    = pygame.mouse.get_pos()
    mouse_btns   = pygame.mouse.get_pressed()
    canvas_mouse = canvas_pos(mouse_pos)
    tool_obj     = TOOL_OBJECTS[current_tool]

    for event in pygame.event.get():

        if event.type == QUIT:
            running = False

        # ── Keyboard ──────────────────────────────────────────────────────────
        elif event.type == KEYDOWN:

            # Brush size shortcuts
            if event.key in (K_1, K_2, K_3):
                k = event.key - K_0          # 49→1, 50→2, 51→3
                current_brush_key = k
                current_size      = BRUSH_SIZES[k]

            # Save
            elif event.key == K_s and (pygame.key.get_mods() & KMOD_CTRL):
                save_canvas()

            # Escape — cancel text
            elif event.key == K_ESCAPE:
                if current_tool == "Text":
                    TOOL_OBJECTS["Text"].active = False

            # All other keys → text tool
            else:
                if current_tool == "Text":
                    TOOL_OBJECTS["Text"].handle_key(canvas, event, current_color)

        # ── Mouse down ────────────────────────────────────────────────────────
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Click in toolbar
            if pos[1] < TOOLBAR_H:
                # Palette swatches
                for i, col in enumerate(PALETTE):
                    if palette_rect(i).collidepoint(pos):
                        current_color = col
                        break

                # Tool buttons
                for i, name in enumerate(TOOL_NAMES):
                    if tool_btn_rect(i).collidepoint(pos):
                        current_tool = name
                        break

                # Brush size buttons
                for k in (1, 2, 3):
                    if brush_btn_rect(k).collidepoint(pos):
                        current_brush_key = k
                        current_size      = BRUSH_SIZES[k]
                        break

            # Click on canvas
            elif in_canvas(pos):
                tool_obj.on_mouse_down(canvas, canvas_mouse, current_color, current_size)

        # ── Mouse up ──────────────────────────────────────────────────────────
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            if in_canvas(event.pos):
                tool_obj.on_mouse_up(canvas, canvas_pos(event.pos), current_color, current_size)

        # ── Mouse move ────────────────────────────────────────────────────────
        elif event.type == MOUSEMOTION:
            if in_canvas(mouse_pos):
                tool_obj.on_mouse_move(canvas, canvas_mouse, current_color, current_size, mouse_btns)

    # ── Render ────────────────────────────────────────────────────────────────

    # Toolbar background
    draw_toolbar(screen)

    # Canvas (blit to screen below toolbar)
    screen.blit(canvas, (0, TOOLBAR_H))

    # Preview overlay: draw a temporary surface so shapes show while dragging
    if in_canvas(mouse_pos):
        preview = canvas.copy()
        tool_obj.draw_preview(preview, canvas_mouse, current_color, current_size)
        screen.blit(preview, (0, TOOLBAR_H))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()