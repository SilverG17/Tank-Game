import pygame
import math
import random

from constants import COLORS

class HUD:
    def __init__(self, game):
        self.game = game

    # ==========================================
    # HEALTH BAR + SCORE
    # ==========================================
    def draw_arcade_health_ui(self, surface, tanks):
        if self.game.mode == "CAMPAIGN":
            self.draw_campaign_health(surface, tanks)
            return
        bar_width = 200
        bar_height = 18
        padding = 20

        for i, tank in enumerate(tanks):

            health_ratio = tank.health / tank.max_health
            fill_width = int(bar_width * health_ratio)

            if i == 0:
                x = padding
                align_right = False

            elif i == 1:
                x = surface.get_width() - bar_width - padding
                align_right = True

            else:
                # fallback for future players
                x = padding + i * (bar_width + 10)
                align_right = False

            y = padding + 40

            # ===== Pulse when low HP =====
            pulse = 1.0
            if health_ratio <= 0.5:
                t = pygame.time.get_ticks() * 0.008
                pulse = 1 + 0.08 * math.sin(t)

            draw_width = int(bar_width * pulse)
            draw_height = int(bar_height * pulse)

            draw_x = x - (draw_width - bar_width) // 2
            draw_y = y - (draw_height - bar_height) // 2

            # ===== Player name =====
            name_text = self.game.font_big.render(
                tank.name, True, COLORS.WHITE
            )

            if align_right:
                name_rect = name_text.get_rect(
                    topright=(x + bar_width, padding - 10)
                )
            else:
                name_rect = name_text.get_rect(
                    topleft=(x, padding - 10)
                )

            surface.blit(name_text, name_rect)

            # ===== Health color =====
            if health_ratio > 0.6:
                color = COLORS.GREEN
            elif health_ratio > 0.3:
                color = COLORS.ORANGE
            else:
                color = COLORS.RED
            if health_ratio <= 0.3:
                draw_x += random.randint(-1, 1)
                draw_y += random.randint(-1, 1)

            # ===== Draw bar =====
            pygame.draw.rect(surface, (100,0,0),
                            (draw_x, draw_y, draw_width, draw_height))

            pygame.draw.rect(surface, color,
                            (draw_x, draw_y, int(draw_width * health_ratio), draw_height))

            pygame.draw.rect(surface, COLORS.WHITE,
                            (draw_x, draw_y, draw_width, draw_height), 2)

            # ===== Points =====
            if self.game.mode == "VERSUS":
                pt_text = self.game.font_small.render(
                    f"PT: {tank.point}", True, COLORS.WHITE
                )

                if i == 0:
                    pt_rect = pt_text.get_rect(
                        topleft=(x, y + bar_height + 6)
                    )
                else:
                    pt_rect = pt_text.get_rect(
                        topright=(x + bar_width, y + bar_height + 6)
                    )

                surface.blit(pt_text, pt_rect)

            # ===== HP text =====
            hp_text = self.game.font_small.render(
                f"{int(tank.health)}/{tank.max_health}",
                True,
                COLORS.WHITE
            )

            hp_rect = hp_text.get_rect(
                center=(x + bar_width // 2, y + bar_height // 2)
            )

            surface.blit(hp_text, hp_rect)

        # ===== Goal text =====
        t = pygame.time.get_ticks() * 0.002   # slower

        pulse = 0.75 + 0.25 * math.sin(t)     # range ~0.5–1.0

        r = int(255 * pulse)
        g = int(215 * pulse)
        b = int(0)

        color = (r, g, b)

        if self.game.mode == "VERSUS":
            goal_text = self.game.font_big.render(
                "GOAL: 400", True, color
            )

            goal_rect = goal_text.get_rect(
                midtop=(surface.get_width() // 2, 10)
            )

            surface.blit(goal_text, goal_rect)

    # ==========================================
    # Draw Campaign
    # ==========================================
    def draw_campaign_health(self, surface, tanks):
        padding = 20

        player = tanks[0]
        enemies = tanks[1:]

        bar_width = 200
        bar_height = 18

        # =====================
        # PLAYER BAR
        # =====================
        health_ratio = player.health / player.max_health

        x = padding
        y = padding + 40

        pygame.draw.rect(surface, (100,0,0),
            (x, y, bar_width, bar_height))

        pygame.draw.rect(surface, COLORS.GREEN,
            (x, y, int(bar_width * health_ratio), bar_height))

        pygame.draw.rect(surface, COLORS.WHITE,
            (x, y, bar_width, bar_height), 2)
        
        hp_text = self.game.font_small.render(
            f"{int(player.health)}/{player.max_health}",
            True,
            COLORS.WHITE
        )

        hp_rect = hp_text.get_rect(
            center=(x + bar_width // 2, y + bar_height // 2)
        )

        surface.blit(hp_text, hp_rect)

        name = self.game.font_big.render(
            player.name, True, COLORS.WHITE
        )

        surface.blit(name, (x, padding - 10))

        # =====================
        # ENEMY STACK
        # =====================
        enemy_bar_width = 140
        enemy_bar_height = 12
        spacing = 22

        start_x = surface.get_width() - enemy_bar_width - padding
        start_y = padding + 40

        for i, enemy in enumerate(enemies):

            if not enemy.alive:
                continue

            ratio = enemy.health / enemy.max_health

            x = start_x
            y = start_y + i * spacing

            pygame.draw.rect(surface, (100,0,0),
                (x, y, enemy_bar_width, enemy_bar_height))

            pygame.draw.rect(surface, COLORS.RED,
                (x, y, int(enemy_bar_width * ratio), enemy_bar_height))

            pygame.draw.rect(surface, COLORS.WHITE,
                (x, y, enemy_bar_width, enemy_bar_height), 2)

            label = self.game.font_small.render(
                f"ENEMY {i+1}", True, COLORS.WHITE
            )

            surface.blit(label, (x - label.get_width() - 6, y - 2))

    # ==========================================
    # CONTROL HINTS
    # ==========================================
    def draw_control_hints(self, surface, players):
        padding = 20
        bottom_y = surface.get_height() - 25

        # ===== PLAYER 1 =====
        if 1 in players: 
            p1_controls = self.game.config.get_controls(1)
            p1_fire = self.game.config.key_list_to_string(p1_controls["fire"])

            p1_text_str = (
                f"P1: "
                f"{self.game.config.key_to_string(p1_controls['up']).upper()} "
                f"{self.game.config.key_to_string(p1_controls['down']).upper()} "
                f"{self.game.config.key_to_string(p1_controls['left']).upper()} "
                f"{self.game.config.key_to_string(p1_controls['right']).upper()} "
                f"| GUN: "
                f"{self.game.config.key_to_string(p1_controls['gun_left']).upper()} "
                f"{self.game.config.key_to_string(p1_controls['gun_right']).upper()} "
                f"| FIRE: {p1_fire}"
            )

            p1_text = self.game.font_small.render(
                p1_text_str, True, COLORS.WHITE
            )

            p1_rect = p1_text.get_rect(
                bottomleft=(padding, bottom_y)
            )

            surface.blit(p1_text, p1_rect)

        # ===== PLAYER 2 =====
        if 2 in players:
            p2_controls = self.game.config.get_controls(2)
            p2_fire = self.game.config.key_list_to_string(p2_controls["fire"])

            p2_text_str = (
                f"P2: "
                f"{self.game.config.key_to_string(p2_controls['up']).upper()} "
                f"{self.game.config.key_to_string(p2_controls['down']).upper()} "
                f"{self.game.config.key_to_string(p2_controls['left']).upper()} "
                f"{self.game.config.key_to_string(p2_controls['right']).upper()} "
                f"| GUN: "
                f"{self.game.config.key_to_string(p2_controls['gun_left']).upper()} "
                f"{self.game.config.key_to_string(p2_controls['gun_right']).upper()} "
                f"| FIRE: {p2_fire}"
            )

            p2_text = self.game.font_small.render(
                p2_text_str, True, COLORS.WHITE
            )

            p2_rect = p2_text.get_rect(
                bottomright=(surface.get_width() - padding, bottom_y)
            )

            surface.blit(p2_text, p2_rect)