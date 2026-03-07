import pygame

from entities.tank import Tank

class BossTank(Tank):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flash_timer = 0
        self.flash_interval = 0.1
        self.flash_state = True

        # Boss stats
        self.max_health = 400
        self.health = 400

        # Boss weapon settings
        self.bullet_scale = 2.5
        self.cooldown_time = 700

    def check_collision(self, next_pos, trees):
        # ignore trees, only check walls
        if not self.bounds_rect.collidepoint(next_pos):
            return False
        return True
    
    def shoot(self, bullet_image):

        # scale bullet image
        w = int(bullet_image.get_width() * self.bullet_scale)
        h = int(bullet_image.get_height() * self.bullet_scale)

        big_bullet = pygame.transform.scale(bullet_image, (w, h))

        bullets = super().shoot(big_bullet)

        return bullets
    
    def update(self, dt, keys, sensitivity, trees):

        # Don't run normal update if exploding
        if self.exploding:
            # Only update explosion timer
            self.explosion_timer += dt
            frame_count = len(self.game.EXPLOSION_FRAMES)
            self.explosion_frame = int(
                (self.explosion_timer / self.explosion_duration) * frame_count
            )
            if self.explosion_frame >= frame_count:
                self.explosion_frame = frame_count - 1
            return

        # run normal tank update (only if alive and not exploding)
        super().update(dt, keys, sensitivity, trees)

        # boss death flashing - only during dying phase, not when exploding
        if hasattr(self.game.state, 'boss_dying') and self.game.state.boss_dying:

            self.flash_timer += dt

            if self.flash_timer >= self.flash_interval:
                self.flash_timer = 0
                self.flash_state = not self.flash_state

    def draw(self, surface):

        # Draw explosion if exploding
        if self.exploding:
            frame = self.game.EXPLOSION_FRAMES[self.explosion_frame]

            # scale explosion based on tank size
            w = int(frame.get_width() * self.scale * 6)
            h = int(frame.get_height() * self.scale * 6)

            frame_scaled = pygame.transform.scale(frame, (w, h))

            rect = frame_scaled.get_rect(center=self.pos)
            surface.blit(frame_scaled, rect)
            return

        hull_img = self.hull
        gun_img = self.gun

        # Boss dying flash
        if hasattr(self.game.state, "boss_dying") and self.game.state.boss_dying:

            color = (255,0,0) if self.flash_state else (255,255,255)

            hull_img = self.hull.copy()
            hull_img.fill(color, special_flags=pygame.BLEND_ADD)

            gun_img = self.gun.copy()
            gun_img.fill(color, special_flags=pygame.BLEND_ADD)

        # Flash effect when hit
        if self.flash_timer > 0 and not hasattr(self.game.state, 'boss_dying'):
            hull_img = self.hull.copy()
            hull_img.fill((255,255,255), special_flags=pygame.BLEND_ADD)

            gun_img = self.gun.copy()
            gun_img.fill((255,255,255), special_flags=pygame.BLEND_ADD)

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

        gun_world_angle = self.hull_angle + self.turret_angle

        # ===== GUN =====
        g_rot = pygame.transform.rotate(gun_img, -gun_world_angle)
        g_rect = g_rot.get_rect(center=gun_pos)

        surface.blit(g_rot, g_rect)