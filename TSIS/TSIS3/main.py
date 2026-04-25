"""
main.py — Entry point for the extended Racer game.
Flow: Main Menu → Username → Game → Game Over → (retry / menu / leaderboard)
"""

import pygame
import sys
from pygame.locals import *

from persistence import load_settings, save_score
from ui          import (screen_main_menu, screen_username, screen_settings,
                          screen_leaderboard, screen_game_over)
from racer       import run_game, SW, SH

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Racer — Extended")
clock  = pygame.time.Clock()

# Load persisted settings once at startup
settings = load_settings()

# Player name — asked once per session
player_name = None

def main():
    global player_name, settings

    while True:
        action = screen_main_menu(screen, clock)

        if action == "quit":
            pygame.quit()
            sys.exit()

        elif action == "leaderboard":
            screen_leaderboard(screen, clock)

        elif action == "settings":
            settings = screen_settings(screen, clock, settings)

        elif action == "play":
            # Ask for name once (or if they haven't entered one yet)
            if player_name is None:
                player_name = screen_username(screen, clock)

            # Game loop — supports retry without re-entering name
            while True:
                score, distance, coins = run_game(screen, clock, settings, player_name)

                # Save to leaderboard
                save_score(player_name, score, distance, coins)

                # Game Over screen
                result = screen_game_over(screen, clock, score, distance, coins, player_name)

                if result == "retry":
                    continue          # play again immediately
                else:
                    break             # back to main menu


if __name__ == "__main__":
    main()