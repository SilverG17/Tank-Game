import pygame
from constants import COLORS


class Debug:
    def __init__(self, game):
        self.game = game
        self.hitbox_enabled = False
        self.FPS_enabled = False
        self.font = pygame.font.SysFont("consolas", 16)

    # ==============================
    # Toggle
    # ==============================
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.hitbox_enabled = not self.hitbox_enabled
            if event.key == pygame.K_F2:
                self.FPS_enabled = not self.FPS_enabled
            if event.key == pygame.K_F3:
                self.kill_all_enemies()

    # ==============================
    # Draw hitboxes
    # ==============================
    def draw_hitboxes(self, surface, tanks=None, bullets=None, trees=None):
        if not self.hitbox_enabled:
            return

        if tanks:
            for tank in tanks:
                pygame.draw.rect(surface, COLORS.GREEN, tank.get_hitbox(), 2)

        if trees:
            for tree in trees:
                pygame.draw.rect(surface, COLORS.RED, tree.get_hitbox(), 2)

        if bullets:
            for bullet in bullets:
                pygame.draw.rect(surface, COLORS.YELLOW, bullet.get_hitbox(), 2)

    # ==============================
    # Draw FPS
    # ==============================
    def draw_fps(self, surface, clock):
        if not self.FPS_enabled:
            return

        fps = int(clock.get_fps())
        text = self.font.render(f"FPS: {fps}", True, (255,255,255))
        surface.blit(text, (10,5))

    # ==============================
    # Kill Enemy
    # ==============================
    def kill_all_enemies(self):
        state = self.game.state

        # Kill normal enemies
        if hasattr(state, "enemies"):
            for enemy in state.enemies:
                if getattr(enemy, "alive", False):
                    if hasattr(enemy, "take_damage"):
                        enemy.take_damage(9999)
                    else:
                        enemy.health = 0
                        enemy.alive = False
                        enemy.exploding = True
                        enemy.explosion_timer = 0

        # Kill boss
        if hasattr(state, "boss") and state.boss:
            boss = state.boss

            if getattr(boss, "alive", False):
                if hasattr(boss, "take_damage"):
                    boss.take_damage(9999)
                else:
                    boss.health = 0
                    boss.alive = False
                    boss.exploding = True
                    boss.explosion_timer = 0