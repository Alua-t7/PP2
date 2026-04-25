"""
tools.py — Drawing tool implementations for the Paint application.
Covers all tools from Practice 10, 11, and the new extended features.
"""

import pygame
import collections
from pygame.locals import *

# ── Brush sizes ────────────────────────────────────────────────────────────────
BRUSH_SIZES = {1: 2, 2: 5, 3: 10}   # key = shortcut, value = px thickness


# ══════════════════════════════════════════════════════════════════════════════
# Pencil (freehand)
# ══════════════════════════════════════════════════════════════════════════════
class PencilTool:
    def __init__(self):
        self.last_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        pygame.draw.circle(canvas, color, pos, size // 2)
        self.last_pos = pos

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        if buttons[0] and self.last_pos:
            pygame.draw.line(canvas, color, self.last_pos, pos, size)
        self.last_pos = pos

    def on_mouse_up(self, canvas, pos, color, size):
        self.last_pos = None

    def draw_preview(self, surface, pos, color, size):
        pygame.draw.circle(surface, color, pos, max(1, size // 2), 1)


# ══════════════════════════════════════════════════════════════════════════════
# Straight Line tool
# ══════════════════════════════════════════════════════════════════════════════
class LineTool:
    def __init__(self):
        self.start = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        pass  # preview handled externally

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            pygame.draw.line(canvas, color, self.start, pos, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            pygame.draw.line(surface, color, self.start, pos, size)


# ══════════════════════════════════════════════════════════════════════════════
# Rectangle tool (Practice 10 — now with brush size)
# ══════════════════════════════════════════════════════════════════════════════
class RectTool:
    def __init__(self):
        self.start = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            rect = pygame.Rect(
                min(self.start[0], pos[0]), min(self.start[1], pos[1]),
                abs(pos[0] - self.start[0]), abs(pos[1] - self.start[1])
            )
            pygame.draw.rect(canvas, color, rect, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            rect = pygame.Rect(
                min(self.start[0], pos[0]), min(self.start[1], pos[1]),
                abs(pos[0] - self.start[0]), abs(pos[1] - self.start[1])
            )
            pygame.draw.rect(surface, color, rect, size)


# ══════════════════════════════════════════════════════════════════════════════
# Circle tool (Practice 10)
# ══════════════════════════════════════════════════════════════════════════════
class CircleTool:
    def __init__(self):
        self.start = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        if self.start:
            dx = pos[0] - self.start[0]
            dy = pos[1] - self.start[1]
            radius = max(1, int((dx**2 + dy**2) ** 0.5))
            pygame.draw.circle(canvas, color, self.start, radius, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        if self.start:
            dx = pos[0] - self.start[0]
            dy = pos[1] - self.start[1]
            radius = max(1, int((dx**2 + dy**2) ** 0.5))
            pygame.draw.circle(surface, color, self.start, radius, size)


# ══════════════════════════════════════════════════════════════════════════════
# Eraser tool (Practice 10)
# ══════════════════════════════════════════════════════════════════════════════
class EraserTool:
    def __init__(self):
        self.last_pos = None

    def on_mouse_down(self, canvas, pos, color, size):
        pygame.draw.circle(canvas, (255, 255, 255), pos, size * 2)
        self.last_pos = pos

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        if buttons[0] and self.last_pos:
            pygame.draw.line(canvas, (255, 255, 255), self.last_pos, pos, size * 4)
            pygame.draw.circle(canvas, (255, 255, 255), pos, size * 2)
        self.last_pos = pos

    def on_mouse_up(self, canvas, pos, color, size):
        self.last_pos = None

    def draw_preview(self, surface, pos, color, size):
        pygame.draw.circle(surface, (200, 200, 200), pos, size * 2, 1)


# ══════════════════════════════════════════════════════════════════════════════
# Square tool (Practice 11)
# ══════════════════════════════════════════════════════════════════════════════
class SquareTool:
    def __init__(self):
        self.start = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        pass

    def _make_rect(self, pos):
        if not self.start:
            return None
        side = max(abs(pos[0] - self.start[0]), abs(pos[1] - self.start[1]))
        sx = self.start[0] + (side if pos[0] >= self.start[0] else -side)
        sy = self.start[1] + (side if pos[1] >= self.start[1] else -side)
        return pygame.Rect(
            min(self.start[0], sx), min(self.start[1], sy), side, side
        )

    def on_mouse_up(self, canvas, pos, color, size):
        rect = self._make_rect(pos)
        if rect:
            pygame.draw.rect(canvas, color, rect, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        rect = self._make_rect(pos)
        if rect:
            pygame.draw.rect(surface, color, rect, size)


# ══════════════════════════════════════════════════════════════════════════════
# Right Triangle tool (Practice 11)
# ══════════════════════════════════════════════════════════════════════════════
class RightTriangleTool:
    def __init__(self):
        self.start = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        pass

    def _points(self, pos):
        if not self.start:
            return None
        return [self.start, (pos[0], self.start[1]), (self.start[0], pos[1])]

    def on_mouse_up(self, canvas, pos, color, size):
        pts = self._points(pos)
        if pts:
            pygame.draw.polygon(canvas, color, pts, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        pts = self._points(pos)
        if pts:
            pygame.draw.polygon(surface, color, pts, size)


# ══════════════════════════════════════════════════════════════════════════════
# Equilateral Triangle tool (Practice 11)
# ══════════════════════════════════════════════════════════════════════════════
class EquilTriangleTool:
    def __init__(self):
        self.start = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        pass

    def _points(self, pos):
        if not self.start:
            return None
        import math
        dx = pos[0] - self.start[0]
        dy = pos[1] - self.start[1]
        side = (dx**2 + dy**2) ** 0.5
        if side < 1:
            return None
        angle = math.atan2(dy, dx)
        p1 = self.start
        p2 = (self.start[0] + side * math.cos(angle),
              self.start[1] + side * math.sin(angle))
        p3 = (self.start[0] + side * math.cos(angle - math.pi / 3),
              self.start[1] + side * math.sin(angle - math.pi / 3))
        return [(int(x), int(y)) for x, y in (p1, p2, p3)]

    def on_mouse_up(self, canvas, pos, color, size):
        pts = self._points(pos)
        if pts:
            pygame.draw.polygon(canvas, color, pts, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        pts = self._points(pos)
        if pts:
            pygame.draw.polygon(surface, color, pts, size)


# ══════════════════════════════════════════════════════════════════════════════
# Rhombus tool (Practice 11)
# ══════════════════════════════════════════════════════════════════════════════
class RhombusTool:
    def __init__(self):
        self.start = None

    def on_mouse_down(self, canvas, pos, color, size):
        self.start = pos

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        pass

    def _points(self, pos):
        if not self.start:
            return None
        cx = (self.start[0] + pos[0]) // 2
        cy = (self.start[1] + pos[1]) // 2
        return [
            (cx, self.start[1]),
            (pos[0], cy),
            (cx, pos[1]),
            (self.start[0], cy),
        ]

    def on_mouse_up(self, canvas, pos, color, size):
        pts = self._points(pos)
        if pts:
            pygame.draw.polygon(canvas, color, pts, size)
        self.start = None

    def draw_preview(self, surface, pos, color, size):
        pts = self._points(pos)
        if pts:
            pygame.draw.polygon(surface, color, pts, size)


# ══════════════════════════════════════════════════════════════════════════════
# Flood-Fill tool (BFS pixel fill)
# ══════════════════════════════════════════════════════════════════════════════
class FillTool:
    def on_mouse_down(self, canvas, pos, color, size):
        _flood_fill(canvas, pos, color)

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        pass

    def draw_preview(self, surface, pos, color, size):
        # Draw a small bucket icon hint
        pygame.draw.circle(surface, color, pos, 8, 2)


def _flood_fill(canvas, start_pos, fill_color):
    """BFS flood fill on a pygame Surface (exact color match)."""
    w, h = canvas.get_size()
    x0, y0 = int(start_pos[0]), int(start_pos[1])
    if not (0 <= x0 < w and 0 <= y0 < h):
        return

    target = canvas.get_at((x0, y0))[:3]
    fill   = fill_color[:3]
    if target == fill:
        return

    visited = set()
    queue   = collections.deque()
    queue.append((x0, y0))
    visited.add((x0, y0))

    while queue:
        x, y = queue.popleft()
        canvas.set_at((x, y), fill_color)
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if (0 <= nx < w and 0 <= ny < h
                    and (nx, ny) not in visited
                    and canvas.get_at((nx, ny))[:3] == target):
                visited.add((nx, ny))
                queue.append((nx, ny))


# ══════════════════════════════════════════════════════════════════════════════
# Text tool
# ══════════════════════════════════════════════════════════════════════════════
class TextTool:
    def __init__(self):
        self.active       = False
        self.pos          = None
        self.text         = ""
        self.font         = None   # built lazily after pygame.init()
        self.cursor_on    = True
        self.cursor_timer = 0

    def _get_font(self):
        if self.font is None:
            self.font = pygame.font.SysFont("Consolas", 22)
        return self.font

    def on_mouse_down(self, canvas, pos, color, size):
        self.active = True
        self.pos    = pos
        self.text   = ""

    def on_mouse_move(self, canvas, pos, color, size, buttons):
        pass

    def on_mouse_up(self, canvas, pos, color, size):
        pass

    def handle_key(self, canvas, event, color):
        if not self.active:
            return
        if event.key == K_RETURN:
            self._commit(canvas, color)
        elif event.key == K_ESCAPE:
            self.active = False
            self.text   = ""
        elif event.key == K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            char = event.unicode
            if char:
                self.text += char

    def _commit(self, canvas, color):
        if self.pos and self.text:
            surf = self._get_font().render(self.text, True, color)
            canvas.blit(surf, self.pos)
        self.active = False
        self.text   = ""

    def draw_preview(self, surface, pos, color, size):
        if not self.active or not self.pos:
            return
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_on    = not self.cursor_on
            self.cursor_timer = 0
        display = self.text + ("|" if self.cursor_on else " ")
        surf    = self._get_font().render(display, True, color)
        surface.blit(surf, self.pos)