import pygame


class Tree:
    def __init__(self, gx, gy, tile_size, image):
        self.gx = gx
        self.gy = gy
        self.tile_size = tile_size
        self.image = image.copy()
        self.pos = pygame.Vector2(
            gx * tile_size,
            gy * tile_size
        )
        self.rect = pygame.Rect(
            self.pos.x,
            self.pos.y,
            tile_size,
            tile_size
        )
        self.max_health = 4
        self.health = self.max_health

    def take_damage(self, amount=1):
        self.health -= amount
        return self.health <= 0  # True nếu cây chết

    def draw(self, surface):
        alpha = int((self.health / self.max_health) * 255)
        img = self.image.copy()   # copy mới mỗi frame
        img.set_alpha(alpha)
        surface.blit(img, self.pos)

    def get_hitbox(self):
        return pygame.Rect(
            self.rect.centerx - 12,
            self.rect.bottom - 28,
            24,
            28
        )