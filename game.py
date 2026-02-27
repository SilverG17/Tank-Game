import pygame
import os

from config import Config
from systems.input_handler import InputHandler
from systems.audio_manager import AudioManager
from systems.collision import CollisionSystem
from systems.particle_system import ParticleSystem
from states.start_state import StartState
from utils.asset_loader import AssetLoader
from constants import TILE_SIZE
from systems.tile_map import TileMap

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

        # ==============================
        # Core systems
        # ==============================
        self.config = Config()
        self.input = InputHandler()
        self.audio = AudioManager()
        self.collision = CollisionSystem()
        self.particles = ParticleSystem()

        # ==============================
        # Assets
        # ==============================
        self.assets = AssetLoader("image")
        self.HULL_IMG = self.assets.load_image(
            "hull_01.png",
            scale=(TILE_SIZE, TILE_SIZE)
        )
        self.GUN_IMG = self.assets.load_image(
            "gun_01.png",
            scale=(TILE_SIZE, TILE_SIZE)
        )
        self.TREE_IMG = self.assets.load_image(
            "tree.png",
            scale=(TILE_SIZE, TILE_SIZE)
        )
        self.BULLET_IMG = self.assets.load_image(
            "bullet.png",
            scale=(TILE_SIZE , TILE_SIZE)
        )
        self.POWERUP_IMG = {
            "SPEED": self.assets.load_image("speed.png", scale=(64, 64)),
            "SHIELD": self.assets.load_image("shield.png", scale=(64, 64)),
            "TRIPLE": self.assets.load_image("triple.png", scale=(64, 64)),
        }
        self.COIN_IMG = self.assets.load_image("coin.png", scale=(32, 32))
        self.CONFIG_IMG = self.assets.load_image("settings_icon.png", scale=(64, 64))

        # ==============================
        # Map system
        # ==============================
        self.map_files = self.load_all_maps("maps")
        self.selected_map_index = 0

        # load map đầu tiên
        self.level_map = self.load_map(self.map_files[self.selected_map_index])
        self.tile_map = TileMap(self)
        self.map_previews = []
        for path in self.map_files:
            map_name = os.path.basename(path).replace(".txt", "")
            try:
                img = self.assets.load_image(
                    f"{map_name}.png",   
                    scale=(400, 250)
                )
            except Exception:
                img = None 
            self.map_previews.append(img)

        # ==============================
        # Fonts
        # ==============================
        self.font_title = pygame.font.SysFont("Impact", 100)
        self.font_big = pygame.font.SysFont("Impact", 30)
        self.font_main = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("arial", 16, bold=True)

        # ==============================
        # Initial State
        # ==============================
        self.state = StartState(self)

        # ==============================
        # Load sounds
        # ==============================
        self.audio.load_sfx("fire.mp3", 0.6)
        self.audio.load_sfx("hit.mp3", 0.7)
        self.audio.load_sfx("coin.mp3", 0.6)
        self.audio.load_sfx("bounce.mp3", 0.4)
        self.audio.load_sfx("nop.mp3", 0.6)
        self.audio.load_music("bg_music.mp3", volume=0.2, loop=True)
        self.audio.set_music_volume(self.config.get_music_volume())
        self.audio.set_sfx_volume(self.config.get_sfx_volume())

    # ==================================
    # Change state
    # ==================================
    def change_state(self, new_state):
        self.state = new_state

    # ==================================
    # Load map 
    # ==================================
    def load_map(self, path):
        with open(path, "r") as f:
            return [list(line.strip()) for line in f]

    # ==================================
    # Update
    # ==================================
    def update(self, dt):
        self.state.update(dt)
        self.particles.update(dt)

    # ==================================
    # Draw
    # ==================================
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.state.draw(self.screen)
        self.particles.draw(self.screen)

    def load_all_maps(self, folder):
        files = []
        for file in os.listdir(folder):
            if file.endswith(".txt"):
                files.append(os.path.join(folder, file))
        files.sort() 
        return files