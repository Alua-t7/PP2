class Ball:
    def __init__(self, screen_width, screen_height):
        self.radius = 25
        self.speed  = 20
        self.color  = (220, 30, 60)   # vivid red
        self.x = screen_width  // 2   # start at center
        self.y = screen_height // 2

        self.sw = screen_width
        self.sh = screen_height

    def move(self, direction):
        """Try to move. Ignore if it would go off-screen."""
        new_x, new_y = self.x, self.y

        if direction == "UP":
            new_y -= self.speed
        elif direction == "DOWN":
            new_y += self.speed
        elif direction == "LEFT":
            new_x -= self.speed
        elif direction == "RIGHT":
            new_x += self.speed

        # Only apply if within bounds
        if self.radius <= new_x <= self.sw - self.radius:
            self.x = new_x
        if self.radius <= new_y <= self.sh - self.radius:
            self.y = new_y

    def draw(self, screen):
        import pygame
        # Shadow for depth
        pygame.draw.circle(screen, (180, 180, 180), (self.x + 4, self.y + 4), self.radius)
        # Main ball
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Shine highlight
        pygame.draw.circle(screen, (255, 120, 140), (self.x - 8, self.y - 8), 8)