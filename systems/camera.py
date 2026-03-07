import pygame
import random

class Camera:
    def __init__(self):
        self.shake_timer = 0
        self.shake_strength = 0

    def shake(self, strength, duration):
        self.shake_strength = strength
        self.shake_timer = duration

    def update(self, dt):
        if self.shake_timer > 0:
            self.shake_timer -= dt

    def get_offset(self):
        if self.shake_timer > 0:
            return (
                random.randint(-self.shake_strength, self.shake_strength),
                random.randint(-self.shake_strength, self.shake_strength)
            )
        return (0, 0)