import pygame
from states.base_state import BaseState
from states.campaign_state import CampaignState
from constants import COLORS


class CutsceneState(BaseState):

    def __init__(self, game):
        super().__init__(game)
        self.game.audio.stop_music()
        self.game.audio.play_sfx("cutscene.mp3")

        self.lines = [
            "Year 2045...",
            "Everything was peaceful.",
            "",
            "Until someone pressed the wrong button.",
            "",
            "Now tanks are everywhere.",
            "Nobody knows why.",
            "",
            "Scientists say:",
            "'We may have messed up.'",
            "",
            "The government looked for a hero.",
            "They found you.",
            "",
            "You have:",
            "- One tank",
            "- Questionable driving skills",
            "- Zero backup",
            "",
            "Good luck.",
            "You're gonna need it.",
            "",
            "Press SPACE to start the disaster."
        ]

        # Start below the screen
        self.scroll_y = game.screen.get_height()

        # Speed of crawl
        self.scroll_speed = 50   # pixels/sec

        # spacing between lines
        self.line_spacing = 50

    # =========================
    # INPUT
    # =========================
    def handle_events(self, events):

        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                # allow skipping
                if event.key == pygame.K_SPACE:
                    self.game.audio.stop_sfx("cutscene.mp3")
                    self.game.audio.load_music("bg_music.mp3")
                    self.game.change_state(CampaignState(self.game))

    # =========================
    # UPDATE
    # =========================
    def update(self, dt):

        # move text upward
        self.scroll_y -= self.scroll_speed * dt

        # when text finished scrolling → auto start mission
        end_y = -len(self.lines) * self.line_spacing

        if self.scroll_y < end_y:
            self.game.audio.stop_sfx("cutscene.mp3")
            self.game.audio.load_music("bg_music.mp3")
            self.game.change_state(CampaignState(self.game))

    # =========================
    # DRAW
    # =========================
    def draw(self, surface):

        surface.fill((0, 0, 0))

        width = surface.get_width()

        for i, line in enumerate(self.lines):

            text = self.game.font_big.render(line, True, COLORS.WHITE)

            y = self.scroll_y + i * self.line_spacing

            surface.blit(
                text,
                (width // 2 - text.get_width() // 2, y)
            )