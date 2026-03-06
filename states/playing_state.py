import pygame

from states.base_state import BaseState
from states.gameover_state import GameOverState
from utils.helpers import key_event_match
from UI.hud import HUD
from entities.tank import Tank
from entities.tree import Tree
from entities.powerup import PowerUp
from entities.coin import Coin
from constants import TILE_SIZE, COLORS, SCORE_LIMIT, POWERUP_SPAWN_INTERVAL


class PlayingState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.reset()
        self.debug_mode = False
        self.hud = HUD(game)
        self.powerup_spawn_timer = 5
        self.powerup_spawn_interval = POWERUP_SPAWN_INTERVAL
        self.alive = True
        self.exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 1.0

    def build_controls(self, player):
        raw_controls = self.game.config.get_controls(player)
        return {
            "up": raw_controls["up"],
            "down": raw_controls["down"],
            "left": raw_controls["left"],
            "right": raw_controls["right"],
            "gun_left": raw_controls["gun_left"],
            "gun_right": raw_controls["gun_right"],
            "fire": raw_controls["fire"],
        }
    
    # ==========================================
    # RESET
    # ==========================================
    def reset(self):
        self.tanks = []

        # Player 1
        self.tanks.append(
            Tank(
                pos=(1.5 * TILE_SIZE, 1.5 * TILE_SIZE),
                controls=self.build_controls(1),
                color=self.game.p1_color,
                name="Player 1",
                hull_style = self.game.p1_hull_style,
                gun_style = self.game.p1_gun_style,
                images={
                    "hull": self.game.TANK_HULLS[self.game.p1_hull_style],
                    "gun": self.game.TANK_GUNS[self.game.p1_gun_style]
                },
                tile_size=TILE_SIZE,
                level_map=self.game.level_map,
                bounds_rect=self.game.screen.get_rect(),
                game=self.game,
                start_angle=180
            )
        )

        # Player 2
        self.tanks.append(
            Tank(
                pos=(16.5 * TILE_SIZE, 10.5 * TILE_SIZE),
                controls=self.build_controls(2),
                color=self.game.p2_color,
                name="Player 2",
                hull_style = self.game.p2_hull_style,
                gun_style = self.game.p2_gun_style,
                images={
                    "hull": self.game.TANK_HULLS[self.game.p2_hull_style],
                    "gun": self.game.TANK_GUNS[self.game.p2_gun_style]
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
        self.spawn_objects_from_map()
        self.game.audio.play_sfx("nop.mp3")

    # ==========================================
    # WORLD SETUP
    # ==========================================
    def spawn_objects_from_map(self):
        for row_index, row in enumerate(self.game.level_map):
            for col_index, char in enumerate(row):
                if char == 'T':
                    self.trees.append(
                        Tree(
                            col_index,
                            row_index,
                            TILE_SIZE,
                            self.game.TREE_IMG
                        )
                    )

    # ==========================================
    # EVENTS
    # ==========================================
    def handle_events(self, events):
        for event in events:
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
                if event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode

    # ==========================================
    # UPDATE
    # ==========================================
    def update(self, dt):
        keys = pygame.key.get_pressed()
        for tank in self.tanks:
            tank.update(
                dt,
                keys,
                sensitivity=180,
                trees=self.trees
            )

        # ===== Update bullets =====
        for bullet in self.bullets[:]:
            bullet.update(
                dt,
                self.game.level_map,
                TILE_SIZE,
                self.game.screen.get_rect()
            )

            # Remove if inactive
            if not bullet.active:
                self.bullets.remove(bullet)
                continue

            # ==== Bullet vs Tank =====
            for tank in self.tanks:
                if tank != bullet.owner:
                    if bullet.get_hitbox().colliderect(tank.get_hitbox()):
                        if not tank.has_shield:
                            tank.take_damage(10)

                            # thưởng điểm cho người bắn (nếu muốn)
                            bullet.owner.point += 15
                        self.bullets.remove(bullet)
                        break

            # ===== Bullet vs Tree =====
            for tree in self.trees[:]:
                if bullet.get_hitbox().colliderect(tree.get_hitbox()):
                    self.game.audio.play_sfx("hit.mp3")

                    if tree.take_damage():
                        self.trees.remove(tree)
                        self.game.level_map[tree.gy][tree.gx] = 'g'

                    self.bullets.remove(bullet)
                    break
        self.powerup_spawn_timer += dt
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.spawn_powerup()
            self.powerup_spawn_timer = 0
        for powerup in self.powerups[:]:
            for tank in self.tanks:
                if tank.get_hitbox().colliderect(powerup.rect):
                    self.game.audio.play_sfx("coin.mp3")
                    if powerup.type == "SPEED":
                        tank.speed_boost = 1.8
                        tank.powerup_timers["SPEED"] = powerup.duration
                    elif powerup.type == "SHIELD":
                        tank.has_shield = True
                        tank.powerup_timers["SHIELD"] = powerup.duration
                    elif powerup.type == "TRIPLE":
                        tank.powerup_timers["TRIPLE"] = powerup.duration
                    self.powerups.remove(powerup)
                    break
        self.coin_spawn_timer += dt
        if self.coin_spawn_timer >= self.coin_spawn_interval:
            self.spawn_coin()
            self.coin_spawn_timer = 0
        for coin in self.coins[:]:
            for tank in self.tanks:
                if tank.rect.colliderect(coin.rect):
                    tank.point += 20
                    self.coins.remove(coin)
                    self.game.audio.play_sfx("coin.mp3")
                    break
        for tank in self.tanks:
            if tank.exploding:
                tank.explosion_timer += dt

        # ===== Game Over (HP) =====
        p1 = self.tanks[0]
        p2 = self.tanks[1]

        if p1.health <= 0 and p1.alive:
            p1.alive = False
            p1.exploding = True
            p1.explosion_timer = 0
            self.game.audio.play_sfx("explosion.mp3")

        if p2.health <= 0 and p2.alive:
            p2.alive = False
            p2.exploding = True
            p2.explosion_timer = 0
            self.game.audio.play_sfx("explosion.mp3")

        if not p1.alive and p1.explosion_timer >= p1.explosion_duration:
            self.game.winner = "Player 2"
            self.game.change_state(GameOverState(self.game))
            return

        if not p2.alive and p2.explosion_timer >= p2.explosion_duration:
            self.game.winner = "Player 1"
            self.game.change_state(GameOverState(self.game))
            return

        # ===== Game Over (Score) =====
        if p1.point >= SCORE_LIMIT:
            self.game.winner = "Player 1"
            self.game.change_state(GameOverState(self.game))
            return

        if p2.point >= SCORE_LIMIT:
            self.game.winner = "Player 2"
            self.game.change_state(GameOverState(self.game))
            return

    # ==========================================
    # Spawn
    # ==========================================
    def spawn_powerup(self):
        powerup = PowerUp(
            tile_size=TILE_SIZE,
            level_map=self.game.level_map,
            images=self.game.POWERUP_IMG
        )
        self.powerups.append(powerup)

    def spawn_coin(self):
        coin = Coin(
            tile_size=TILE_SIZE,
            level_map=self.game.level_map,
            image=self.game.COIN_IMG
        )
        self.coins.append(coin)

    # ==========================================
    # DRAW
    # ==========================================
    def draw(self, surface):
        # draw tile map
        self.game.tile_map.draw(surface)
        self.hud.draw_arcade_health_ui(surface, self.tanks)
        self.hud.draw_control_hints(surface)

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
        if self.debug_mode:
            for tank in self.tanks:
                pygame.draw.rect(surface, COLORS.GREEN, tank.get_hitbox(), 2)
            for tree in self.trees:
                pygame.draw.rect(surface, COLORS.RED, tree.get_hitbox(), 2)
            for bullet in self.bullets:
                pygame.draw.rect(surface, COLORS.YELLOW, bullet.get_hitbox(), 2)