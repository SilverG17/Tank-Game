import pygame
from states.base_state import BaseState
from constants import Color

class GameOverState(BaseState):
    def __init__(self, game):
        super().__init__(game)

    # ==========================================
    # EVENTS
    # ==========================================
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    from states.playing_state import PlayingState
                    self.game.change_state(PlayingState(self.game))

                if event.key == pygame.K_ESCAPE:
                    from states.start_state import StartState
                    self.game.change_state(StartState(self.game))

    # ==========================================
    # UPDATE
    # ==========================================
    def update(self, dt):
        pass

    # ==========================================
    # DRAW
    # ==========================================
    def draw(self, surface):
        surface.fill((20, 20, 20))

        width = surface.get_width()
        height = surface.get_height()

        winner_text = f"{self.game.winner} IS THE VICTOR"

        title = self.game.font_title.render(
            winner_text,
            True,
            (255, 215, 0) 
        )

        retry = self.game.font_big.render(
            "Press R to Restart", True, Color.WHITE
        )

        menu = self.game.font_big.render(
            "Press ESC to exit to Menu", True, Color.GRAY
        )

        surface.blit(
            title,
            (width // 2 - title.get_width() // 2,
            height // 3)
        )

        surface.blit(
            retry,
            (width // 2 - retry.get_width() // 2,
            height // 2)
        )

        surface.blit(
            menu,
            (width // 2 - menu.get_width() // 2,
            height // 2 + 80)
        )