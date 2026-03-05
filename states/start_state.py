import pygame
import os
import random

from states.base_state import BaseState
from states.playing_state import PlayingState
from states.select_state import SelectState
from systems.tile_map import TileMap 
from constants import COLORS

class StartState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.MAIN_BG = game.MAIN_BG
        self.MAIN_BG = pygame.transform.scale(
            game.MAIN_BG,
            (game.screen.get_width(), game.screen.get_height())
        )
        self.CONFIG_IMG = game.CONFIG_IMG
        self.title_font = game.font_title
        self.subtitle_font = game.font_big
        self.config_font = game.font_big
        self.game.selected_map_index = 0 
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
            total_maps = len(self.game.map_files) + 1

            # ========================
            # KEYBOARD
            # ========================
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.game.selected_map_index -= 1
                    if self.game.selected_map_index < 0:
                        self.game.selected_map_index = total_maps - 1
                elif event.key == pygame.K_RIGHT:
                    self.game.selected_map_index += 1
                    if self.game.selected_map_index >= total_maps:
                        self.game.selected_map_index = 0
                elif event.key == pygame.K_SPACE:
                    if self.game.selected_map_index == 0:
                        selected_path = random.choice(self.game.map_files)
                    else:
                        selected_path = self.game.map_files[self.game.selected_map_index - 1]
                    self.game.level_map = self.game.load_map(selected_path)
                    self.game.tile_map = TileMap(self.game)
                    self.game.change_state(SelectState(self.game))
                elif event.key == pygame.K_c:
                    from states.Config_state import ConfigState
                    self.game.change_state(ConfigState(self.game))

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
        surface.blit(self.MAIN_BG, (0, 0))
        width = surface.get_width()
        height = surface.get_height()

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        title = self.title_font.render(
            "TANK BATTLE", True, COLORS.YELLOW
        )

        surface.blit(
            title,
            (width // 2 - title.get_width() // 2,
            60)
        )

        # ==========================
        # START TEXT
        # ==========================
        subtitle = self.subtitle_font.render(
            "PRESS SPACE TO START",
            True,
            COLORS.WHITE
        )

        surface.blit(
            subtitle,
            (width // 2 - subtitle.get_width() // 2,
            500)
        )

        # ==========================
        # CONFIG TEXT
        # ==========================
        config_text = self.game.font_small.render(
            "PRESS C TO CONFIGURE CONTROLS",
            True,
            COLORS.CYAN
        )

        surface.blit(
            config_text,
            (width // 2 - config_text.get_width() // 2, 540)
        )

        # ==========================
        # MAP PREVIEW 
        # ==========================
        if self.game.selected_map_index == 0:
            preview = self.game.RANDOM_PREVIEW
        else:
            preview = self.game.map_previews[self.game.selected_map_index - 1]
        if preview:
            surface.blit(
                preview,
                (width // 2 - preview.get_width() // 2,
                230)
            )

        # ==========================
        # MAP NAME
        # ==========================
        if self.game.selected_map_index == 0:
            map_name = "RANDOM"
        else:
            current_file = self.game.map_files[self.game.selected_map_index - 1]
            map_name = os.path.basename(current_file).replace(".txt", "")
        map_text = self.subtitle_font.render(
            f"MAP: {map_name}",
            True,
            COLORS.CYAN
        )

        surface.blit(
            map_text,
            (width // 2 - map_text.get_width() // 2,
            180)
        )

        surface.blit(self.CONFIG_IMG, self.config_rect)