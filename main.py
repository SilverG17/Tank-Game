import pygame
import sys

from constants import WIDTH, HEIGHT, FPS
from game import Game   

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tank Battle")
    clock = pygame.time.Clock()
    game = Game(screen)
    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        # ===== LẤY EVENTS =====
        events = pygame.event.get()

        # ===== XỬ LÝ EVENTS CHO STATE =====
        game.state.handle_events(events)

        # ===== UPDATE INPUT SYSTEM =====
        game.input.update()
        if game.input.quit_requested:
            running = False
        game.update(dt)
        game.draw()
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()