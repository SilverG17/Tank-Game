import pygame
import os
import random

from states.base_state import BaseState
from states.versus_state import VersusState
from states.campaign_state import CampaignState
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
                    self.game.selected_map_index +=1
                    if self.game.selected_map_index >= total_maps:
                        self.game.selected_map_index = 0

                elif event.key == pygame.K_UP:
                    self.game.mode_index -= 1
                    if self.game.mode_index < 0:
                        self.game.mode_index = len(self.game.modes) - 1

                elif event.key == pygame.K_DOWN:
                    self.game.mode_index += 1
                    if self.game.mode_index >= len(self.game.modes):
                        self.game.mode_index = 0

                elif event.key == pygame.K_SPACE:
                    # CHANGE STATE BASED ON MODE
                    self.game.mode = self.game.modes[self.game.mode_index]

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
            "TANK BATTLE", True, COLORS.GOLD
        )
        surface.blit(title, (width // 2 - title.get_width() // 2, 40))

        # ==========================
        # START TEXT
        # ==========================
        subtitle = self.subtitle_font.render(
            "PRESS SPACE TO START",
            True,
            COLORS.WHITE
        )
        surface.blit(subtitle, (width // 2 - subtitle.get_width() // 2, 540))

        # ==========================
        # MODE TEXT
        # ==========================
        mode_text = self.subtitle_font.render(
            f"MODE: {self.game.modes[self.game.mode_index]}",
            True,
            COLORS.RED
        )
        surface.blit(mode_text, (width // 2 - mode_text.get_width() // 2, 150))

        mode_hint = self.game.font_small.render(
            "UP / DOWN to change mode",
            True,
            COLORS.GRAY
        )
        surface.blit(mode_hint, (width // 2 - mode_hint.get_width() // 2, 190))

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
            COLORS.BLUE
        )
        surface.blit(map_text, (width // 2 - map_text.get_width() // 2, 210))

        map_hint = self.game.font_small.render(
            "LEFT / RIGHT to change map",
            True,
            COLORS.GRAY
        )
        surface.blit(map_hint, (width // 2 - map_hint.get_width() // 2, 250))

        # ==========================
        # MAP PREVIEW 
        # ==========================
        if self.game.selected_map_index == 0:
            preview = self.game.RANDOM_PREVIEW
        else:
            preview = self.game.map_previews[self.game.selected_map_index - 1]
        if preview:
            surface.blit(preview, (width // 2 - preview.get_width() // 2, 280))

        # ==========================
        # CONFIG TEXT
        # ==========================
        config_text = self.game.font_small.render(
            "PRESS C TO CONFIGURE CONTROLS",
            True,
            COLORS.CYAN
        )
        surface.blit(config_text, (width // 2 - config_text.get_width() // 2, 590))
        surface.blit(self.CONFIG_IMG, self.config_rect)