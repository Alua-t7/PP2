import pygame
import datetime
import math

class MickeyClock:
    def __init__(self, screen, hand_image_path):
        self.screen = screen
        self.hand_img = pygame.image.load(hand_image_path).convert_alpha()
        hand_width = 80   
        hand_height = 200  
        self.hand_img = pygame.transform.scale(self.hand_img, (hand_width, hand_height))
        self.center = (screen.get_width() // 2, screen.get_height() // 2)

    def get_time(self):
        now = datetime.datetime.now()
        return now.minute, now.second

    def draw_hand(self, image, angle, offset=(0, 0)):
        """Rotate hand around its wrist (bottom center), then place at clock center."""
        cx, cy = self.center
        cx += offset[0]
        cy += offset[1]

        # Rotate the image
        rotated = pygame.transform.rotate(image, angle)

        # The wrist is at the bottom center of the ORIGINAL image
        # After rotation, we need to offset so wrist lands on center
        orig_w, orig_h = image.get_size()
        rot_w, rot_h = rotated.get_size()

        # Vector from image center to wrist (bottom center) in original image
        wrist_offset_x = 0
        wrist_offset_y = orig_h / 2  # wrist is at bottom

        # Rotate that vector by the same angle
        angle_rad = math.radians(-angle)
        rotated_ox = wrist_offset_x * math.cos(angle_rad) - wrist_offset_y * math.sin(angle_rad)
        rotated_oy = wrist_offset_x * math.sin(angle_rad) + wrist_offset_y * math.cos(angle_rad)

        # Place so the wrist lands exactly on (cx, cy)
        blit_x = cx - rot_w / 2 - rotated_ox
        blit_y = cy - rot_h / 2 - rotated_oy

        self.screen.blit(rotated, (blit_x, blit_y))

    def draw(self):
        self.draw_clock_face()
        self.draw_numbers()
        minutes, seconds = self.get_time()

        min_angle = -(minutes / 60 * 360)
        sec_angle = -(seconds / 60 * 360)

        sec_hand = self.hand_img.copy()

        # Both hands share the same wrist point = clock center
        self.draw_hand(self.hand_img, min_angle, offset=(0, 0))  # minutes
        self.draw_hand(sec_hand,      sec_angle, offset=(0, 0))  # seconds

    def draw_clock_face(self):
        cx, cy = self.center
        radius = 220

        # Outer circle (clock border)
        pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), radius, 6)

        # Hour markers (12 thick lines)
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            outer_x = int(cx + radius * math.cos(angle))
            outer_y = int(cy + radius * math.sin(angle))
            inner_x = int(cx + (radius - 20) * math.cos(angle))
            inner_y = int(cy + (radius - 20) * math.sin(angle))
            pygame.draw.line(self.screen, (255, 255, 255), (inner_x, inner_y), (outer_x, outer_y), 4)

        # Minute markers (60 thin lines)
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            outer_x = int(cx + radius * math.cos(angle))
            outer_y = int(cy + radius * math.sin(angle))
            inner_x = int(cx + (radius - 10) * math.cos(angle))
            inner_y = int(cy + (radius - 10) * math.sin(angle))
            pygame.draw.line(self.screen, (180, 180, 180), (inner_x, inner_y), (outer_x, outer_y), 1)

        # Center dot
        pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 8)

    def draw_numbers(self):
        cx, cy = self.center
        radius = 180  # slightly inside the tick marks
        font = pygame.font.SysFont("Arial", 36, bold=True)

        for i in range(1, 13):
            angle = math.radians(i * 30 - 90)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            text = font.render(str(i), True, (255, 255, 255))
            rect = text.get_rect(center=(x, y))
            self.screen.blit(text, rect)