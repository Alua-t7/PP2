import pygame
import datetime
import math
import numpy as np


class MickeyClock:
    def __init__(self, screen, minute_hand_path, second_hand_path, background_path):
        self.screen = screen
        self.w, self.h = screen.get_size()
        self.center = (self.w // 2, self.h // 2)

        # In __init__, replace background loading with this:
        bg = pygame.image.load(background_path).convert_alpha()
        bg_w, bg_h = bg.get_size()
        # Keep original aspect ratio
        scale = min(self.w / bg_w, self.h / bg_h)
        new_w = int(bg_w * scale)
        new_h = int(bg_h * scale)
        self.background = pygame.transform.scale(bg, (new_w, new_h))
        # Center position for background
        self.bg_pos = ((self.w - new_w) // 2, (self.h - new_h) // 2)
        # Update center to match clock face center
        self.center = (self.w // 2, self.h // 2)

        # Load hands and scale them
        self.minute_img = self._load_hand("images/minute_hand.png", 220)
        self.second_img = self._load_hand("images/second_hand.png", 220)

        # Correction angles — tweak if hands don't point to 12
        self.minute_correction = 0
        self.second_correction = 0

    def _load_hand(self, path, max_size):
        img = pygame.image.load(path).convert_alpha()
        w, h = img.get_size()
        # Keep aspect ratio
        scale = max_size / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return pygame.transform.scale(img, (new_w, new_h))

    def get_time(self):
        now = datetime.datetime.now()
        return now.minute, now.second

    def draw_hand(self, image, angle, correction):
        cx, cy = self.center
        total_angle = angle + correction
        rotated = pygame.transform.rotate(image, total_angle)
        rot_w, rot_h = rotated.get_size()
        # Stick end is at canvas center = rotation center
        blit_x = cx - rot_w / 2
        blit_y = cy - rot_h / 2
        self.screen.blit(rotated, (blit_x, blit_y))
        

        self.screen.blit(rotated, (blit_x, blit_y))

    def draw(self):
        self.screen.fill((255, 255, 255))  # white background
        self.screen.blit(self.background, self.bg_pos)  # ← use bg_pos

        minutes, seconds = self.get_time()
        min_angle = -(minutes / 60 * 360)
        sec_angle = -(seconds / 60 * 360)

        # Draw hands
        self.draw_hand(self.minute_img, min_angle, self.minute_correction)
        self.draw_hand(self.second_img, sec_angle, self.second_correction)

        # Center dot
        pygame.draw.circle(self.screen, (0, 0, 0), self.center, 10)