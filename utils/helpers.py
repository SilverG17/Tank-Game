import math
import pygame

# ==========================================
# MATH HELPERS
# ==========================================
def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def lerp(a, b, t):
    return a + (b - a) * t

def distance(pos1, pos2):
    return pygame.Vector2(pos1).distance_to(pos2)

def angle_to_vector(angle_degrees):
    rad = math.radians(angle_degrees)
    return pygame.Vector2(math.cos(rad), -math.sin(rad))

def vector_to_angle(vector):
    return math.degrees(math.atan2(-vector.y, vector.x))

# ==========================================
# GRID HELPERS
# ==========================================
def grid_to_world(gx, gy, tile_size):
    return pygame.Vector2(gx * tile_size, gy * tile_size)

def world_to_grid(x, y, tile_size):
    return int(x // tile_size), int(y // tile_size)

# ==========================================
# INPUT HELPERS
# ==========================================
def key_pressed(keys, bind):
    """
    Check if a key binding is pressed.
    Supports:
        int  -> single key
        list -> multiple keys
    """
    if isinstance(bind, list):
        return any(keys[k] for k in bind)
    return keys[bind]


def key_event_match(event_key, bind):
    """
    Check if a KEYDOWN event matches a binding.
    Works with int or list.
    """
    if isinstance(bind, list):
        return event_key in bind
    return event_key == bind