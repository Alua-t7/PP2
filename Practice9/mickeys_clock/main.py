import pygame
import sys
from clock import MickeyClock

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Mickey Mouse Clock")
    clock_obj = MickeyClock(screen, "images/mickey_hand.png")
    tick = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((15, 25, 50))  # dark background
        clock_obj.draw()
        pygame.display.flip()
        tick.tick(1)  # update every 1 second

if __name__ == "__main__":
    main()