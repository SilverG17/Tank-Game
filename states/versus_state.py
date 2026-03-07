import pygame

from states.base_state import BaseState
from states.gameover_state import GameOverState
from utils.helpers import key_event_match
from utils.world_loader import WorldLoader
from UI.hud import HUD
from entities.tank import Tank
from entities.tree import Tree
from systems.control_builder import build_controls
from systems.combat_system import update_bullets, update_coins, update_powerups, check_game_over
from constants import TILE_SIZE, COLORS, POWERUP_SPAWN_INTERVAL, TURRET_OFFSETS


class VersusState(BaseState):
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
        self.tanks = []

        # =========================
        # Player 1 style
        # =========================
        style1 = self.game.player_styles[1]
        self.tanks.append(
            Tank(
                pos=(1.5 * TILE_SIZE, 1.5 * TILE_SIZE),
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

        # =========================
        # Player 2 style
        # =========================
        style2 = self.game.player_styles[2]
        self.tanks.append(
            Tank(
                pos=(16.5 * TILE_SIZE, 10.5 * TILE_SIZE),
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

        self.bullets = []
        self.trees = []
        self.point = 0
        self.powerups = []
        self.coins = []
        self.coin_spawn_timer = 0
        self.coin_spawn_interval = 4
        self.game.audio.play_sfx("nop.mp3")
        self.trees = WorldLoader.spawn_objects_from_map(
            self.game.level_map,
            self.game.TREE_IMG
        )

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

                # ===== LẤY CONTROLS TỪ CONFIG =====
                p1_controls = self.game.config.get_controls(1)
                p2_controls = self.game.config.get_controls(2)

                # ===== PLAYER 1 FIRE =====
                if key_event_match(event.key, p1_controls["fire"]):
                    bullet = self.tanks[0].shoot(self.game.BULLET_IMG)
                    if bullet:
                        self.bullets.extend(bullet)
                        self.game.audio.play_sfx("fire.mp3")

                # ===== PLAYER 2 FIRE =====
                if key_event_match(event.key, p2_controls["fire"]):
                    bullet = self.tanks[1].shoot(self.game.BULLET_IMG)
                    if bullet:
                        self.bullets.extend(bullet)
                        self.game.audio.play_sfx("fire.mp3")

    # ==========================================
    # UPDATE
    # ==========================================
    def update(self, dt):
        keys = pygame.key.get_pressed()

        # ===== Update bullets =====
        for tank in self.tanks:
            tank.update(dt, keys, sensitivity=180, trees=self.trees)

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

        # Coins
        self.coin_spawn_timer = update_coins(
            self.game,
            self.coins,
            self.tanks,
            dt,
            self.coin_spawn_timer,
            self.coin_spawn_interval
        )

        check_game_over(self.game, self.tanks)

    # ==========================================
    # DRAW
    # ==========================================
    def draw(self, surface):
        # draw tile map
        self.game.tile_map.draw(surface)
        self.hud.draw_arcade_health_ui(surface, self.tanks)
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
        for coin in self.coins:
            coin.draw(surface)
        
        # Debug mode
        self.game.debug.draw_hitboxes(
            surface,
            tanks=self.tanks,
            bullets=self.bullets,
            trees=self.trees
        )
        self.game.debug.draw_fps(surface, self.game.clock)