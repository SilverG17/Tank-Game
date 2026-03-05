import pygame
import os

from config import Config
from systems.input_handler import InputHandler
from systems.audio_manager import AudioManager
from systems.collision import CollisionSystem
from systems.particle_system import ParticleSystem
from states.start_state import StartState
from utils.asset_loader import AssetLoader
from constants import TILE_SIZE, WIDTH, HEIGHT
from systems.tile_map import TileMap

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

        # ==============================
        # Core systems
        # ==============================
        self.config = Config()
        self.create_window()
        self.input = InputHandler()
        self.audio = AudioManager()
        self.collision = CollisionSystem()
        self.particles = ParticleSystem()
        self.render_surface = pygame.Surface((WIDTH, HEIGHT))
        self.player_styles = {
            1: {"hull": 0, "gun": 0, "color": 0},
            2: {"hull": 0, "gun": 0, "color": 0},
        }

        # ==============================
        # Assets
        # ==============================
        self.assets = AssetLoader()

        # Load Background
        self.SETTINGS_BG = self.assets.load_image(
            "Background/Setting_bg.png"
        )
        self.MAIN_BG = self.assets.load_image(
            "Background/Main_bg.png"
        )
        self.SELECT_BG = self.assets.load_image(
            "Background/Select_bg.png" 
        )
        self.GAMEOVER_BG = self.assets.load_image(
            "Background/GameOver_bg.png"
        )

        # Load all tank sprites
        self.TANK_HULLS = []
        self.TANK_GUNS = []
        for i in range(1, 9):
            hull = self.assets.load_image(
                f"Tank/hull_{i:02}.png",
                scale=(TILE_SIZE, TILE_SIZE)
            )
            gun = self.assets.load_image(
                f"Tank/gun_{i:02}.png",
                scale=(TILE_SIZE * 0.6, TILE_SIZE * 0.6)
            )
            self.TANK_HULLS.append(hull)
            self.TANK_GUNS.append(gun)

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
            "TRIPLE": self.assets.load_image("triple.png", scale=(32, 32)),
        }
        self.COIN_IMG = self.assets.load_image("coin.png", scale=(32, 32))
        self.CONFIG_IMG = self.assets.load_image("settings_icon.png", scale=(64, 64))

        # ==============================
        # Map system
        # ==============================
        self.map_files = self.load_all_maps("maps")
        self.selected_map_index = 0

        self.RANDOM_PREVIEW = self.assets.load_image(
            "random_preview.png",
            scale=(400, 250)
        )

        # load first map by default
        self.level_map = self.load_map(self.map_files[self.selected_map_index])
        self.tile_map = TileMap(self)
        self.map_previews = []
        for path in self.map_files:
            map_name = os.path.basename(path).replace(".txt", "")
            try:
                img = self.assets.load_image(
                    f"Maps/{map_name}.png",   
                    scale=(400, 250)
                )
            except FileNotFoundError:
                img = None 
            self.map_previews.append(img)

        # ==============================
        # Explosion animation
        # ==============================
        self.EXPLOSION_FRAMES = []

        for letter in "ABCDEFGH":
            img = self.assets.load_image(
                f"Explosion/Explosion_{letter}.png",
                scale=(96, 96)
            )
            self.EXPLOSION_FRAMES.append(img)

        # ==============================
        # Fonts
        # ==============================
        self.font_title = pygame.font.SysFont("Impact", 100)
        self.font_big = pygame.font.SysFont("Impact", 30)
        self.font_main = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16, bold=True)

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
        self.audio.load_sfx("explosion.mp3", 0.6)
        self.music_main = "bg_music.mp3"
        self.music_gameover = "GameOver.mp3"
        self.audio.load_music(self.music_main, volume=0.2, loop=True)
        self.audio.set_music_volume(self.config.get_music_volume())
        self.audio.set_sfx_volume(self.config.get_sfx_volume())

    # ==================================
    # Create / recreate window
    # ==================================
    def create_window(self):

        width, height = self.config.get_resolution()

        flags = 0
        if self.config.is_fullscreen():
            flags = pygame.FULLSCREEN

        self.screen = pygame.display.set_mode((width, height), flags)

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
        self.render_surface.fill((0, 0, 0))
        self.state.draw(self.render_surface)
        self.particles.draw(self.render_surface)
        scaled = pygame.transform.smoothscale(
            self.render_surface,
            self.screen.get_size()
        )
        self.screen.blit(scaled, (0, 0))

    def load_all_maps(self, folder):
        files = []
        for file in sorted(os.listdir(folder)):
            if file.endswith(".txt"):
                files.append(os.path.join(folder, file))
        return files