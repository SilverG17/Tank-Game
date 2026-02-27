import pygame
import math

from entities.bullet import Bullet

class Tank:
    def __init__(
        self,
        pos,
        controls,
        color,
        name,
        images,
        tile_size,
        level_map,
        bounds_rect,
        game,
        start_angle = 0
    ):
        self.pos = pygame.Vector2(pos)
        self.controls = controls
        self.name = name
        self.game = game
        self.tile_size = tile_size
        self.level_map = level_map
        self.bounds_rect = bounds_rect
        self.max_health = 100
        self.health = 100

        # ===== Stats =====
        self.hull_angle = start_angle
        self.gun_angle = start_angle
        self.health = 100
        self.point = 0
        self.flash_timer = 0

        # ===== Powerups =====
        self.speed_boost = 1.0
        self.has_shield = False
        self.powerup_timers = {
            'SPEED': 0,
            'SHIELD': 0,
            'TRIPLE': 0
        }
        self.max_bullets = 5
        self.cooldown_time = 500
        self.last_shot_time = 0

        # ===== Images =====
        scale_factor = 0.8  
        hull_size = (
            int(images["hull"].get_width() * scale_factor),
            int(images["hull"].get_height() * scale_factor)
        )
        self.hull_orig = pygame.transform.smoothscale(images["hull"], hull_size)
        gun_size = (
            int(images["gun"].get_width() * scale_factor),
            int(images["gun"].get_height() * scale_factor)
        )
        self.gun_orig = pygame.transform.smoothscale(images["gun"], gun_size)
        self.hull = self.hull_orig.copy()
        self.hull.fill(color, special_flags=pygame.BLEND_MULT)
        self.rect = self.hull.get_rect(center=self.pos)

    # =========================================================
    # COLLISION
    # =========================================================
    def check_collision(self, next_pos, trees):
        if not self.bounds_rect.collidepoint(next_pos):
            return False
        tank_rect = self.hull.get_rect(center=next_pos).inflate(-20, -20)

        # Check rock collision
        start_x = max(0, int((next_pos.x - self.tile_size) // self.tile_size))
        end_x = min(len(self.level_map[0]), int((next_pos.x + self.tile_size) // self.tile_size) + 1)
        start_y = max(0, int((next_pos.y - self.tile_size) // self.tile_size))
        end_y = min(len(self.level_map), int((next_pos.y + self.tile_size) // self.tile_size) + 1)
        for gy in range(start_y, end_y):
            for gx in range(start_x, end_x):
                if self.level_map[gy][gx] == 'B':
                    block_rect = pygame.Rect(
                        gx * self.tile_size,
                        gy * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                    if tank_rect.colliderect(block_rect):
                        return False

        # Check tree collision
        for t in trees:
            tree_rect = t.rect.inflate(-15, -15)
            if tank_rect.colliderect(tree_rect):
                return False
        return True

    # =========================================================
    # UPDATE
    # =========================================================
    def update(self, dt, keys, sensitivity, trees):
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Rotation for base
        if keys[self.controls['left']]:
            self.hull_angle -= sensitivity * dt
        if keys[self.controls['right']]:
            self.hull_angle += sensitivity * dt
        rad = math.radians(self.hull_angle - 90)

        # Rotation for gun
        gun_rotate_speed = sensitivity * dt
        if keys[self.controls['gun_left']]:
            self.gun_angle -= gun_rotate_speed
        if keys[self.controls['gun_right']]:
            self.gun_angle += gun_rotate_speed

        move_vec = pygame.Vector2(0, 0)
        if keys[self.controls['up']]:
            move_vec = pygame.Vector2(math.cos(rad), math.sin(rad))
        elif keys[self.controls['down']]:
            move_vec = pygame.Vector2(-math.cos(rad), -math.sin(rad))
        if move_vec.length() > 0:
            new_pos = self.pos + move_vec * (160 * self.speed_boost) * dt
            if self.check_collision(new_pos, trees):
                self.pos = new_pos
                self.rect.center = self.pos

        # Update powerup timers
        for key in self.powerup_timers:
            if self.powerup_timers[key] > 0:
                self.powerup_timers[key] -= dt
            else:
                if key == 'SPEED':
                    self.speed_boost = 1.0
                if key == 'SHIELD':
                    self.has_shield = False

    # =========================================================
    # SHOOT
    # =========================================================
    def shoot(self, bullet_image):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.cooldown_time:
            return None
        self.last_shot_time = current_time
        bullets = []
        if self.powerup_timers["TRIPLE"] > 0:
            angles = [self.gun_angle - 15, self.gun_angle, self.gun_angle + 15]
            for a in angles:
                bullets.append(
                    Bullet(
                        pos=self.pos,
                        angle=a,
                        owner=self,
                        image=bullet_image,
                        game=self.game
                    )
                )
        else:
            bullets.append(
                Bullet(
                    pos=self.pos,
                    angle=self.gun_angle,
                    owner=self,
                    image=bullet_image,
                    game=self.game
                )
            )
        return bullets

    # =========================================================
    # DRAW
    # =========================================================
    def draw(self, surface):
        if self.flash_timer > 0 and int(self.flash_timer * 15) % 2 == 0:
            return
        if self.has_shield:
            pygame.draw.circle(surface, (0, 255, 255),
                               (int(self.pos.x), int(self.pos.y)), 35, 2)
        if self.speed_boost > 1.0:
            pygame.draw.circle(surface, (255, 255, 0),
                               (int(self.pos.x), int(self.pos.y)), 30, 1)
        h_rot = pygame.transform.rotate(self.hull, -self.hull_angle)
        g_rot = pygame.transform.rotate(self.gun_orig, -self.gun_angle)
        surface.blit(h_rot, h_rot.get_rect(center=self.pos))
        surface.blit(g_rot, g_rot.get_rect(center=self.pos))