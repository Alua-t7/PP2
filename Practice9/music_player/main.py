import pygame
import sys
from player import MusicPlayer
from ui import PlayerUI

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Music Player")

    player = MusicPlayer("tracks")
    ui     = PlayerUI(screen)
    clock  = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.prev_track()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        ui.draw(player)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()