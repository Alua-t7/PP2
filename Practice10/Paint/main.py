
import pygame
import math

SCREEN_W  = 900
SCREEN_H  = 650

TOOLBAR_H = 60          # Height of the top toolbar strip
CANVAS_Y  = TOOLBAR_H  # Canvas starts just below the toolbar

# Tools
TOOL_PEN     = "pen"
TOOL_RECT    = "rect"
TOOL_CIRCLE  = "circle"
TOOL_ERASER  = "eraser"

# Colors used in the UI
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
LIGHT_GRAY = (210, 210, 210)
DARK_GRAY  = (80,  80,  80)
TOOLBAR_BG = (45,  45,  55)   # Toolbar background

# Palette of selectable drawing colors
PALETTE = [
    (0,   0,   0),      # Black
    (255, 255, 255),    # White
    (220, 50,  50),     # Red
    (50,  180, 50),     # Green
    (50,  100, 220),    # Blue
    (255, 200, 0),      # Yellow
    (255, 130, 0),      # Orange
    (160, 50,  200),    # Purple
    (0,   200, 200),    # Cyan
    (200, 100, 60),     # Brown
    (255, 180, 200),    # Pink
    (100, 100, 100),    # Gray
]

PALETTE_CELL = 32      # Width/height of each color swatch in the toolbar
PALETTE_X    = 320     # Left edge of the palette row in the toolbar


def draw_rounded_rect(surface, color, rect, radius=6, width=0):
    pygame.draw.rect(surface, color, rect, width, border_radius=radius)


# TOOLBAR BUTTON CLASS

class ToolButton:
    """A clickable button in the toolbar representing a drawing tool."""

    def __init__(self, label, tool, rect):
        self.label = label    # Display text
        self.tool  = tool     # Tool identifier string
        self.rect  = pygame.Rect(rect)

    def draw(self, surface, font, active_tool):
        # Highlight the active tool
        bg_color     = (100, 120, 200) if self.tool == active_tool else (70, 70, 85)
        border_color = (180, 200, 255) if self.tool == active_tool else (110, 110, 130)

        draw_rounded_rect(surface, bg_color,     self.rect, radius=7)
        draw_rounded_rect(surface, border_color, self.rect, radius=7, width=2)

        label_surf = font.render(self.label, True, WHITE)
        lx = self.rect.centerx - label_surf.get_width()  // 2
        ly = self.rect.centery - label_surf.get_height() // 2
        surface.blit(label_surf, (lx, ly))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# =============================================================================
