import pygame

from constants import TILE_SIZE

class TileMap:
    def __init__(self, game):
        self.game = game
        self.map_data = game.level_map

        # ==========================================
        # LOAD ALL TILE IMAGES
        # ==========================================
        self.tiles = {
            'e': self.load("tileGrass_roadEast.png"),
            'n': self.load("tileGrass_roadNorth.png"),
            'X': self.load("tileGrass_roadCrossing.png"),
            'R': self.load("tileGrass_roadCornerLL.png"),
            'L': self.load("tileGrass_roadCornerLR.png"),
            'r': self.load("tileGrass_roadCornerUL.png"),
            'l': self.load("tileGrass_roadCornerUR.png"),
            'S': self.load("tileGrass_roadSplitS.png"),
            'E': self.load("tileGrass_roadSplitE.png"),
            'N': self.load("tileGrass_roadSplitN.png"),
            'W': self.load("tileGrass_roadSplitW.png"),
            'g': self.load("tileGrass2.png"),
            'B': self.load("tileRock_large.png"),
            'T': self.load("tree.png"),
        }

        # Tiles nào là vật cản (collision)
        self.blocking_tiles = ['B']

    # ==========================================
    # IMAGE LOADER WRAPPER
    # ==========================================
    def load(self, filename):
        return self.game.assets.load_image(
            filename,
            scale=(TILE_SIZE, TILE_SIZE)
        )

    # ==========================================
    # DRAW MAP
    # ==========================================
    def draw(self, surface):
        for row_index, row in enumerate(self.map_data):
            for col_index, tile_char in enumerate(row):

                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                surface.blit(self.tiles['g'], (x, y))

                if tile_char in self.tiles and tile_char not in ['g', 'T']:
                    surface.blit(self.tiles[tile_char], (x, y))

    # ==========================================
    # GET TILE AT GRID POSITION
    # ==========================================
    def get_tile(self, grid_x, grid_y):
        if 0 <= grid_y < len(self.map_data):
            if 0 <= grid_x < len(self.map_data[0]):
                return self.map_data[grid_y][grid_x]
        return None

    # ==========================================
    # CHECK COLLISION BY PIXEL POSITION
    # ==========================================
    def is_blocked(self, pixel_x, pixel_y):
        grid_x = int(pixel_x // TILE_SIZE)
        grid_y = int(pixel_y // TILE_SIZE)

        tile = self.get_tile(grid_x, grid_y)

        if tile in self.blocking_tiles:
            return True

        return False

    # ==========================================
    # MAP SIZE HELPERS
    # ==========================================
    @property
    def width(self):
        return len(self.map_data[0]) * TILE_SIZE

    @property
    def height(self):
        return len(self.map_data) * TILE_SIZE