import pygame
from states.base_state import BaseState
from constants import COLORS

class GameOverState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        if self.game.mode == "CAMPAIGN" and self.game.winner == "PLAYER":
            pass
        else:
            self.game.audio.load_music(self.game.music_gameover, volume=0.3, loop=True)

        # Choose background
        if self.game.mode == "CAMPAIGN" and self.game.winner == "PLAYER":
            bg = game.VICTORY_BG
        else:
            bg = game.GAMEOVER_BG

        self.bg = pygame.transform.scale(
            bg,
            (game.screen.get_width(), game.screen.get_height())
        )

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
                    if self.game.mode == "VERSUS":
                        from states.versus_state import VersusState
                        next_state = VersusState(self.game)

                    elif self.game.mode == "CAMPAIGN":
                        from states.campaign_state import CampaignState
                        next_state = CampaignState(self.game)

                    elif self.game.mode == "COOP":
                        from states.coop_state import CoopState
                        next_state = CoopState(self.game)

                    self.game.audio.load_music(self.game.music_main, volume=0.2, loop=True)
                    self.game.change_state(next_state)

                if event.key == pygame.K_ESCAPE:
                    from states.start_state import StartState
                    self.game.audio.load_music(self.game.music_main, volume=0.2, loop=True)
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
        surface.blit(self.bg, (0, 0))
        width = surface.get_width()
        height = surface.get_height()

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        if self.game.mode == "CAMPAIGN":
            if self.game.winner == "PLAYER":
                winner_text = "YOU WIN"
            else:
                winner_text = "YOU LOSE TO A BOT"
        else:
            winner_text = f"{self.game.winner} IS THE VICTOR"

        title = self.game.font_title.render(
            winner_text,
            True,
            (255, 215, 0) 
        )

        retry = self.game.font_big.render(
            "Press R to Restart", True, COLORS.WHITE
        )

        menu = self.game.font_big.render(
            "Press ESC to exit to Menu", True, COLORS.GRAY
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