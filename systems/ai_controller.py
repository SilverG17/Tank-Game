import pygame
import math
import random

IDEAL_RANGE = 240
TOLERANCE = 80
PANIC_RANGE = 90

class TankAI:
    def __init__(self, tank, players, trees):
        self.enabled = True
        self.tank = tank
        self.players = players
        self.trees = trees

        self.move_speed = 120
        self.rotate_speed = 140
        self.turret_speed = 200

        self.move_state = "approach"
        self.move_timer = 0
        self.move_duration = random.uniform(0.6, 1.2)
        self.shoot_timer = 0
        self.shoot_delay = 1.2

        self.strafe_dir = random.choice([-1, 1])
        self.strafe_timer = 0

    # ==========================================
    # Update
    # ==========================================
    def update(self, dt):
        if not self.tank.alive or self.tank.exploding or not self.enabled:
            return
        self.target = self.get_target()
        if not self.target:
            return

        self.move_timer += dt
        dx = self.target.pos.x - self.tank.pos.x
        dy = self.target.pos.y - self.tank.pos.y
        dist = math.hypot(dx, dy)

        target_angle = math.degrees(math.atan2(dy, dx)) + 90

        if dist > 180:
            self.rotate_hull(target_angle, dt)

        if self.move_timer > self.move_duration:
            self.move_timer = 0
            if dist > IDEAL_RANGE + TOLERANCE:
                self.move_state = "approach"
            elif dist < PANIC_RANGE:
                self.move_state = "retreat"
            else:
                self.move_state = "strafe"

        if self.move_state == "approach":
            self.move_forward(dt)

        elif self.move_state == "retreat":
            self.move_backward(dt)

        elif self.move_state == "strafe":
            self.strafe(dt)

        self.aim_turret(target_angle, dt)
        diff = (target_angle - (self.tank.hull_angle + self.tank.turret_angle) + 180) % 360 - 180
        if abs(diff) < 5:
            self.try_shoot(dt)

    # ==========================================
    # Hull Rotation
    # ==========================================
    def rotate_hull(self, target_angle, dt):

        diff = (target_angle - self.tank.hull_angle + 180) % 360 - 180

        if diff > 3:
            self.tank.hull_angle += self.rotate_speed * dt
        elif diff < -3:
            self.tank.hull_angle -= self.rotate_speed * dt

    # ==========================================
    # Movement
    # ==========================================
    def move_forward(self, dt):
        self.move(dt, 1)

    def move_backward(self, dt):
        self.move(dt, -1)


    def strafe(self, dt):

        self.strafe_timer += dt
        if self.strafe_timer > random.uniform(1.5, 3.5):
            self.strafe_dir *= -1
            self.strafe_timer = 0

        rad = math.radians(self.tank.hull_angle + (90 * self.strafe_dir))

        move_vec = pygame.Vector2(
            math.cos(rad),
            math.sin(rad)
        )

        velocity = move_vec * self.move_speed * dt
        new_pos = self.tank.pos + velocity

        if self.tank.check_collision(new_pos, self.trees):
            self.tank.pos = new_pos
            self.tank.rect.center = self.tank.pos


    def move(self, dt, direction):

        rad = math.radians(self.tank.hull_angle - 90)

        move_vec = pygame.Vector2(
            math.cos(rad) * direction,
            math.sin(rad) * direction
        )

        velocity = move_vec * self.move_speed * dt
        new_pos = self.tank.pos + velocity

        if self.tank.check_collision(new_pos, self.trees):
            self.tank.pos = new_pos
            self.tank.rect.center = self.tank.pos
        else:
            # obstacle avoidance
            self.tank.hull_angle += random.choice([-90, 90])

    # ==========================================
    # Turret Aiming
    # ==========================================
    def aim_turret(self, target_angle, dt):

        desired = target_angle - self.tank.hull_angle
        diff = (desired - self.tank.turret_angle + 180) % 360 - 180

        if diff > 2:
            self.tank.turret_angle += self.turret_speed * dt
        elif diff < -2:
            self.tank.turret_angle -= self.turret_speed * dt


    # ==========================================
    # Shooting
    # ==========================================
    def try_shoot(self, dt):
        if not self.target.alive:
            return
        self.shoot_timer += dt
        if self.shoot_timer < self.shoot_delay:
            return

        dx = self.target.pos.x - self.tank.pos.x
        dy = self.target.pos.y - self.tank.pos.y

        target_angle = math.degrees(math.atan2(dy, dx)) + 90
        turret_world = self.tank.hull_angle + self.tank.turret_angle

        diff = (target_angle - turret_world + 180) % 360 - 180

        if abs(diff) > 20:
            return

        blocker = self.get_blocking_object()

        # Shoot player normally
        if blocker is None:
            bullet = self.tank.shoot(self.tank.game.BULLET_IMG)

        # Shoot obstacle (tree/rock)
        else:
            bullet = self.tank.shoot(self.tank.game.BULLET_IMG)

        if bullet:
            self.tank.game.state.bullets.extend(bullet)

        self.shoot_timer = 0

    # ==========================================
    # Line of sight check
    # ==========================================
    def get_blocking_object(self):
        direction = self.target.pos - self.tank.pos
        distance = direction.length()

        if distance == 0:
            return None

        direction.normalize_ip()

        step = 20

        for i in range(0, int(distance), step):

            check = self.tank.pos + direction * i

            # Check trees first
            for t in self.trees:
                if t.rect.collidepoint(check):
                    return t

            gx = int(check.x // self.tank.tile_size)
            gy = int(check.y // self.tank.tile_size)

            # prevent crash outside map
            if gy < 0 or gy >= len(self.tank.level_map):
                continue

            if gx < 0 or gx >= len(self.tank.level_map[0]):
                continue

            if self.tank.level_map[gy][gx] == 'B':
                return "rock"

        return None
    
    def get_target(self):
        alive_players = [p for p in self.players if p.alive]
        if not alive_players:
            return None

        return min(
            alive_players,
            key=lambda p: (p.pos - self.tank.pos).length()
        )