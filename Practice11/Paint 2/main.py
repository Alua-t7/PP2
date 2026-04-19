# Paint App — Extended from Practice 10
import pygame
import sys
import math

# --- Initialize Pygame --------------------------------------------------------
pygame.init()


SCREEN_W  = 960
SCREEN_H  = 680

TOOLBAR_H = 64          # Pixel height of the top toolbar strip
CANVAS_Y  = TOOLBAR_H  # Canvas starts directly below the toolbar

# --- Tool identifiers ---------------------------------------------------------
TOOL_PEN       = "pen"
TOOL_RECT      = "rect"
TOOL_SQUARE    = "square"
TOOL_CIRCLE    = "circle"
TOOL_ERASER    = "eraser"
TOOL_RTRIANGLE = "right_triangle"
TOOL_ETRIANGLE = "equilateral_triangle"
TOOL_RHOMBUS   = "rhombus"

# --- UI Colors ----------------------------------------------------------------
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
LIGHT_GRAY = (210, 210, 210)
DARK_GRAY  = (80,  80,  80)
TOOLBAR_BG = (35,  35,  45)   # Dark toolbar background

# --- Drawing palette ----------------------------------------------------------
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

PALETTE_CELL = 30       # Size of each color swatch in the toolbar
PALETTE_X    = 10       # Where the palette row starts (left edge)


# =============================================================================
# GEOMETRY HELPERS
# =============================================================================

def square_points(start, end):
    x0, y0 = start
    x1, y1 = end
    # Use the smaller axis difference so the shape is always square
    side = min(abs(x1 - x0), abs(y1 - y0))
    # Preserve drag direction (negative side when dragging left/up)
    sx = side if x1 >= x0 else -side
    sy = side if y1 >= y0 else -side
    return [
        (x0,      y0),
        (x0 + sx, y0),
        (x0 + sx, y0 + sy),
        (x0,      y0 + sy),
    ]


def right_triangle_points(start, end):
    """
    Return the three vertices of a right-angle triangle.

    The right angle is at `start`.
    The two legs run horizontally to (end_x, start_y)
    and vertically to (start_x, end_y).
    """
    x0, y0 = start
    x1, y1 = end
    return [
        (x0, y0),   # right-angle corner
        (x1, y0),   # horizontal leg end
        (x0, y1),   # vertical leg end
    ]


def equilateral_triangle_points(start, end):
    """
    Return the three vertices of an equilateral triangle.

    The base runs horizontally, centered on `start`.
    Its width equals the horizontal drag distance.
    The apex rises above (or below) depending on drag direction.
    """
    x0, y0 = start
    x1, y1 = end
    half_base = (x1 - x0)                       # signed half-base length
    base_left  = (x0 - half_base, y0)
    base_right = (x1, y0)
    # Height of an equilateral triangle = side * sqrt(3) / 2
    # Here side = abs(x1 - x0) * 2  (full base)
    height = abs(half_base * 2) * math.sqrt(3) / 2
    # Apex goes in the opposite vertical direction of the drag
    apex_y = y0 - height if y1 <= y0 else y0 + height
    apex   = (x0, int(apex_y))
    return [base_left, base_right, apex]


def rhombus_points(start, end):
    """
    Return the four vertices of a rhombus (diamond shape).

    The center is at `start`.
    Half-width  = horizontal distance to `end`.
    Half-height = vertical   distance to `end`.
    """
    cx, cy = start
    x1, y1 = end
    hw = abs(x1 - cx)   # half-width
    hh = abs(y1 - cy)   # half-height
    return [
        (cx,      cy - hh),   # top
        (cx + hw, cy),        # right
        (cx,      cy + hh),   # bottom
        (cx - hw, cy),        # left
    ]


# =============================================================================
# TOOLBAR BUTTON
# =============================================================================

