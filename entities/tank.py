import pygame
import math

from utils.helpers import key_pressed
from entities.bullet import Bullet
from constants import TURRET_OFFSETS, COLORS

class Tank:
    def __init__(
        self,
        pos,
        controls,
        color,
        name,
        turret_offset,
        images,
        tile_size,
        level_map,
        bounds_rect,
        game,
        start_angle=0,
        scale = 0.2
    ):
        self.pos = pygame.Vector2(pos)
        self.controls = controls
        self.name = name
        self.game = game
        self.tile_size = tile_size
        self.level_map = level_map
        self.scale = scale
        self.bounds_rect = bounds_rect
        self.max_health = 100
        self.turret_offset = pygame.Vector2(turret_offset) * scale

        # ===== Life State =====
        self.alive = True
        self.exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 1.0
        self.explosion_frame = 0

        # ===== Stats =====
        self.hull_angle = start_angle
        self.turret_angle = 0
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
        scale_factor = scale

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

        # ===== Apply color tint =====
        if color is None:
            # Default color (original PNG)
            self.hull = self.hull_orig.copy()
            self.gun = self.gun_orig.copy()
        else:
            # Apply tint
            self.hull = self.hull_orig.copy()
            self.hull.fill(color, special_flags=pygame.BLEND_MULT)

            self.gun = self.gun_orig.copy()
            self.gun.fill(color, special_flags=pygame.BLEND_MULT)

        self.rect = self.hull.get_rect(center=self.pos)

    # =========================================================
    # DAMAGE
    # =========================================================
    def take_damage(self, damage):
        if not self.alive:
            return

        if self.has_shield:
            return

        self.health -= damage
        self.flash_timer = 0.15 

        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.exploding = True
            self.explosion_timer = 0

    # =========================================================
    # COLLISION
    # =========================================================
    def get_hitbox(self):
        return self.rect.inflate(-20, 0)

    def check_collision(self, next_pos, trees):
        if not self.bounds_rect.collidepoint(next_pos):
            return False
        tank_rect = pygame.Rect(0,0,0,0)
        tank_rect = self.get_hitbox().copy()
        tank_rect.center = next_pos

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
        # Handle explosion animation when dead
        if not self.alive:
            if self.exploding:
                self.explosion_timer += dt
                frame_count = len(self.game.EXPLOSION_FRAMES)
                self.explosion_frame = int(
                    (self.explosion_timer / self.explosion_duration) * frame_count
                )
                if self.explosion_frame >= frame_count:
                    self.explosion_frame = frame_count - 1
            return
        
        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.controls and keys:
            # Rotation for base
            if key_pressed(keys, self.controls['left']):
                self.hull_angle -= sensitivity * dt
            if key_pressed(keys, self.controls['right']):
                self.hull_angle += sensitivity * dt

            # Rotation for gun
            gun_rotate_speed = sensitivity * dt
            if key_pressed(keys, self.controls['gun_left']):
                self.turret_angle -= gun_rotate_speed
            if key_pressed(keys, self.controls['gun_right']):
                self.turret_angle += gun_rotate_speed

            rad = math.radians(self.hull_angle - 90)
            move_vec = pygame.Vector2(0, 0)
            if key_pressed(keys, self.controls['up']):
                move_vec = pygame.Vector2(math.cos(rad), math.sin(rad))

            elif key_pressed(keys, self.controls['down']):
                move_vec = pygame.Vector2(-math.cos(rad), -math.sin(rad))
            if move_vec.length() > 0:
                move_vec = move_vec.normalize()
                velocity = move_vec * (160 * self.speed_boost) * dt

                # --- Move X axis first ---
                new_pos_x = pygame.Vector2(self.pos.x + velocity.x, self.pos.y)
                if self.check_collision(new_pos_x, trees):
                    self.pos.x = new_pos_x.x

                # --- Then move Y axis ---
                new_pos_y = pygame.Vector2(self.pos.x, self.pos.y + velocity.y)
                if self.check_collision(new_pos_y, trees):
                    self.pos.y = new_pos_y.y

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
        # Final turret direction
        gun_world_angle = self.hull_angle + self.turret_angle
        rad = math.radians(gun_world_angle - 90)

        barrel_length = 40

        spawn_pos = pygame.Vector2(
            self.pos.x + math.cos(rad) * barrel_length,
            self.pos.y + math.sin(rad) * barrel_length
        )

        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.cooldown_time:
            return None

        self.last_shot_time = current_time

        bullets = []

        if self.powerup_timers["TRIPLE"] > 0:
            angles = [
                gun_world_angle - 15,
                gun_world_angle,
                gun_world_angle + 15
            ]

            for a in angles:
                bullets.append(
                    Bullet(
                        pos=spawn_pos,
                        angle=a,
                        owner=self,
                        image=bullet_image,
                        game=self.game
                    )
                )

        else:
            bullets.append(
                Bullet(
                    pos=spawn_pos,
                    angle=gun_world_angle,
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
        # ===== EXPLOSION =====
        if self.exploding:
            frame = self.game.EXPLOSION_FRAMES[self.explosion_frame]

            # scale explosion based on tank size
            w = int(frame.get_width() * self.scale * 6)
            h = int(frame.get_height() * self.scale * 6)

            frame_scaled = pygame.transform.scale(frame, (w, h))

            rect = frame_scaled.get_rect(center=self.pos)
            surface.blit(frame_scaled, rect)
            return
        
        # Flash effect when hit
        hull_img = self.hull
        gun_img = self.gun

        if self.flash_timer > 0:
            hull_img = self.hull.copy()
            hull_img.fill(COLORS.WHITE, special_flags=pygame.BLEND_ADD)

            gun_img = self.gun.copy()
            gun_img.fill(COLORS.WHITE, special_flags=pygame.BLEND_ADD)

        # ===== SHADOW =====
        shadow_surface = pygame.Surface((40, 30), pygame.SRCALPHA)

        pygame.draw.ellipse(
            shadow_surface,
            (0,0,0,70),
            (0,0,40,30)
        )

        surface.blit(
            shadow_surface,
            (self.pos.x - 19, self.pos.y - 15)
        )

        # ===== HULL =====
        h_rot = pygame.transform.rotate(hull_img, -self.hull_angle)
        h_rect = h_rot.get_rect(center=self.pos)
        surface.blit(h_rot, h_rect)

        # ===== TURRET POSITION =====
        rotated_offset = self.turret_offset.rotate(self.hull_angle)
        gun_pos = self.pos + rotated_offset

        # ===== FINAL GUN ANGLE =====
        gun_world_angle = self.hull_angle + self.turret_angle

        # ===== DRAW GUN =====
        g_rot = pygame.transform.rotate(gun_img, -gun_world_angle)
        g_rect = g_rot.get_rect(center=gun_pos)

        surface.blit(g_rot, g_rect)

        # ===== POWERUP EFFECTS =====
        if self.has_shield:
            pygame.draw.circle(surface, COLORS.CYAN,
                               (int(self.pos.x), int(self.pos.y)), 35, 2)
        if self.speed_boost > 1.0:
            pygame.draw.circle(surface, COLORS.YELLOW,
                               (int(self.pos.x), int(self.pos.y)), 30, 1)

        if not self.alive:
            return