import pygame
import random

from states.base_state import BaseState
from states.gameover_state import GameOverState
from utils.helpers import key_event_match
from utils.world_loader import WorldLoader
from UI.hud import HUD
from entities.tank import Tank
from entities.tree import Tree
from systems.control_builder import build_controls
from systems.combat_system import update_bullets, update_powerups
from systems.safe_spawn import get_safe_spawn
from systems.ai_controller import TankAI
from constants import TILE_SIZE, COLORS, POWERUP_SPAWN_INTERVAL, TURRET_OFFSETS

class CoopState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.reset()
        self.hud = HUD(game)
        self.powerup_spawn_timer = 10
        self.powerup_spawn_interval = POWERUP_SPAWN_INTERVAL
        self.alive = True
        self.exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 1.0

    # ==========================================
    # RESET
    # ==========================================
    def reset(self):
        # Trees
        self.trees = WorldLoader.spawn_objects_from_map(
            self.game.level_map,
            self.game.TREE_IMG
        )

        # =================
        # PLAYERS
        # =================
        self.players = []

        style1 = self.game.player_styles[1]
        self.players.append(
            Tank(
                pos=get_safe_spawn(
                    self.trees,
                    self.game.screen.get_rect(),
                    TILE_SIZE,
                    self.game.level_map,
                    [p.pos for p in self.players],
                    6 * TILE_SIZE
                ),
                controls=build_controls(self.game.config, 1),
                name="Player 1",
                color=style1["color"],
                turret_offset=TURRET_OFFSETS[style1["hull"]],
                images={
                    "hull": self.game.TANK_HULLS[style1["hull"]],
                    "gun": self.game.TANK_GUNS[style1["gun"]],
                },
                tile_size=TILE_SIZE,
                level_map=self.game.level_map,
                bounds_rect=self.game.screen.get_rect(),
                game=self.game,
                start_angle=180
            )
        )

        style2 = self.game.player_styles[2]
        self.players.append(
            Tank(
                pos=get_safe_spawn(
                    self.trees,
                    self.game.screen.get_rect(),
                    TILE_SIZE,
                    self.game.level_map,
                    [p.pos for p in self.players],
                    6 * TILE_SIZE
                ),
                controls=build_controls(self.game.config, 2),
                name="Player 2",
                color=style2["color"],
                turret_offset=TURRET_OFFSETS[style2["hull"]],
                images={
                    "hull": self.game.TANK_HULLS[style2["hull"]],
                    "gun": self.game.TANK_GUNS[style2["gun"]],
                },
                tile_size=TILE_SIZE,
                level_map=self.game.level_map,
                bounds_rect=self.game.screen.get_rect(),
                game=self.game
            )
        )

        # =================
        # ENEMIES
        # =================
        self.enemies = []

        for i in range(2):
            enemy_style = {
                "hull": random.randint(0, len(self.game.TANK_HULLS)-1),
                "gun": random.randint(0, len(self.game.TANK_GUNS)-1)
            }
            enemy = Tank(
                pos=get_safe_spawn(
                    self.trees,
                    self.game.screen.get_rect(),
                    TILE_SIZE,
                    self.game.level_map,
                    [p.pos for p in self.players],
                    6 * TILE_SIZE
                ),
                controls=None,
                name=f"Enemy{i}",
                color=COLORS.RED,
                turret_offset=TURRET_OFFSETS[enemy_style["hull"]],
                images={
                    "hull": self.game.TANK_HULLS[enemy_style["hull"]],
                    "gun": self.game.TANK_GUNS[enemy_style["gun"]],
                },
                tile_size=TILE_SIZE,
                level_map=self.game.level_map,
                bounds_rect=self.game.screen.get_rect(),
                game=self.game
            )

            self.enemies.append(enemy)

        # Combine
        self.tanks = [*self.players, *self.enemies]

        # AI
        self.enemy_ai = [
            TankAI(enemy, self.players, self.trees)
            for enemy in self.enemies
        ]

        self.bullets = []
        self.powerups = []

    # ==========================================
    # EVENTS
    # ==========================================
    def handle_events(self, events):
        for event in events:
            self.game.debug.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from states.start_state import StartState
                    self.game.change_state(StartState(self.game))

                # ===== TAKE CONTROL FROM CONFIG =====
                p1_controls = self.game.config.get_controls(1)
                p2_controls = self.game.config.get_controls(2)

                # ===== PLAYER FIRE =====
                if key_event_match(event.key, p1_controls["fire"]):
                    bullet = self.players[0].shoot(self.game.BULLET_IMG)
                    if bullet:
                        self.bullets.extend(bullet)
                        self.game.audio.play_sfx("fire.mp3")

                if key_event_match(event.key, p2_controls["fire"]):
                    bullet = self.players[1].shoot(self.game.BULLET_IMG)
                    if bullet:
                        self.bullets.extend(bullet)
                        self.game.audio.play_sfx("fire.mp3")

    # ==========================================
    # UPDATE
    # ==========================================
    def update(self, dt):
        keys = pygame.key.get_pressed()
        for player in self.players:
            player.update(dt, keys, 180, self.trees)
        for enemy in self.enemies:
            enemy.update(dt, None, 180, self.trees)
        for ai in self.enemy_ai:
            if ai.tank.alive:
                ai.update(dt)

        # Bullets
        update_bullets(
            self.game,
            self.bullets,
            self.tanks,
            self.trees,
            dt
        )

        # Powerups
        self.powerup_spawn_timer = update_powerups(
            self.game,
            self.powerups,
            self.tanks,
            dt,
            self.powerup_spawn_timer,
            self.powerup_spawn_interval
        )

        if all(not p.alive for p in self.players):
            self.game.winner = "ENEMY"
            self.game.change_state(GameOverState(self.game))

        if all(not e.alive for e in self.enemies):
            self.game.winner = "PLAYERS"
            self.game.change_state(GameOverState(self.game))

    # ==========================================
    # DRAW
    # ==========================================
    def draw(self, surface):
        # draw tile map
        self.game.tile_map.draw(surface)
        self.hud.draw_arcade_health_ui(surface, self.players)
        self.hud.draw_control_hints(surface, [1,2])

        # draw entities
        for tree in self.trees:
            tree.draw(surface)
        for bullet in self.bullets:
            bullet.draw(surface)
        for tank in self.tanks:
            tank.draw(surface)
        for powerup in self.powerups:
            powerup.draw(surface)
        
        # Debug mode
        self.game.debug.draw_hitboxes(
            surface,
            tanks=self.tanks,
            bullets=self.bullets,
            trees=self.trees
        )
        self.game.debug.draw_fps(surface, self.game.clock)