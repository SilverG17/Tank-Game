import pygame

from states.base_state import BaseState
from constants import COLORS
from states.start_state import StartState
from UI.menu_drawer import MenuDrawer

class ConfigState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = game.font_big
        self.option_font = game.font_small
        self.options = [
            "RESOLUTION",
            "FULLSCREEN",
            "MUSIC VOLUME",
            "SFX VOLUME",
            "PLAYER 1 CONTROLS",
            "PLAYER 2 CONTROLS",
            "TOGGLE MUTE",
            "BACK"
        ]
        self.resolutions = [
            (854, 480),
            (1024, 576),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080)
        ]
        current = self.game.config.get_resolution()
        self.res_index = self.resolutions.index(current) if current in self.resolutions else 1
        self.hold_delay = 0.15
        self.hold_timer = self.hold_delay
        self.selected = 0
        self.waiting_for_key = False
        self.waiting_player = None
        self.waiting_action = None
        self.control_mode = False
        self.control_player = None
        self.control_selected = 0
        self.actions = ["up", "down", "left", "right", "gun_left", "gun_right", "fire"]

    # ==========================
    # EVENTS
    # ==========================
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:

                # ===== CONTROL MODE =====
                if self.control_mode:
                    if self.waiting_for_key:
                        new_key = event.key
                        player_key = f"player{self.control_player}"
                        action = self.actions[self.control_selected]
                        current = self.game.config.data["controls"][player_key].get(action)

                        if isinstance(current, list):
                            if new_key not in current:
                                current.append(new_key)
                        elif isinstance(current, int):
                            if new_key != current:
                                self.game.config.data["controls"][player_key][action] = [current, new_key]
                        else:
                            self.game.config.data["controls"][player_key][action] = [new_key]
                        self.game.config.save_config()
                        self.waiting_for_key = False
                        return
                    if event.key == pygame.K_ESCAPE:
                        self.control_mode = False
                        return
                    if event.key == pygame.K_UP:
                        self.control_selected = (self.control_selected - 1) % len(self.actions)
                    if event.key == pygame.K_DOWN:
                        self.control_selected = (self.control_selected + 1) % len(self.actions)
                    if event.key == pygame.K_RETURN:
                        self.waiting_for_key = True
                    if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                        player_key = f"player{self.control_player}"
                        action = self.actions[self.control_selected]
                        current = self.game.config.data["controls"][player_key].get(action)
                        if isinstance(current, list) and current:
                            current.pop()  # xóa key cuối
                        elif isinstance(current, int):
                            self.game.config.data["controls"][player_key][action] = []
                        self.game.config.save_config()
                        return
                    return

                # ===== NORMAL MENU =====
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state(StartState(self.game))

                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)

                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)

                if event.key == pygame.K_RETURN:
                    self.activate_option()

    def change_resolution(self, direction):
        self.res_index = (self.res_index + direction) % len(self.resolutions)
        w, h = self.resolutions[self.res_index]

        self.game.config.set_resolution(w, h)
        self.game.create_window()

    def enter_control_menu(self, player):
        self.control_mode = True
        self.control_player = player
        self.control_selected = 0

    # ==========================
    # OPTION LOGIC
    # ==========================
    def activate_option(self):
        if self.options[self.selected] == "BACK":
            self.game.change_state(StartState(self.game))
        elif self.options[self.selected] == "TOGGLE MUTE":
            current = self.game.config.data["audio"].get("master_mute", False)
            self.game.config.data["audio"]["master_mute"] = not current
            self.game.config.save_config()
            if current:
                pygame.mixer.music.set_volume(
                    self.game.config.get_music_volume()
                )
            else:
                pygame.mixer.music.set_volume(0)

        elif self.options[self.selected] == "PLAYER 1 CONTROLS":
            self.enter_control_menu(1)

        elif self.options[self.selected] == "PLAYER 2 CONTROLS":
            self.enter_control_menu(2)

        elif self.options[self.selected] == "FULLSCREEN":
            self.game.config.toggle_fullscreen()
            self.game.create_window()

        elif self.options[self.selected] == "RESOLUTION":
            self.res_index = (self.res_index + 1) % len(self.resolutions)
            w, h = self.resolutions[self.res_index]

            self.game.config.set_resolution(w, h)
            self.game.create_window()

    # ==========================
    # DRAW
    # ==========================
    def draw(self, surface):
        if self.control_mode:
            MenuDrawer.draw_control_menu(surface, self.game, self)
        else:
            MenuDrawer.draw_settings(surface, self.game, self)

    def draw_bar(self, surface, value, y):
        width = surface.get_width()

        bar_width = 220
        bar_height = 14

        x = width // 2 + 80

        # background
        pygame.draw.rect(surface, (70, 70, 70), (x, y, bar_width, bar_height))

        # filled
        pygame.draw.rect(
            surface,
            COLORS.GREEN,
            (x, y, int(bar_width * value), bar_height)
        )

        # border
        pygame.draw.rect(surface, COLORS.WHITE, (x, y, bar_width, bar_height), 2)
        
    def draw_control_menu(self, surface):
        MenuDrawer.draw_background(surface)
        width = surface.get_width()

        # ======================
        # TITLE
        # ======================
        title = self.title_font.render(
            f"PLAYER {self.control_player} CONTROLS",
            True,
            COLORS.YELLOW
        )

        surface.blit(
            title,
            (width // 2 - title.get_width() // 2, 80)
        )

        # ======================
        # MENU LAYOUT
        # ======================
        menu_x = width // 2 - 220
        value_x = width // 2 + 60
        start_y = 200
        row_height = 50

        controls = self.game.config.get_controls(self.control_player)

        # ======================
        # DRAW ACTIONS
        # ======================
        for i, action in enumerate(self.actions):

            y = start_y + i * row_height

            # selected color
            color = COLORS.GRAY
            if i == self.control_selected:
                color = COLORS.CYAN

            # action name
            action_text = self.option_font.render(
                action.upper(),
                True,
                color
            )

            # key display
            value = controls[action]

            if isinstance(value, list):
                key_name = ", ".join(
                    pygame.key.name(k).upper() for k in value
                )
            elif isinstance(value, int):
                key_name = pygame.key.name(value).upper()
            else:
                key_name = "-"

            key_text = self.option_font.render(
                key_name,
                True,
                COLORS.WHITE
            )

            surface.blit(action_text, (menu_x, y))
            surface.blit(key_text, (value_x, y))

            # selection arrow
            if i == self.control_selected:
                arrow = self.option_font.render("►", True, COLORS.CYAN)
                surface.blit(arrow, (menu_x - 40, y))

        # ======================
        # WAITING FOR KEY
        # ======================
        if self.waiting_for_key:
            wait_text = self.option_font.render(
                "PRESS A KEY...",
                True,
                COLORS.RED
            )

            surface.blit(
                wait_text,
                (width // 2 - wait_text.get_width() // 2, 520)
            )

        # ======================
        # HINT TEXT
        # ======================
        hint = self.option_font.render(
            "ENTER: CHANGE   |   DEL: REMOVE   |   ESC: BACK",
            True,
            COLORS.GRAY
        )

        surface.blit(
            hint,
            (width // 2 - hint.get_width() // 2, 650)
        )

    # ==========================
    # ADJUST VOLUME
    # ==========================
    def adjust_value(self, delta):
        option = self.options[self.selected]
        if option == "MUSIC VOLUME":
            vol = self.game.config.get_music_volume()
            vol = max(0.0, min(1.0, vol + delta))
            self.game.config.data["audio"]["music_volume"] = vol
            self.game.config.save_config()
            pygame.mixer.music.set_volume(vol)
        elif option == "SFX VOLUME":
            vol = self.game.config.get_sfx_volume()
            vol = max(0.0, min(1.0, vol + delta))
            self.game.config.data["audio"]["sfx_volume"] = vol
            self.game.config.save_config()
            self.game.audio.set_sfx_volume(vol)

    # ==========================
    # UPDATE
    # ==========================
    def update(self, dt):
        keys = pygame.key.get_pressed()
        option = self.options[self.selected]
        if option in ["MUSIC VOLUME", "SFX VOLUME", "RESOLUTION", "FULLSCREEN"]:
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.hold_timer -= dt
                if self.hold_timer <= 0:

                    if option == "MUSIC VOLUME":
                        if keys[pygame.K_LEFT]:
                            self.adjust_value(-0.02)
                        if keys[pygame.K_RIGHT]:
                            self.adjust_value(0.02)

                    elif option == "SFX VOLUME":
                        if keys[pygame.K_LEFT]:
                            self.adjust_value(-0.02)
                        if keys[pygame.K_RIGHT]:
                            self.adjust_value(0.02)

                    elif option == "RESOLUTION":
                        if keys[pygame.K_LEFT]:
                            self.change_resolution(-1)
                        if keys[pygame.K_RIGHT]:
                            self.change_resolution(1)

                    elif option == "FULLSCREEN":
                        self.game.config.toggle_fullscreen()
                        self.game.create_window()

                    self.hold_timer = self.hold_delay
            else:
                self.hold_timer = 0
