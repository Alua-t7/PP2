import pygame

# ── Colour palette ──────────────────────────────────────────
BLACK      = (0,   0,   0)
DARK       = (15,  10,  20)   # near-black background
PINK       = (255, 20,  147)  # hot pink accents
PINK_LIGHT = (255, 182, 213)  # soft pink for text
PINK_DIM   = (120, 20,  80)   # muted pink for inactive
WHITE      = (255, 255, 255)
GRAY       = (60,  50,  65)   # dark gray for bar bg

class PlayerUI:
    def __init__(self, screen):
        self.screen = screen
        self.w, self.h = screen.get_size()

        # Fonts
        self.font_title  = pygame.font.SysFont("Georgia",      42, bold=True)
        self.font_track  = pygame.font.SysFont("Georgia",      26, bold=True)
        self.font_status = pygame.font.SysFont("Courier New",  20, bold=True)
        self.font_time   = pygame.font.SysFont("Courier New",  18)
        self.font_key    = pygame.font.SysFont("Courier New",  20, bold=True)
        self.font_label  = pygame.font.SysFont("Georgia",      14)

    def draw(self, player):
        self._draw_background()
        self._draw_title()
        self._draw_track_info(player)
        self._draw_progress(player)
        self._draw_controls(player)

    # ── Background with subtle gradient feel ────────────────
    def _draw_background(self):
        self.screen.fill(DARK)
        # top pink glow strip
        glow = pygame.Surface((self.w, 4))
        glow.fill(PINK)
        self.screen.blit(glow, (0, 0))
        # bottom pink glow strip
        self.screen.blit(glow, (0, self.h - 4))

    # ── Title ───────────────────────────────────────────────
    def _draw_title(self):
        title = self.font_title.render("♪  MUSIC PLAYER  ♪", True, PINK)
        self.screen.blit(title, title.get_rect(center=(self.w // 2, 48)))

        # thin divider line
        pygame.draw.line(self.screen, PINK_DIM, (60, 78), (self.w - 60, 78), 1)

    # ── Track info ──────────────────────────────────────────
    def _draw_track_info(self, player):
        # Track name
        name = player.current_track_name()
        # Truncate if too long
        if len(name) > 32:
            name = name[:30] + "…"
        track = self.font_track.render(name, True, WHITE)
        self.screen.blit(track, track.get_rect(center=(self.w // 2, 115)))

        # Track counter  e.g.  [ 2 / 5 ]
        counter = self.font_status.render(
            f"[ {player.index + 1} / {len(player.tracks)} ]", True, PINK_LIGHT
        )
        self.screen.blit(counter, counter.get_rect(center=(self.w // 2, 150)))

        # Status badge
        if player.playing:
            badge_text  = "▶  PLAYING"
            badge_color = PINK
            bg_color    = (80, 0, 50)
        else:
            badge_text  = "⏹  STOPPED"
            badge_color = GRAY
            bg_color    = (30, 25, 35)

        badge_surf = self.font_status.render(badge_text, True, badge_color)
        badge_rect = badge_surf.get_rect(center=(self.w // 2, 185))
        # pill background
        pad = 14
        pill = pygame.Rect(
            badge_rect.x - pad, badge_rect.y - 6,
            badge_rect.w + pad * 2, badge_rect.h + 12
        )
        pygame.draw.rect(self.screen, bg_color, pill, border_radius=20)
        pygame.draw.rect(self.screen, badge_color, pill, 2, border_radius=20)
        self.screen.blit(badge_surf, badge_rect)

    # ── Progress bar ────────────────────────────────────────
    def _draw_progress(self, player):
        bar_x, bar_y = 60, 230
        bar_w, bar_h  = self.w - 120, 10

        # Background track
        pygame.draw.rect(self.screen, GRAY,
                         (bar_x, bar_y, bar_w, bar_h), border_radius=6)

        # Filled portion
        max_sec = 180
        elapsed = min(player.get_position_seconds(), max_sec)
        fill_w  = int((elapsed / max_sec) * bar_w)
        if fill_w > 0:
            pygame.draw.rect(self.screen, PINK,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=6)

            # Glowing dot at playhead
            dot_x = bar_x + fill_w
            pygame.draw.circle(self.screen, WHITE,  (dot_x, bar_y + bar_h // 2), 7)
            pygame.draw.circle(self.screen, PINK,   (dot_x, bar_y + bar_h // 2), 5)

        # Elapsed time
        secs  = int(player.get_position_seconds())
        label = self.font_time.render(
            f"{secs // 60}:{secs % 60:02d}", True, PINK_LIGHT
        )
        self.screen.blit(label, (bar_x, bar_y + 18))

    # ── Keyboard controls ───────────────────────────────────
    def _draw_controls(self, player):
        controls = [
            ("P", "Play"),
            ("S", "Stop"),
            ("N", "Next"),
            ("B", "Back"),
            ("Q", "Quit"),
        ]
        total_w   = self.w - 120
        gap       = total_w // len(controls)
        start_x   = 60
        y         = self.h - 95
        key_size  = 44

        for i, (key, label) in enumerate(controls):
            cx = start_x + i * gap + gap // 2

            # Highlight active key
            is_active = (
                (key == "P" and player.playing) or
                (key == "S" and not player.playing)
            )
            border_color = PINK  if is_active else PINK_DIM
            fill_color   = (80, 0, 50) if is_active else (25, 15, 30)

            # Key box
            box = pygame.Rect(cx - key_size // 2, y, key_size, key_size)
            pygame.draw.rect(self.screen, fill_color,   box, border_radius=10)
            pygame.draw.rect(self.screen, border_color, box, 2, border_radius=10)

            # Key letter
            k = self.font_key.render(key, True, WHITE)
            self.screen.blit(k, k.get_rect(center=box.center))

            # Label below
            l = self.font_label.render(label, True, PINK_LIGHT)
            self.screen.blit(l, l.get_rect(center=(cx, y + key_size + 14)))