# MAIN
# =============================================================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Paint")
    clock  = pygame.time.Clock()

    # --- Fonts ----------------------------------------------------------------
    font       = pygame.font.SysFont("Verdana", 13, bold=True)
    font_small = pygame.font.SysFont("Verdana", 11)

    # --- Canvas ---------------------------------------------------------------
    # The canvas is a separate Surface so toolbar never gets drawn on.
    canvas = pygame.Surface((SCREEN_W, SCREEN_H - TOOLBAR_H))
    canvas.fill(WHITE)

    # --- Tool buttons ---------------------------------------------------------
    buttons = [
        ToolButton("Pen",    TOOL_PEN,    (10,  12, 68, 36)),
        ToolButton("Rect",   TOOL_RECT,   (85,  12, 68, 36)),
        ToolButton("Circle", TOOL_CIRCLE, (160, 12, 68, 36)),
        ToolButton("Eraser", TOOL_ERASER, (235, 12, 68, 36)),
    ]

    # --- State ----------------------------------------------------------------
    current_tool  = TOOL_PEN
    draw_color    = BLACK          # Active drawing color
    eraser_color  = WHITE          # Eraser always paints white (canvas background)
    brush_radius  = 8              # Radius for Pen and Eraser brush

    drawing       = False          # True while left mouse button is held
    start_pos     = None           # Mouse position when drag started (for shapes)
    prev_pos      = None           # Previous mouse position (for freehand pen)

    # A preview surface lets us show the ghost shape while dragging,
    # without permanently committing it to the canvas until mouse release.
    preview = canvas.copy()

    # =========================================================================
    # GAME LOOP
    # =========================================================================
    while True:
        mouse_pos = pygame.mouse.get_pos()

        # Adjust mouse_pos relative to the canvas (subtract toolbar height)
        canvas_mouse = (mouse_pos[0], mouse_pos[1] - CANVAS_Y)

        # --- Events -----------------------------------------------------------
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # Keyboard shortcuts -----------------------------------------------
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                # Tool shortcuts
                if event.key == pygame.K_p:
                    current_tool = TOOL_PEN
                if event.key == pygame.K_r:
                    current_tool = TOOL_RECT
                if event.key == pygame.K_c:
                    current_tool = TOOL_CIRCLE
                if event.key == pygame.K_e:
                    current_tool = TOOL_ERASER

            # Mouse wheel — adjust brush size for Pen / Eraser ----------------
            if event.type == pygame.MOUSEWHEEL:
                if current_tool in (TOOL_PEN, TOOL_ERASER):
                    brush_radius = max(1, min(80, brush_radius + event.y))

            # Mouse button DOWN ------------------------------------------------
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # Check if a toolbar button was clicked
                toolbar_clicked = False
                for btn in buttons:
                    if btn.is_clicked(mouse_pos):
                        current_tool    = btn.tool
                        toolbar_clicked = True
                        break

                # Check if a palette swatch was clicked
                if not toolbar_clicked:
                    for i, color in enumerate(PALETTE):
                        sx = PALETTE_X + i * (PALETTE_CELL + 4)
                        sy = (TOOLBAR_H - PALETTE_CELL) // 2
                        swatch_rect = pygame.Rect(sx, sy, PALETTE_CELL, PALETTE_CELL)
                        if swatch_rect.collidepoint(mouse_pos):
                            draw_color    = color
                            # Switching to a real color also deactivates eraser
                            if current_tool == TOOL_ERASER:
                                current_tool = TOOL_PEN
                            toolbar_clicked = True
                            break

                # Start drawing on the canvas
                if not toolbar_clicked and mouse_pos[1] >= CANVAS_Y:
                    drawing   = True
                    start_pos = canvas_mouse
                    prev_pos  = canvas_mouse

                    # Freehand pen/eraser: paint the very first dot immediately
                    if current_tool == TOOL_PEN:
                        pygame.draw.circle(canvas, draw_color, canvas_mouse, brush_radius)
                    elif current_tool == TOOL_ERASER:
                        pygame.draw.circle(canvas, eraser_color, canvas_mouse, brush_radius)

            # Mouse MOTION while holding left button ---------------------------
            if event.type == pygame.MOUSEMOTION and drawing:
                if current_tool == TOOL_PEN:
                    # Draw a filled circle at the current position AND
                    # connect it to the previous position with a thick line
                    # so there are no gaps when the mouse moves quickly.
                    if prev_pos:
                        pygame.draw.line(canvas, draw_color,
                                         prev_pos, canvas_mouse, brush_radius * 2)
                    pygame.draw.circle(canvas, draw_color, canvas_mouse, brush_radius)
                    prev_pos = canvas_mouse

                elif current_tool == TOOL_ERASER:
                    # Same continuous-line trick for the eraser
                    if prev_pos:
                        pygame.draw.line(canvas, eraser_color,
                                         prev_pos, canvas_mouse, brush_radius * 2)
                    pygame.draw.circle(canvas, eraser_color, canvas_mouse, brush_radius)
                    prev_pos = canvas_mouse

                # For RECT and CIRCLE we only show a live ghost preview —
                # the shape is not committed until mouse release.

            # Mouse button UP — commit shape to canvas -------------------------
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
                drawing = False

                if current_tool == TOOL_RECT and start_pos:
                    # Build the rect from drag start → current position
                    x = min(start_pos[0], canvas_mouse[0])
                    y = min(start_pos[1], canvas_mouse[1])
                    w = abs(canvas_mouse[0] - start_pos[0])
                    h = abs(canvas_mouse[1] - start_pos[1])
                    if w > 0 and h > 0:
                        pygame.draw.rect(canvas, draw_color, pygame.Rect(x, y, w, h), 2)

                elif current_tool == TOOL_CIRCLE and start_pos:
                    # Radius = distance from start to current mouse position
                    dx = canvas_mouse[0] - start_pos[0]
                    dy = canvas_mouse[1] - start_pos[1]
                    radius = int(math.hypot(dx, dy))
                    if radius > 0:
                        pygame.draw.circle(canvas, draw_color, start_pos, radius, 2)

                start_pos = None
                prev_pos  = None

        # =====================================================================
        # DRAW
        # =====================================================================

        # --- Build preview surface (canvas + ghost shape) -------------------
        preview.blit(canvas, (0, 0))   # Start with the committed canvas

        # Draw the ghost (preview) shape while dragging
        if drawing and start_pos and mouse_pos[1] >= CANVAS_Y:
            if current_tool == TOOL_RECT:
                x = min(start_pos[0], canvas_mouse[0])
                y = min(start_pos[1], canvas_mouse[1])
                w = abs(canvas_mouse[0] - start_pos[0])
                h = abs(canvas_mouse[1] - start_pos[1])
                if w > 0 and h > 0:
                    pygame.draw.rect(preview, draw_color, pygame.Rect(x, y, w, h), 2)

            elif current_tool == TOOL_CIRCLE:
                dx     = canvas_mouse[0] - start_pos[0]
                dy     = canvas_mouse[1] - start_pos[1]
                radius = int(math.hypot(dx, dy))
                if radius > 0:
                    pygame.draw.circle(preview, draw_color, start_pos, radius, 2)

        # --- Blit canvas onto screen -----------------------------------------
        screen.blit(preview, (0, CANVAS_Y))

        # --- Draw toolbar background -----------------------------------------
        pygame.draw.rect(screen, TOOLBAR_BG, (0, 0, SCREEN_W, TOOLBAR_H))
        # Thin separator line between toolbar and canvas
        pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_H), (SCREEN_W, TOOLBAR_H), 1)

        # --- Draw tool buttons -----------------------------------------------
        for btn in buttons:
            btn.draw(screen, font, current_tool)

        # --- Draw color palette ----------------------------------------------
        for i, color in enumerate(PALETTE):
            sx = PALETTE_X + i * (PALETTE_CELL + 4)
            sy = (TOOLBAR_H - PALETTE_CELL) // 2
            swatch_rect = pygame.Rect(sx, sy, PALETTE_CELL, PALETTE_CELL)

            # Fill the swatch
            pygame.draw.rect(screen, color, swatch_rect, border_radius=5)
            # White border around the selected color
            if color == draw_color:
                pygame.draw.rect(screen, WHITE, swatch_rect, 3, border_radius=5)
            else:
                pygame.draw.rect(screen, DARK_GRAY, swatch_rect, 1, border_radius=5)

        # --- Draw brush size indicator ----------------------------------------
        # Shows current brush radius as a small circle on the right of toolbar
        if current_tool in (TOOL_PEN, TOOL_ERASER):
            ind_x  = PALETTE_X + len(PALETTE) * (PALETTE_CELL + 4) + 20
            ind_y  = TOOLBAR_H // 2
            display_r = min(brush_radius, 20)   # Cap display so it fits toolbar
            pygame.draw.circle(screen, draw_color if current_tool == TOOL_PEN else LIGHT_GRAY,
                                (ind_x + 20, ind_y), display_r)
            pygame.draw.circle(screen, DARK_GRAY, (ind_x + 20, ind_y), display_r, 1)
            size_label = font_small.render(f"{brush_radius}px", True, LIGHT_GRAY)
            screen.blit(size_label, (ind_x + 44, ind_y - size_label.get_height() // 2))

        # --- Cursor: show eraser outline when eraser is active ---------------
        if current_tool == TOOL_ERASER and mouse_pos[1] >= CANVAS_Y:
            pygame.draw.circle(screen, DARK_GRAY, mouse_pos, brush_radius, 1)

        # --- Shortcut hint at bottom-right of toolbar ------------------------
        hint = font_small.render("P=Pen  R=Rect  C=Circle  E=Eraser  scroll=size", True, (140, 140, 160))
        screen.blit(hint, (SCREEN_W - hint.get_width() - 8, TOOLBAR_H - hint.get_height() - 4))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()