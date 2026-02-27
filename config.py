import json
import os
import copy
import pygame

class Config:

    DEFAULT_CONFIG = {
        "controls": {
            "player1": {
                "up": pygame.K_w,
                "down": pygame.K_s,
                "left": pygame.K_a,
                "right": pygame.K_d,
                "gun_left": pygame.K_q,
                "gun_right": pygame.K_e,
                "fire": [pygame.K_SPACE]
            },
            "player2": {
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "gun_left": pygame.K_o,
                "gun_right": pygame.K_p,
                "fire": [pygame.K_m]
            }
        },
        "audio": {
            "music_volume": 0.2,
            "sfx_volume": 0.6,
            "bounce_volume": 0.4,
            "master_mute": False
        },
        "gameplay": {
            "p1_sensitivity": 200,
            "p2_sensitivity": 200,
            "max_bullets": 5,
            "cooldown_time": 0.2
        }
    }

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.data = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                print("Error loading config, using defaults")
        return copy.deepcopy(self.DEFAULT_CONFIG)

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    # -------------------------
    # Key Helpers
    # -------------------------
    def key_to_string(self, key):
        return pygame.key.name(key)

    def key_list_to_string(self, keys):
        return ", ".join(pygame.key.name(k).upper() for k in keys)

    # -------------------------
    # Controls
    # -------------------------
    def get_controls(self, player):
        return self.data["controls"][f"player{player}"]

    # -------------------------
    # Audio
    # -------------------------
    def get_music_volume(self):
        return self.data["audio"]["music_volume"]

    def get_sfx_volume(self):
        return self.data["audio"]["sfx_volume"]

    # -------------------------
    # Gameplay
    # -------------------------
    def get_sensitivity(self, player):
        return self.data["gameplay"][f"p{player}_sensitivity"]

    def set_sensitivity(self, player, value):
        self.data["gameplay"][f"p{player}_sensitivity"] = max(50, min(500, value))
        self.save_config()

    def key_from_string(self, key_name):
        return pygame.key.key_code(key_name)