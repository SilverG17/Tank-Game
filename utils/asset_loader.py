import pygame
import os

class AssetLoader:
    def __init__(self, base_path="image", fonts_path="fonts"):
        self.base_path = base_path
        self.fonts_path = fonts_path
        self.images = {}
        self.fonts = {}

    # ==========================================
    # IMAGE LOADING
    # ==========================================
    def load_image(self, filename, colorkey=None, scale=None):
        key = (filename, scale)

        if key in self.images:
            return self.images[key]

        path = os.path.join(self.base_path, filename)
        image = pygame.image.load(path).convert_alpha()
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")

        if colorkey is not None:
            image.set_colorkey(colorkey)

        if scale:
            image = pygame.transform.smoothscale(image, scale)

        self.images[key] = image
        return image

    # ==========================================
    # FONT LOADING
    # ==========================================
    def load_font(self, filename, size):
        key = (filename, size)
        if key in self.fonts:
            return self.fonts[key]
        path = os.path.join(self.fonts_path, filename)
        font = pygame.font.Font(path, size)
        self.fonts[key] = font
        return font