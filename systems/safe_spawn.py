import pygame
import random


def too_close(pos, players, min_dist):
    pos_vec = pygame.Vector2(pos)

    for p in players:
        p_vec = pygame.Vector2(p)
        if pos_vec.distance_to(p_vec) < min_dist:
            return True

    return False


def get_safe_spawn(trees, bounds_rect, tile_size, level_map, players=None, min_player_dist=0):

    map_h = len(level_map)
    map_w = len(level_map[0])

    while True:

        gx = random.randint(1, map_w - 2)
        gy = random.randint(1, map_h - 2)

        x = gx * tile_size + tile_size // 2
        y = gy * tile_size + tile_size // 2

        spawn_rect = pygame.Rect(
            x - tile_size // 2,
            y - tile_size // 2,
            tile_size,
            tile_size
        )

        # Avoid rock tiles
        if level_map[gy][gx] == "B":
            continue

        blocked = False

        # Avoid trees
        for tree in trees:
            if spawn_rect.colliderect(tree.rect):
                blocked = True
                break

        if blocked:
            continue

        # Avoid players
        if players and too_close((x, y), players, min_player_dist):
            continue

        return (x, y)