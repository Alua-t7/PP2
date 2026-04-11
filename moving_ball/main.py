import pygame
import sys
from ball import Ball

WIDTH, HEIGHT = 600, 500

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Red Ball")

    ball  = Ball(WIDTH, HEIGHT)
    clock = pygame.time.Clock()

    font       = pygame.font.SysFont("Courier New", 18)
    font_title = pygame.font.SysFont("Georgia", 28, bold=True)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    ball.move("UP")
                elif event.key == pygame.K_DOWN:
                    ball.move("DOWN")
                elif event.key == pygame.K_LEFT:
                    ball.move("LEFT")
                elif event.key == pygame.K_RIGHT:
                    ball.move("RIGHT")
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        # Background
        screen.fill((255, 255, 255))

        # Title
        title = font_title.render("Move the Ball!", True, (40, 40, 40))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 30)))

        # Position display
        pos = font.render(f"x: {ball.x}   y: {ball.y}", True, (150, 150, 150))
        screen.blit(pos, (10, HEIGHT - 30))

        # Controls hint
        hint = font.render("Arrow keys to move  |  Q to quit", True, (200, 200, 200))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 18)))

        ball.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()