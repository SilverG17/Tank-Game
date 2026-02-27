import pygame
import math


class Bullet:
    def __init__(self, pos, angle, owner, image, game, speed=450):
        self.pos = pygame.Vector2(pos)
        self.angle = angle
        self.game = game
        rad = math.radians(angle - 90)
        self.vel = pygame.Vector2(
            math.cos(rad),
            math.sin(rad)
        ) * speed
        self.owner = owner
        self.original_image = image
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.pos)
        self.active = True
        self.bounces = 0
        self.max_bounces = 3

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self, dt, level_map, tile_size, bounds_rect):
        next_pos = self.pos + self.vel * dt
        gx = int(next_pos.x // tile_size)
        gy = int(next_pos.y // tile_size)

        # ---- Bounce ----
        if 0 <= gy < len(level_map) and 0 <= gx < len(level_map[0]):
            if level_map[gy][gx] == 'B':

                rel_x = next_pos.x % tile_size
                rel_y = next_pos.y % tile_size

                margin = tile_size * 0.15

                if rel_x < margin or rel_x > tile_size - margin:
                    self.vel.x *= -1
                else:
                    self.vel.y *= -1

                if hasattr(self, "game"):
                    self.game.audio.play_sfx("bounce.mp3")

                self.bounces += 1
                if self.bounces > self.max_bounces:
                    self.active = False

                return
        self.pos = next_pos
        self.rect.center = self.pos
        if not bounds_rect.collidepoint(self.pos):
            self.active = False

    # =====================================================
    # DRAW
    # =====================================================
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def get_hitbox(self):
        return self.rect.inflate(-50, -50)