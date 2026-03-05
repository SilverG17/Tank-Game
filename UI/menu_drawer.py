import pygame

class MenuDrawer:
    # ==============================
    # SETTINGS MENU
    # ==============================
    @staticmethod
    def draw_settings(surface, game, state):
        """
        Draw the main settings menu.
        """
        bg = pygame.transform.scale(game.SETTINGS_BG, surface.get_size())
        surface.blit(bg, (0, 0))
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        width = surface.get_width()

        # ===== TITLE =====
        title = game.font_title.render("SETTINGS", True, (255, 220, 0))
        surface.blit(title, (width // 2 - title.get_width() // 2, 40))

        label_x = width // 2 - 200
        value_x = width // 2 + 80
        start_y = 200
        row_height = 60

        pygame.draw.line(
            surface,
            (60, 60, 100),
            (width // 2 + 40, start_y - 10),
            (width // 2 + 40, start_y + 450),
            2
        )

        for i, option in enumerate(state.options):

            y = start_y + i * row_height

            color = (255, 255, 255)
            if i == state.selected:
                color = (0, 255, 255)
                rect_left = label_x - 40
                rect_right = value_x + 235
                rect_width = rect_right - rect_left

                # highlight bar
                rect = pygame.Rect(rect_left, y - 6, rect_width, 42)

                pygame.draw.rect(surface, (35, 40, 80), rect)
                pygame.draw.rect(surface, (0, 255, 255), rect, 2)

            label = game.font_small.render(option, True, color)
            surface.blit(label, (label_x, y))

            # arrow
            if i == state.selected:
                arrow = game.font_small.render("►", True, (0,255,255))
                surface.blit(arrow, (label_x - 30, y))

            # ======================
            # RESOLUTION
            # ======================
            if option == "RESOLUTION":

                w, h = state.resolutions[state.res_index]

                if i == state.selected:
                    text = f"< {w} x {h} >"
                    value_color = (0, 255, 255)
                else:
                    text = f"{w} x {h}"
                    value_color = (150, 150, 150)

                value = game.font_small.render(text, True, value_color)
                surface.blit(value, (value_x + 60, y))

            # ======================
            # FULLSCREEN
            # ======================
            elif option == "FULLSCREEN":

                state_text = "ON" if game.config.is_fullscreen() else "OFF"

                value = game.font_small.render(
                    state_text,
                    True,
                    (180, 180, 180)
                )

                surface.blit(value, (value_x + 85, y))

            # ======================
            # MUSIC VOLUME
            # ======================
            elif option == "MUSIC VOLUME":

                value = game.config.get_music_volume()

                MenuDrawer.draw_bar(surface, value, value_x, y + 5)

            # ======================
            # SFX VOLUME
            # ======================
            elif option == "SFX VOLUME":

                value = game.config.get_sfx_volume()

                MenuDrawer.draw_bar(surface, value, value_x, y + 5)

            # ======================
            # NAVIGATION HINT
            # ======================
            hint = game.font_small.render(
                "↑ ↓ : Select   |   ← → : Change Value   |   ENTER : Confirm   |   ESC : Back",
                True,
                (160, 160, 160)
            )

            surface.blit(
                hint,
                (width // 2 - hint.get_width() // 2, surface.get_height() - 50)
            )

    # ==============================
    # CONTROL MENU
    # ==============================
    @staticmethod
    def draw_control_menu(surface, game, state):

        bg = pygame.transform.scale(game.SETTINGS_BG, surface.get_size())
        surface.blit(bg, (0, 0))
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        width = surface.get_width()

        title = game.font_title.render("SETTINGS", True, (255,230,120))

        shadow = game.font_title.render("SETTINGS", True, (0,0,0))

        surface.blit(shadow,(width//2-title.get_width()//2+3,83))
        surface.blit(title,(width//2-title.get_width()//2,80))

        surface.blit(title, (width // 2 - title.get_width() // 2, 80))

        controls = game.config.get_controls(state.control_player)

        menu_x = width // 2 - 150
        value_x = width // 2 + 50

        for i, action in enumerate(state.actions):

            y = 200 + i * 50

            color = (150, 150, 150)
            if i == state.control_selected:
                color = (0, 255, 255)

                pygame.draw.rect(
                    surface,
                    (40, 40, 70),
                    (menu_x - 60, y - 5, 360, 40)
                )

            action_text = game.font_small.render(
                action.upper(),
                True,
                color
            )

            value = controls[action]

            if isinstance(value, list):
                key_name = ", ".join(
                    pygame.key.name(k).upper() for k in value
                )
            elif isinstance(value, int):
                key_name = pygame.key.name(value).upper()
            else:
                key_name = str(value)

            key_text = game.font_small.render(
                key_name,
                True,
                (255, 255, 255)
            )

            surface.blit(action_text, (menu_x, y))
            surface.blit(key_text, (value_x, y))

        # waiting text
        if state.waiting_for_key:

            wait_text = game.font_small.render(
                "Press a key...",
                True,
                (255, 80, 80)
            )

            surface.blit(
                wait_text,
                (width // 2 - wait_text.get_width() // 2, 520)
            )

        hint = game.font_small.render(
            "ENTER: Change  |  DEL: Remove  |  ESC: Back",
            True,
            (160, 160, 160)
        )

        surface.blit(
            hint,
            (width // 2 - hint.get_width() // 2, 650)
        )

    # ==============================
    # VOLUME BAR
    # ==============================
    @staticmethod
    def draw_bar(surface, value, x, y):

        bar_width = 220
        bar_height = 14

        pygame.draw.rect(
            surface,
            (70, 70, 70),
            (x, y, bar_width, bar_height)
        )

        pygame.draw.rect(
            surface,
            (80, 220, 120),
            (x, y, int(bar_width * value), bar_height)
        )

        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (x, y, bar_width, bar_height),
            2
        )

    # ==============================
    # BACKGROUND
    # ==============================
    @staticmethod
    def draw_background(surface):

        w, h = surface.get_size()

        top = (25, 25, 55)
        bottom = (10, 10, 25)

        for y in range(h):
            t = y / h

            r = int(top[0] * (1 - t) + bottom[0] * t)
            g = int(top[1] * (1 - t) + bottom[1] * t)
            b = int(top[2] * (1 - t) + bottom[2] * t)

            pygame.draw.line(surface, (r, g, b), (0, y), (w, y))