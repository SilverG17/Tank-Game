import pygame
import random

class Particle:
    def __init__(self, pos, velocity, lifetime, color, size):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(velocity)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size

    def update(self, dt):
        self.pos += self.vel * dt
        self.lifetime -= dt

    def draw(self, surface):
        if self.lifetime <= 0:
            return

        # Fade out
        alpha = max(0, self.lifetime / self.max_lifetime)
        radius = max(1, int(self.size * alpha))
        pygame.draw.circle(surface, self.color, self.pos, radius)

    def is_alive(self):
        return self.lifetime > 0

class ParticleSystem:
    def __init__(self):
        self.particles = []

    # ==========================================
    # GENERIC SPAWN
    # ==========================================
    def spawn(
        self,
        pos,
        count=10,
        speed_range=(50, 150),
        lifetime_range=(0.3, 0.6),
        color=(255, 200, 50),
        size_range=(3, 6),
    ):
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(*speed_range)
            velocity = pygame.Vector2(1, 0).rotate(angle) * speed
            lifetime = random.uniform(*lifetime_range)
            size = random.uniform(*size_range)
            p = Particle(pos, velocity, lifetime, color, size)
            self.particles.append(p)

    # ==========================================
    # UPDATE
    # ==========================================
    def update(self, dt):
        for p in self.particles:
            p.update(dt)

        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]

    # ==========================================
    # DRAW
    # ==========================================
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)