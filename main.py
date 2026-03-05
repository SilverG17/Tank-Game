import pygame
import sys

from constants import FPS
from game import Game

def main():
    pygame.init()

    game = Game(None)

    clock = pygame.time.Clock()

    while game.running:
        dt = clock.tick(FPS) / 1000

        events = pygame.event.get()
        game.state.handle_events(events)

        game.input.update()

        if game.input.quit_requested:
            game.running = False

        game.update(dt)
        game.draw()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()