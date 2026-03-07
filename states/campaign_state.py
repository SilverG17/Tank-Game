import pygame
import random

from states.base_state import BaseState
from states.gameover_state import GameOverState
from utils.helpers import key_event_match
from utils.world_loader import WorldLoader
from UI.hud import HUD
from entities.tank import Tank
from entities.tree import Tree
from entities.boss_tank import BossTank
from systems.control_builder import build_controls
from systems.combat_system import update_bullets, update_powerups
from systems.safe_spawn import get_safe_spawn
from systems.ai_controller import TankAI
from constants import TILE_SIZE, COLORS, POWERUP_SPAWN_INTERVAL, TURRET_OFFSETS


class CampaignState(BaseState):
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
        self.boss_spawned = False
        self.boss = None
        self.boss_death_shake = False
        self.boss_death_timer = 0
        self.boss_death_delay = 2.5
        self.boss_dying = False
        self.boss_death_started = False
    
    # ==========================================
    # RESET
    # ==========================================
    def reset(self):
        self.trees = WorldLoader.spawn_objects_from_map(
            self.game.level_map,
            self.game.TREE_IMG
        )

        # =========================
        # Player
        # =========================
        style1 = self.game.player_styles[1]
        self.player = Tank(
                pos=(1.5 * TILE_SIZE, 1.5 * TILE_SIZE),
                controls=build_controls(self.game.config, 1),
                name="Player",
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

        # =========================
        # Enemy
        # =========================
        self.enemies = []
        for i in range(self.game.enemy_count):
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
                    self.player.pos,
                    6 * TILE_SIZE),
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

        self.bullets = []
        self.point = 0
        self.powerups = []
        self.game.audio.play_sfx("nop.mp3")
        self.enemy_ai = []
        for enemy in self.enemies:
            self.enemy_ai.append(TankAI(enemy, [self.player], self.trees))
        self.tanks = [self.player] + self.enemies

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

                # ===== PLAYER FIRE =====
                if key_event_match(event.key, p1_controls["fire"]):
                    bullet = self.player.shoot(self.game.BULLET_IMG)
                    if bullet:
                        self.bullets.extend(bullet)
                        self.game.audio.play_sfx("fire.mp3")

    # ==========================================
    # UPDATE
    # ==========================================
    def update(self, dt):
        keys = pygame.key.get_pressed()

        # Player update
        self.player.update(dt, keys, sensitivity=180, trees=self.trees)

        # Update enemy tanks
        for enemy in self.enemies:
            enemy.update(dt, None, 180, self.trees)

        # Update boss
        if self.boss_spawned and self.boss:
            if self.boss_dying:
                self.boss.vel = pygame.Vector2(0, 0)
                self.boss.update(dt, None, 180, self.trees)

            else:
                self.boss.update(dt, None, 180, self.trees)

        # AI controls alive enemies
        for ai in self.enemy_ai:
            if ai.enabled and ai.tank.alive:
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

        # Player died
        if not self.player.alive and self.player.explosion_timer >= self.player.explosion_duration:
            self.game.winner = "ENEMY"
            self.game.change_state(GameOverState(self.game))

        # All small enemies defeated
        if (not self.boss_spawned and
            all((not e.alive) and (e.explosion_timer >= e.explosion_duration) for e in self.enemies)):
            self.game.audio.stop_music()
            self.game.audio.load_music("boss_spawn.mp3", volume=0.20)
            self.spawn_boss()

        # Boss crush trees while moving 
        if self.boss_spawned and self.boss and self.boss.alive:
            for tree in self.trees[:]:
                if self.boss.pos.distance_to(tree.pos) < 70:
                    self.trees.remove(tree)

        # Boss defeated
        if self.boss_spawned and self.boss:
            # Detect boss death
            if self.boss.health <= 0 and not self.boss_death_started:
                self.game.audio.stop_music()
                self.game.audio.load_music ("Victory.mp3", volume=0.20)
                self.boss_death_started = True
                self.boss_dying = True
                self.boss_death_timer = 0

                # keep boss alive for flashing
                self.boss.health = 1

                # cancel automatic explosion
                self.boss.exploding = False
                self.boss.explosion_timer = 0
                self.boss.explosion_frame = 0

                for ai in self.enemy_ai:
                    if ai.tank == self.boss:
                        ai.enabled = False

                self.boss.vel = pygame.Vector2(0, 0)

                self.game.camera.shake(18, 0.6)

            # Countdown phase
            if self.boss_dying:
                self.boss_death_timer += dt

                # freeze boss movement
                self.boss.vel = pygame.Vector2(0, 0)

                if self.boss_death_timer >= self.boss_death_delay:
                    # trigger explosion animation
                    self.game.camera.shake(18, 0.6)
                    self.boss.alive = False
                    self.boss.exploding = True
                    self.boss.explosion_timer = 0
                    self.boss_dying = False  # Exit dying state

            # Wait explosion animation finish
            if (not self.boss.alive and
                self.boss.explosion_timer >= self.boss.explosion_duration):
                self.game.winner = "PLAYER"
                self.game.change_state(GameOverState(self.game))


    # ==========================================
    # Spawn Boss
    # ==========================================
    def spawn_boss(self):

        self.boss_spawned = True

        boss_style = {
            "hull": random.randint(0, len(self.game.TANK_HULLS)-1),
            "gun": random.randint(0, len(self.game.TANK_GUNS)-1)
        }

        self.boss = BossTank(
            pos=get_safe_spawn(
                self.trees,
                self.game.screen.get_rect(),
                TILE_SIZE,
                self.game.level_map,
                self.player.pos,
                8 * TILE_SIZE
            ),
            controls=None,
            name="BOSS",
            color=COLORS.GRAY,
            turret_offset=TURRET_OFFSETS[boss_style["hull"]],
            images={
                "hull": self.game.TANK_HULLS[boss_style["hull"]],
                "gun": self.game.TANK_GUNS[boss_style["gun"]],
            },
            tile_size=TILE_SIZE, 
            level_map=self.game.level_map,
            bounds_rect=self.game.screen.get_rect(),
            game=self.game,
            scale=0.7
        )

        # Add boss to systems
        self.tanks.append(self.boss)

        self.enemy_ai.append(
            TankAI(self.boss, [self.player], self.trees)
        )

    # ==========================================
    # DRAW
    # ==========================================
    def draw(self, surface):
        offset = self.game.camera.get_offset()

        # draw everything normally
        temp_surface = pygame.Surface(surface.get_size())

        self.game.tile_map.draw(temp_surface)
        self.hud.draw_arcade_health_ui(temp_surface, self.tanks)
        self.hud.draw_control_hints(temp_surface, [1])

        for tree in self.trees:
            tree.draw(temp_surface)

        for bullet in self.bullets:
            bullet.draw(temp_surface)

        for tank in self.tanks:
            tank.draw(temp_surface)

        for powerup in self.powerups:
            powerup.draw(temp_surface)

        self.game.debug.draw_hitboxes(
            temp_surface,
            tanks=self.tanks,
            bullets=self.bullets,
            trees=self.trees
        )

        self.game.debug.draw_fps(temp_surface, self.game.clock)

        # apply camera shake
        surface.blit(temp_surface, offset)