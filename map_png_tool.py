import pygame
import os

# ==============================
# CONFIG
# ==============================

TILE_SIZE = 64
PREVIEW_SIZE = (400, 250)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_FOLDER = os.path.join(BASE_DIR, "maps")
IMAGE_FOLDER = os.path.join(BASE_DIR, "image")

# ==============================
# LOAD MAP FILE
# ==============================

def load_map(path):
    with open(path, "r") as f:
        return [list(line.strip()) for line in f]

# ==============================
# LOAD TILE IMAGES
# ==============================

def load_tiles():
    tiles = {}

    def load(name):
        img = pygame.image.load(os.path.join(IMAGE_FOLDER, name)).convert_alpha()
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

    tiles['e'] = load("tileGrass_roadEast.png")
    tiles['n'] = load("tileGrass_roadNorth.png")
    tiles['X'] = load("tileGrass_roadCrossing.png")
    tiles['R'] = load("tileGrass_roadCornerLL.png")
    tiles['L'] = load("tileGrass_roadCornerLR.png")
    tiles['r'] = load("tileGrass_roadCornerUL.png")
    tiles['l'] = load("tileGrass_roadCornerUR.png")
    tiles['S'] = load("tileGrass_roadSplitS.png")
    tiles['E'] = load("tileGrass_roadSplitE.png")
    tiles['N'] = load("tileGrass_roadSplitN.png")
    tiles['W'] = load("tileGrass_roadSplitW.png")
    tiles['g'] = load("tileGrass2.png")
    tiles['B'] = load("tileRock_large.png")
    tiles['T'] = load("tree.png")

    return tiles

# ==============================
# RENDER MAP TO SURFACE
# ==============================

def render_map(map_data, tiles):

    rows = len(map_data)
    cols = len(map_data[0])

    surface = pygame.Surface((cols * TILE_SIZE, rows * TILE_SIZE), pygame.SRCALPHA)

    for row_index, row in enumerate(map_data):
        for col_index, tile_char in enumerate(row):

            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE

            # nền grass luôn vẽ trước
            surface.blit(tiles['g'], (x, y))

            if tile_char in tiles and tile_char != 'g':
                surface.blit(tiles[tile_char], (x, y))

    return surface

# ==============================
# EXPORT ALL MAPS
# ==============================
def export_all_maps():
    pygame.init()
    pygame.display.set_mode((1, 1))
    tiles = load_tiles()
    for file in os.listdir(MAP_FOLDER):
        if not file.endswith(".txt"):
            continue
        map_path = os.path.join(MAP_FOLDER, file)
        map_data = load_map(map_path)
        rendered = render_map(map_data, tiles)

        # scale về preview size
        preview = pygame.transform.scale(rendered, PREVIEW_SIZE)
        name = file.replace(".txt", ".png")
        save_path = os.path.join(IMAGE_FOLDER, name)
        pygame.image.save(preview, save_path)
        print(f"Saved preview: {name}")
    pygame.quit()

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    export_all_maps()