import pygame
import random

class Coin:
    def __init__(self, tile_size, level_map, image):
        self.tile_size = tile_size
        self.level_map = level_map
        self.image = image
        self.spawn()

    def spawn(self):
        valid_positions = []
        for gy in range(len(self.level_map)):
            for gx in range(len(self.level_map[gy])):
                # Không spawn vào đá, cây, ô trống đặc biệt
                if self.level_map[gy][gx] not in ['B', 'T', '.']:
                    valid_positions.append((gx, gy))
        if valid_positions:
            gx, gy = random.choice(valid_positions)
            self.pos = pygame.Vector2(
                gx * self.tile_size + self.tile_size // 2,
                gy * self.tile_size + self.tile_size // 2
            )
            self.rect = self.image.get_rect(center=self.pos)
        else:
            print("Warning: No valid position to spawn Coin!")

    def draw(self, surface):
        surface.blit(self.image, self.rect)