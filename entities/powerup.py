import pygame
import random


class PowerUp:
    TYPES = ['SPEED', 'SHIELD', 'TRIPLE']

    def __init__(self, tile_size, level_map, images, duration=5.0):
        self.tile_size = tile_size
        self.level_map = level_map
        self.images = images
        self.duration = duration
        self.type = random.choice(self.TYPES)
        self.image = self.images[self.type]
        self.spawn()

    def spawn(self):
        valid_positions = []
        for gy, row in enumerate(self.level_map):
            for gx, char in enumerate(row):
                # Chỉ spawn trên cỏ hoặc đường
                if char == 'g' or char in "enXRLrlSENW":
                    x = gx * self.tile_size + self.tile_size // 2
                    y = gy * self.tile_size + self.tile_size // 2
                    valid_positions.append((x, y))

        if valid_positions:
            self.pos = pygame.Vector2(random.choice(valid_positions))
            self.rect = self.image.get_rect(center=self.pos)
        else:
            print("Warning: No valid position to spawn PowerUp!")

    def draw(self, surface):
        surface.blit(self.image, self.rect)