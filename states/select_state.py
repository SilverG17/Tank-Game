import pygame

from states.base_state import BaseState
from states.versus_state import VersusState
from states.cutscene_state import CutsceneState
from states.coop_state import CoopState
from constants import TURRET_OFFSETS, TANK_COLORS, COLORS

class SelectState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.SELECT_BG = game.SELECT_BG
        self.SELECT_BG = pygame.transform.scale(
            self.SELECT_BG,
            (game.screen.get_width(), game.screen.get_height())
        )

        # ===== Player selections =====
        self.p1_hull = 0
        self.p1_gun = 0
        self.p1_color = 0

        self.p2_hull = 1
        self.p2_gun = 1
        self.p2_color = 1

        self.max_colors = len(TANK_COLORS)
        self.max_styles = len(self.game.TANK_HULLS)
        self.cursor = 0
        self.preview_angle = 0

        # ===== Campaign settings =====
        self.enemy_count = 1
        self.max_enemies = 5

    # ======================================
    # INPUT
    # ======================================
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from states.start_state import StartState
                    self.game.change_state(StartState(self.game))
                if event.key == pygame.K_UP:
                    max_cursor = 6 if self.game.mode == "VERSUS" or self.game.mode == "COOP" else 4
                    self.cursor = (self.cursor - 1) % max_cursor
                if event.key == pygame.K_DOWN:
                    max_cursor = 6 if self.game.mode == "VERSUS" or self.game.mode == "COOP" else 4
                    self.cursor = (self.cursor + 1) % max_cursor
                if event.key == pygame.K_LEFT:
                    self.change_style(-1)
                if event.key == pygame.K_RIGHT:
                    self.change_style(1)
                if event.key == pygame.K_SPACE:
                    self.start_game()

    # ======================================
    # CHANGE STYLE
    # ======================================
    def change_style(self, direction):

        # ===== CAMPAIGN MODE =====
        if self.game.mode == "CAMPAIGN":

            if self.cursor == 0:
                self.p1_hull = (self.p1_hull + direction) % self.max_styles

            elif self.cursor == 1:
                self.p1_gun = (self.p1_gun + direction) % self.max_styles

            elif self.cursor == 2:
                self.p1_color = (self.p1_color + direction) % self.max_colors

            elif self.cursor == 3:
                self.enemy_count += direction

                if self.enemy_count < 1:
                    self.enemy_count = self.max_enemies
                elif self.enemy_count > self.max_enemies:
                    self.enemy_count = 1

            return

        # ===== VERSUS MODE =====
        if self.cursor == 0:
            self.p1_hull = (self.p1_hull + direction) % self.max_styles

        elif self.cursor == 1:
            self.p1_gun = (self.p1_gun + direction) % self.max_styles

        elif self.cursor == 2:
            self.p1_color = (self.p1_color + direction) % self.max_colors

        elif self.cursor == 3:
            self.p2_hull = (self.p2_hull + direction) % self.max_styles

        elif self.cursor == 4:
            self.p2_gun = (self.p2_gun + direction) % self.max_styles

        elif self.cursor == 5:
            self.p2_color = (self.p2_color + direction) % self.max_colors

    # ======================================
    # START GAME
    # ======================================
    def start_game(self):
        # Save selections into Game
        self.game.player_styles[1] = {
            "hull": self.p1_hull,
            "gun": self.p1_gun,
            "color": TANK_COLORS[self.p1_color][1]
        }

        self.game.player_styles[2] = {
            "hull": self.p2_hull,
            "gun": self.p2_gun,
            "color": TANK_COLORS[self.p2_color][1]
        }

        if self.game.mode == "VERSUS":
            self.game.change_state(VersusState(self.game))

        elif self.game.mode == "CAMPAIGN":
            self.game.enemy_count = self.enemy_count
            self.game.change_state(CutsceneState(self.game))

        elif self.game.mode == "COOP":
            self.game.enemy_count = self.enemy_count
            self.game.change_state(CoopState(self.game))

    # ======================================
    # UPDATE
    # ======================================
    def update(self, dt):
        self.preview_angle = (self.preview_angle + 40 * dt) % 360
        pass

    # ======================================
    # DRAW
    # ======================================
    def draw(self, surface):
        surface.blit(self.SELECT_BG, (0, 0))
        width = surface.get_width()
        height = surface.get_height()

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        # TITLE
        title = self.game.font_title.render(
            "SELECT TANK STYLE",
            True,
            COLORS.YELLOW
        )

        surface.blit(
            title,
            (width // 2 - title.get_width() // 2, 60)
        )

        # OPTIONS
        if self.game.mode == "VERSUS" or self.game.mode == "COOP":
            options = [
                f"P1 Hull  : {self.p1_hull + 1}",
                f"P1 Gun   : {self.p1_gun + 1}",
                f"P1 Color : {TANK_COLORS[self.p1_color][0]}",
                f"P2 Hull  : {self.p2_hull + 1}",
                f"P2 Gun   : {self.p2_gun + 1}",
                f"P2 Color : {TANK_COLORS[self.p2_color][0]}",
            ]
        else:
            options = [
                f"Hull    : {self.p1_hull + 1}",
                f"Gun     : {self.p1_gun + 1}",
                f"Color   : {TANK_COLORS[self.p1_color][0]}",
                f"Enemies : {self.enemy_count}",
            ]

        start_y = 220

        for i, text in enumerate(options):

            color = COLORS.YELLOW if i == self.cursor else COLORS.WHITE

            txt = self.game.font_big.render(text, True, color)

            surface.blit(
                txt,
                (width // 2 - txt.get_width() // 2, start_y + i * 60)
            )

        # TANK PREVIEW
        self.draw_preview(surface)

        # INSTRUCTION
        hint = self.game.font_small.render(
            "UP/DOWN select | LEFT/RIGHT change | SPACE start | ESC back",
            True,
            COLORS.GRAY
        )

        surface.blit(
            hint,
            (width // 2 - hint.get_width() // 2, height - 60)
        )

    # ======================================
    # TANK PREVIEW
    # ======================================
    def draw_preview(self, surface):
        preview_scale = 0.2
        width = surface.get_width()

        # ===== PLAYER 1 DATA =====
        p1_color = TANK_COLORS[self.p1_color][1]
        p1_hull_img = self.game.TANK_HULLS[self.p1_hull].copy()
        p1_gun_img = self.game.TANK_GUNS[self.p1_gun].copy()

        hull_size = (
            int(p1_hull_img.get_width() * preview_scale),
            int(p1_hull_img.get_height() * preview_scale)
        )

        gun_size = (
            int(p1_gun_img.get_width() * preview_scale),
            int(p1_gun_img.get_height() * preview_scale)
        )

        p1_hull_img = pygame.transform.smoothscale(p1_hull_img, hull_size)
        p1_gun_img = pygame.transform.smoothscale(p1_gun_img, gun_size)

        # ===== PLAYER 2 DATA =====
        p2_color = TANK_COLORS[self.p2_color][1]
        p2_hull_img = self.game.TANK_HULLS[self.p2_hull].copy()
        p2_gun_img = self.game.TANK_GUNS[self.p2_gun].copy()

        hull_size = (
            int(p2_hull_img.get_width() * preview_scale),
            int(p2_hull_img.get_height() * preview_scale)
        )

        gun_size = (
            int(p2_gun_img.get_width() * preview_scale),
            int(p2_gun_img.get_height() * preview_scale)
        )

        p2_hull_img = pygame.transform.smoothscale(p2_hull_img, hull_size)
        p2_gun_img = pygame.transform.smoothscale(p2_gun_img, gun_size)

        # ===== APPLY COLOR =====
        if p1_color is not None:
            p1_hull_img.fill(p1_color, special_flags=pygame.BLEND_MULT)
            p1_gun_img.fill(p1_color, special_flags=pygame.BLEND_MULT)

        if p2_color is not None:
            p2_hull_img.fill(p2_color, special_flags=pygame.BLEND_MULT)
            p2_gun_img.fill(p2_color, special_flags=pygame.BLEND_MULT)

        # ===== PREVIEW POSITION =====
        x1 = width // 2 - 250
        x2 = width // 2 + 250
        y = 460

        # ===== OFFSET (same system as Tank class) =====
        offset_p1 = pygame.Vector2(TURRET_OFFSETS[self.p1_hull]) * preview_scale
        offset_p2 = pygame.Vector2(TURRET_OFFSETS[self.p2_hull]) * preview_scale

        hull_angle = self.preview_angle
        gun_angle = self.preview_angle

        p1_label = self.game.font_small.render("PLAYER 1", True, COLORS.WHITE)
        surface.blit(p1_label, p1_label.get_rect(center=(x1, y + 90)))

        # =====================================
        # PLAYER 1
        # =====================================
        # rotate hull
        p1_hull_rot = pygame.transform.rotate(p1_hull_img, -hull_angle)
        surface.blit(p1_hull_rot, p1_hull_rot.get_rect(center=(x1, y)))

        # turret position
        offset = offset_p1.rotate(hull_angle)
        gun_pos = (x1 + offset.x, y + offset.y)

        # rotate gun
        p1_gun_rot = pygame.transform.rotate(p1_gun_img, -gun_angle)
        surface.blit(p1_gun_rot, p1_gun_rot.get_rect(center=gun_pos))

        # =====================================
        # PLAYER 2
        # =====================================
        if self.game.mode == "VERSUS" or self.game.mode == "COOP":
            p2_hull_rot = pygame.transform.rotate(p2_hull_img, -hull_angle)
            surface.blit(p2_hull_rot, p2_hull_rot.get_rect(center=(x2, y)))

            offset = offset_p2.rotate(hull_angle)
            gun_pos = (x2 + offset.x, y + offset.y)

            p2_gun_rot = pygame.transform.rotate(p2_gun_img, -gun_angle)
            surface.blit(p2_gun_rot, p2_gun_rot.get_rect(center=gun_pos))

            p2_label = self.game.font_small.render("PLAYER 2", True, COLORS.WHITE)
            surface.blit(p2_label, p2_label.get_rect(center=(x2, y + 90)))