class ToolButton:
    """A clickable button in the toolbar that activates a drawing tool."""

    def __init__(self, label, tool, rect):
        self.label = label
        self.tool  = tool
        self.rect  = pygame.Rect(rect)

    def draw(self, surface, font, active_tool):
        """Render the button; highlight if it is the currently active tool."""
        is_active    = (self.tool == active_tool)
        bg_color     = (90, 110, 200) if is_active else (60, 60, 78)
        border_color = (180, 200, 255) if is_active else (100, 100, 120)

        pygame.draw.rect(surface, bg_color,     self.rect, border_radius=7)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=7)

        text = font.render(self.label, True, WHITE)
        tx   = self.rect.centerx - text.get_width()  // 2
        ty   = self.rect.centery - text.get_height() // 2
        surface.blit(text, (tx, ty))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# =============================================================================
# MAIN
# =============================================================================

def main():
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Paint")
    clock  = pygame.time.Clock()

    font       = pygame.font.SysFont("Verdana", 11, bold=True)
    font_tiny  = pygame.font.SysFont("Verdana", 10)

    # --- Canvas ---------------------------------------------------------------
    # Separate surface so toolbar is never accidentally drawn on
    canvas = pygame.Surface((SCREEN_W, SCREEN_H - TOOLBAR_H))
    canvas.fill(WHITE)

    # --- Tool buttons ---------------------------------------------------------
    # Two rows of buttons to fit all tools in the toolbar
    # Row 1: original tools
    # Row 2: new shape tools
    btn_h = 26   # button height
    btn_w = 68   # button width
    gap   = 4    # gap between buttons

    # Starting x position — placed after the color palette
    bx = PALETTE_X + len(PALETTE) * (PALETTE_CELL + 3) + 12

    # Row y positions within the toolbar
    row1_y = 4
    row2_y = row1_y + btn_h + gap

    buttons = [
        # --- Row 1: basic tools ---
        ToolButton("Pen",      TOOL_PEN,       (bx,                    row1_y, btn_w, btn_h)),
        ToolButton("Rect",     TOOL_RECT,      (bx + (btn_w+gap),      row1_y, btn_w, btn_h)),
        ToolButton("Circle",   TOOL_CIRCLE,    (bx + (btn_w+gap)*2,    row1_y, btn_w, btn_h)),
        ToolButton("Eraser",   TOOL_ERASER,    (bx + (btn_w+gap)*3,    row1_y, btn_w, btn_h)),
        # --- Row 2: new shape tools ---
        ToolButton("Square",   TOOL_SQUARE,    (bx,                    row2_y, btn_w, btn_h)),
        ToolButton("R.Tri",    TOOL_RTRIANGLE, (bx + (btn_w+gap),      row2_y, btn_w, btn_h)),
        ToolButton("Eq.Tri",   TOOL_ETRIANGLE, (bx + (btn_w+gap)*2,    row2_y, btn_w, btn_h)),
        ToolButton("Rhombus",  TOOL_RHOMBUS,   (bx + (btn_w+gap)*3,    row2_y, btn_w, btn_h)),
    ]

    # --- State ----------------------------------------------------------------
    current_tool = TOOL_PEN
    draw_color   = BLACK
    brush_radius = 8

    drawing   = False     # True while left mouse button is held
    start_pos = None      # Canvas-relative position where drag began
    prev_pos  = None      # Previous canvas-relative position (for pen continuity)

    # preview surface: shows the committed canvas + ghost shape while dragging
    preview = canvas.copy()

    # Shape tools that use drag-preview (not freehand)
    SHAPE_TOOLS = {TOOL_RECT, TOOL_SQUARE, TOOL_CIRCLE,
                   TOOL_RTRIANGLE, TOOL_ETRIANGLE, TOOL_RHOMBUS}

    # =========================================================================
    # DRAW SHAPE HELPER
    # Draws either to `canvas` (on commit) or `preview` (while dragging).
    # =========================================================================

    def draw_shape(surface, tool, start, end, color):
        """
        Draw the shape for `tool` from `start` to `end` on `surface`.
        All shapes are drawn as outlines (width=2) for a consistent look.
        """
        if tool == TOOL_RECT:
            # Standard rectangle — any aspect ratio
            x = min(start[0], end[0])
            y = min(start[1], end[1])
            w = abs(end[0] - start[0])
            h = abs(end[1] - start[1])
            if w > 0 and h > 0:
                pygame.draw.rect(surface, color, pygame.Rect(x, y, w, h), 2)

        elif tool == TOOL_SQUARE:
            # Perfect square — uses the shorter drag axis as side length
            pts = square_points(start, end)
            if pts:
                pygame.draw.polygon(surface, color, pts, 2)

        elif tool == TOOL_CIRCLE:
            # Circle — radius = distance from drag start to current mouse
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            r  = int(math.hypot(dx, dy))
            if r > 0:
                pygame.draw.circle(surface, color, start, r, 2)

        elif tool == TOOL_RTRIANGLE:
            # Right-angle triangle with the right angle at drag start
            pts = right_triangle_points(start, end)
            pygame.draw.polygon(surface, color, pts, 2)

        elif tool == TOOL_ETRIANGLE:
            # Equilateral triangle — base centered on drag start
            pts = equilateral_triangle_points(start, end)
            pygame.draw.polygon(surface, color, pts, 2)

        elif tool == TOOL_RHOMBUS:
            # Rhombus (diamond) centered on drag start
            pts = rhombus_points(start, end)
            pygame.draw.polygon(surface, color, pts, 2)

    # =========================================================================
    # GAME LOOP
    # =========================================================================
    while True:
        mouse_pos    = pygame.mouse.get_pos()
        # Translate screen coordinates to canvas coordinates
        canvas_mouse = (mouse_pos[0], mouse_pos[1] - CANVAS_Y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # --- Keyboard shortcuts -------------------------------------------
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                key_map = {
                    pygame.K_p: TOOL_PEN,
                    pygame.K_r: TOOL_RECT,
                    pygame.K_c: TOOL_CIRCLE,
                    pygame.K_e: TOOL_ERASER,
                    pygame.K_s: TOOL_SQUARE,
                    pygame.K_t: TOOL_RTRIANGLE,
                    pygame.K_q: TOOL_ETRIANGLE,
                    pygame.K_h: TOOL_RHOMBUS,
                }
                if event.key in key_map:
                    current_tool = key_map[event.key]

            # --- Mouse wheel: adjust brush size (Pen / Eraser only) ----------
            if event.type == pygame.MOUSEWHEEL:
                if current_tool in (TOOL_PEN, TOOL_ERASER):
                    brush_radius = max(1, min(80, brush_radius + event.y))

            # --- Mouse button DOWN --------------------------------------------
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                toolbar_clicked = False

                # Check tool buttons
                for btn in buttons:
                    if btn.is_clicked(mouse_pos):
                        current_tool    = btn.tool
                        toolbar_clicked = True
                        break

                # Check palette swatches
                if not toolbar_clicked:
                    for i, color in enumerate(PALETTE):
                        sx = PALETTE_X + i * (PALETTE_CELL + 3)
                        sy = (TOOLBAR_H - PALETTE_CELL) // 2
                        if pygame.Rect(sx, sy, PALETTE_CELL, PALETTE_CELL).collidepoint(mouse_pos):
                            draw_color      = color
                            toolbar_clicked = True
                            # Selecting a color while using eraser switches back to pen
                            if current_tool == TOOL_ERASER:
                                current_tool = TOOL_PEN
                            break

                # Start drawing on canvas
                if not toolbar_clicked and mouse_pos[1] >= CANVAS_Y:
                    drawing   = True
                    start_pos = canvas_mouse
                    prev_pos  = canvas_mouse

                    # Pen and eraser paint the first dot immediately on click
                    if current_tool == TOOL_PEN:
                        pygame.draw.circle(canvas, draw_color, canvas_mouse, brush_radius)
                    elif current_tool == TOOL_ERASER:
                        pygame.draw.circle(canvas, WHITE, canvas_mouse, brush_radius)

            # --- Mouse MOTION while holding left button -----------------------
            if event.type == pygame.MOUSEMOTION and drawing:
                if current_tool == TOOL_PEN:
                    # Connect previous and current positions for smooth strokes
                    if prev_pos:
                        pygame.draw.line(canvas, draw_color,
                                         prev_pos, canvas_mouse, brush_radius * 2)
                    pygame.draw.circle(canvas, draw_color, canvas_mouse, brush_radius)
                    prev_pos = canvas_mouse

                elif current_tool == TOOL_ERASER:
                    if prev_pos:
                        pygame.draw.line(canvas, WHITE,
                                         prev_pos, canvas_mouse, brush_radius * 2)
                    pygame.draw.circle(canvas, WHITE, canvas_mouse, brush_radius)
                    prev_pos = canvas_mouse
                # Shape tools show a live ghost preview — committed on mouse up

            # --- Mouse button UP — commit shape to canvas ---------------------
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
                drawing = False
                if current_tool in SHAPE_TOOLS and start_pos:
                    draw_shape(canvas, current_tool, start_pos, canvas_mouse, draw_color)
                start_pos = None
                prev_pos  = None

        # =====================================================================
        # RENDERING
        # =====================================================================

        # Start preview from the committed canvas
        preview.blit(canvas, (0, 0))

        # Overlay the ghost shape while dragging a shape tool
        if drawing and start_pos and current_tool in SHAPE_TOOLS and mouse_pos[1] >= CANVAS_Y:
            draw_shape(preview, current_tool, start_pos, canvas_mouse, draw_color)

        # Blit canvas onto screen below the toolbar
        screen.blit(preview, (0, CANVAS_Y))

        # --- Toolbar ----------------------------------------------------------
        pygame.draw.rect(screen, TOOLBAR_BG, (0, 0, SCREEN_W, TOOLBAR_H))
        pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_H), (SCREEN_W, TOOLBAR_H), 1)

        # Draw tool buttons
        for btn in buttons:
            btn.draw(screen, font, current_tool)

        # Draw color palette swatches
        for i, color in enumerate(PALETTE):
            sx   = PALETTE_X + i * (PALETTE_CELL + 3)
            sy   = (TOOLBAR_H - PALETTE_CELL) // 2
            rect = pygame.Rect(sx, sy, PALETTE_CELL, PALETTE_CELL)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            # Highlight the active color with a white border
            border = WHITE if color == draw_color else DARK_GRAY
            width  = 3     if color == draw_color else 1
            pygame.draw.rect(screen, border, rect, width, border_radius=5)

        # --- Brush size indicator (pen / eraser) ------------------------------
        if current_tool in (TOOL_PEN, TOOL_ERASER):
            ind_color = draw_color if current_tool == TOOL_PEN else LIGHT_GRAY
            ind_x = bx + (btn_w + gap) * 4 + 16
            ind_y = TOOLBAR_H // 2
            disp_r = min(brush_radius, 18)
            pygame.draw.circle(screen, ind_color, (ind_x, ind_y), disp_r)
            pygame.draw.circle(screen, DARK_GRAY,  (ind_x, ind_y), disp_r, 1)
            size_surf = font_tiny.render(f"{brush_radius}px", True, LIGHT_GRAY)
            screen.blit(size_surf, (ind_x + disp_r + 4,
                                    ind_y - size_surf.get_height() // 2))

        # --- Eraser cursor outline -------------------------------------------
        if current_tool == TOOL_ERASER and mouse_pos[1] >= CANVAS_Y:
            pygame.draw.circle(screen, DARK_GRAY, mouse_pos, brush_radius, 1)

        # --- Keyboard shortcut hint -------------------------------------------
        hint = font_tiny.render(
            "P=Pen  R=Rect  S=Square  C=Circle  T=R.Tri  Q=Eq.Tri  H=Rhombus  E=Eraser  scroll=size",
            True, (130, 130, 150))
        screen.blit(hint, (4, SCREEN_H - hint.get_height() - 3))

        pygame.display.flip()
        clock.tick(60)


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    main()