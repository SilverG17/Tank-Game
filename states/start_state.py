import pygame
import os

from states.base_state import BaseState
from states.playing_state import PlayingState
from systems.tile_map import TileMap 
from constants import Color

class StartState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.CONFIG_IMG = game.CONFIG_IMG
        self.title_font = game.font_title
        self.subtitle_font = game.font_big
        width = game.screen.get_width()
        height = game.screen.get_height()
        self.config_rect = self.CONFIG_IMG.get_rect(
            midbottom=(width // 2, height - 30)
        )

    # ==========================
    # EVENTS
    # ==========================
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # ========================
            # KEYBOARD
            # ========================
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.game.selected_map_index -= 1
                    if self.game.selected_map_index < 0:
                        self.game.selected_map_index = len(self.game.map_files) - 1
                elif event.key == pygame.K_RIGHT:
                    self.game.selected_map_index += 1
                    if self.game.selected_map_index >= len(self.game.map_files):
                        self.game.selected_map_index = 0
                elif event.key == pygame.K_SPACE:
                    selected_path = self.game.map_files[self.game.selected_map_index]
                    self.game.level_map = self.game.load_map(selected_path)
                    self.game.tile_map = TileMap(self.game)
                    self.game.change_state(PlayingState(self.game))

            # ========================
            # MOUSE
            # ========================
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    from states.Config_state import ConfigState
                    if self.config_rect.collidepoint(event.pos):
                        self.game.change_state(ConfigState(self.game))

    # ==========================
    # UPDATE
    # ==========================
    def update(self, dt):
        pass

    # ==========================
    # DRAW
    # ==========================
    def draw(self, surface):
        surface.fill((30, 50, 30))

        width = surface.get_width()
        height = surface.get_height()

        title = self.title_font.render(
            "TANK BATTLE", True, Color.YELLOW
        )

        surface.blit(
            title,
            (width // 2 - title.get_width() // 2,
            60)
        )

        # ==========================
        # START TEXT (xuống dưới preview 1 chút)
        # ==========================
        subtitle = self.subtitle_font.render(
            "PRESS SPACE TO START",
            True,
            Color.WHITE
        )

        surface.blit(
            subtitle,
            (width // 2 - subtitle.get_width() // 2,
            500)
        )

        # ==========================
        # MAP PREVIEW 
        # ==========================
        preview = self.game.map_previews[self.game.selected_map_index]
        if preview:
            surface.blit(
                preview,
                (width // 2 - preview.get_width() // 2,
                230)
            )

        # ==========================
        # MAP NAME
        # ==========================
        current_file = self.game.map_files[self.game.selected_map_index]
        map_name = os.path.basename(current_file).replace(".txt", "")
        map_text = self.subtitle_font.render(
            f"MAP: {map_name}",
            True,
            Color.CYAN
        )

        surface.blit(
            map_text,
            (width // 2 - map_text.get_width() // 2,
            180)
        )

        surface.blit(self.CONFIG_IMG, self.config_rect)