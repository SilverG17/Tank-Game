import pygame
import os

class AssetLoader:
    def __init__(self, base_path="image"):
        self.base_path = base_path
        self.images = {}
        self.fonts = {}

    # ==========================================
    # IMAGE LOADING
    # ==========================================
    def load_image(self, filename, colorkey=None, scale=None):
        """
        filename: path relative to assets folder
        colorkey: màu trong suốt
        scale: (w, h)
        """
        if filename in self.images:
            return self.images[filename]
        path = os.path.join(self.base_path, filename)
        image = pygame.image.load(path).convert_alpha()
        if colorkey is not None:
            image.set_colorkey(colorkey)
        if scale:
            image = pygame.transform.scale(image, scale)
        self.images[filename] = image
        return image

    # ==========================================
    # FONT LOADING
    # ==========================================
    def load_font(self, filename, size):
        key = (filename, size)
        if key in self.fonts:
            return self.fonts[key]
        path = os.path.join(self.base_path, filename)
        font = pygame.font.Font(path, size)
        self.fonts[key] = font
        return font