import pygame
import os

class AudioManager:
    def __init__(self, base_path="sound"):
        self.base_path = base_path

        self.sounds = {}  # name: {sound, base_volume}
        self.sfx_volume = 1.0
        self.music_volume = 0.5
        self.music_loaded = False

        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()

    # ==========================================
    # LOAD SOUND EFFECT
    # ==========================================
    def load_sfx(self, name, volume=1.0):

        if name in self.sounds:
            return self.sounds[name]["sound"]

        path = os.path.join(self.base_path, name)

        if not os.path.exists(path):
            print(f"[AudioManager] Missing sound: {path}")
            return None

        try:
            sound = pygame.mixer.Sound(path)

            self.sounds[name] = {
                "sound": sound,
                "base_volume": volume
            }

            # apply global volume
            sound.set_volume(volume * self.sfx_volume)

            return sound

        except Exception as e:
            print(f"[AudioManager] Error loading {path}: {e}")
            return None
        
    # ==========================================
    # PLAY SOUND EFFECT
    # ==========================================
    def play_sfx(self, name):
        if name not in self.sounds:
            self.load_sfx(name)

        data = self.sounds.get(name)
        if data:
            data["sound"].play()

    # ==========================================
    # GLOBAL SFX VOLUME
    # ==========================================
    def set_sfx_volume(self, volume):
        self.sfx_volume = volume

        for data in self.sounds.values():
            data["sound"].set_volume(
                data["base_volume"] * self.sfx_volume
            )

    # ==========================================
    # MUSIC
    # ==========================================
    def load_music(self, name, volume=0.5, loop=True):
        path = os.path.join(self.base_path, name)

        if not os.path.exists(path):
            print(f"[AudioManager] Missing music: {path}")
            return

        pygame.mixer.music.load(path)
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
        self.music_loaded = True

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)