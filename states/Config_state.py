import pygame

from states.base_state import BaseState
from constants import Color
from states.start_state import StartState

class ConfigState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = game.font_big
        self.option_font = game.font_small
        self.options = [
            "MUSIC VOLUME",
            "SFX VOLUME",
            "PLAYER 1 CONTROLS",
            "PLAYER 2 CONTROLS",
            "TOGGLE MUTE",
            "BACK"
        ]
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

                        # luôn lưu dạng list[int]
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

    # ==========================
    # DRAW
    # ==========================
    def draw(self, surface):
        surface.fill((20, 20, 40))
        width = surface.get_width()
        title = self.title_font.render("SETTINGS", True, Color.YELLOW)
        surface.blit(
            title,
            (width // 2 - title.get_width() // 2, 80)
        )
        if self.control_mode:
            self.draw_control_menu(surface)
            return
        for i, option in enumerate(self.options):
            color = Color.WHITE
            if i == self.selected:
                color = Color.CYAN
            text = self.option_font.render(option, True, color)
            y = 200 + i * 60
            surface.blit(
                text,
                (width // 2 - text.get_width() // 2, y)
            )

            # ===== DRAW VOLUME BAR =====
            if option == "MUSIC VOLUME":
                value = self.game.config.get_music_volume()
                self.draw_bar(surface, value, y + 30)
            if option == "SFX VOLUME":
                value = self.game.config.get_sfx_volume()
                self.draw_bar(surface, value, y + 30)

    def draw_bar(self, surface, value, y):
        width = surface.get_width()
        bar_width = 300
        bar_height = 15
        x = width // 2 - bar_width // 2

        # nền
        pygame.draw.rect(surface, (80, 80, 80),
                        (x, y, bar_width, bar_height))

        # phần volume
        pygame.draw.rect(surface, Color.GREEN,
                        (x, y, bar_width * value, bar_height))
        
    def draw_control_menu(self, surface):
        surface.fill((20, 20, 40))
        width = surface.get_width()
        title = self.title_font.render(
            f"PLAYER {self.control_player} CONTROLS",
            True,
            Color.YELLOW
        )
        surface.blit(
            title,
            (width // 2 - title.get_width() // 2, 80)
        )
        controls = self.game.config.get_controls(self.control_player)
        for i, action in enumerate(self.actions):
            value = controls[action]
            if isinstance(value, list):
                key_name = ", ".join(
                    pygame.key.name(k).upper() for k in value
                )
            elif isinstance(value, int):
                key_name = pygame.key.name(value).upper()
            else:
                key_name = str(value).upper()
            text_str = f"{action.upper()}: {key_name}"
            color = Color.WHITE
            if i == self.control_selected:
                color = Color.CYAN
            text = self.option_font.render(text_str, True, color)
            y = 200 + i * 50
            surface.blit(
                text,
                (width // 2 - text.get_width() // 2, y)
            )
        if self.waiting_for_key:
            wait_text = self.option_font.render(
                "Press a key...",
                True,
                Color.RED
            )
            surface.blit(
                wait_text,
                (width // 2 - wait_text.get_width() // 2, 500)
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
        if option in ["MUSIC VOLUME", "SFX VOLUME"]:
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.hold_timer -= dt
                if self.hold_timer <= 0:
                    if keys[pygame.K_LEFT]:
                        self.adjust_value(-0.02)
                    if keys[pygame.K_RIGHT]:
                        self.adjust_value(0.02)
                    self.hold_timer = self.hold_delay
            else:
                self.hold_timer = 0
