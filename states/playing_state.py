import pygame

from states.base_state import BaseState
from states.gameover_state import GameOverState
from entities.tank import Tank
from entities.tree import Tree
from entities.powerup import PowerUp
from entities.coin import Coin
from constants import TILE_SIZE, Color, SCORE_LIMIT


class PlayingState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.reset()
        self.debug_mode = False
        self.powerup_spawn_timer = 5
        self.powerup_spawn_interval = 5

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
                color=(0, 200, 0),
                name="Player 1",
                images={
                    "hull": self.game.HULL_IMG,
                    "gun": self.game.GUN_IMG
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
                color=(200, 0, 0),
                name="Player 2",
                images={
                    "hull": self.game.HULL_IMG,
                    "gun": self.game.GUN_IMG
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
                if event.key in p1_controls["fire"]:
                    bullet = self.tanks[0].shoot(self.game.BULLET_IMG)
                    if bullet:
                        self.bullets.extend(bullet)
                        self.game.audio.play_sfx("fire.mp3")

                # ===== PLAYER 2 FIRE =====
                if event.key in p2_controls["fire"]:
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
                    if bullet.get_hitbox().colliderect(tank.rect):
                        if not tank.has_shield:
                            tank.health -= 10
                            tank.flash_timer = 0.3

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
                if tank.rect.colliderect(powerup.rect):
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

        # ===== Game Over (HP) =====
        p1 = self.tanks[0]
        p2 = self.tanks[1]

        if p1.health <= 0:
            self.game.winner = "Player 2"
            self.game.change_state(GameOverState(self.game))
            return

        if p2.health <= 0:
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
    # UI
    # ==========================================
    def draw_arcade_health_ui(self, surface):
        bar_width = 200
        bar_height = 18
        padding = 20
        for i, tank in enumerate(self.tanks):
            health_ratio = tank.health / tank.max_health
            fill_width = int(bar_width * health_ratio)

            # ===== Player 1 - Trái =====
            if i == 0:
                x = padding
                align_right = False

            # ===== Player 2 - Phải =====
            else:
                x = surface.get_width() - bar_width - padding
                align_right = True
            y = padding + 30

            # ----- Tên player -----
            name_text = self.game.font_big.render(tank.name, True, Color.WHITE)
            if align_right:
                name_rect = name_text.get_rect(topright=(x + bar_width, padding))
            else:
                name_rect = name_text.get_rect(topleft=(x, padding))
            surface.blit(name_text, name_rect)

            # ----- Nền thanh máu -----
            pygame.draw.rect(surface, (100, 0, 0), (x, y, bar_width, bar_height))

            # ----- Màu máu theo % -----
            if health_ratio > 0.6:
                color = Color.GREEN
            elif health_ratio > 0.3:
                color = Color.ORANGE
            else:
                color = Color.RED
            pygame.draw.rect(surface, color, (x, y, fill_width, bar_height))
            hp_text = self.game.font_small.render(f"{int(tank.health)}/{tank.max_health}", True, Color.WHITE)
            hp_rect = hp_text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
            surface.blit(hp_text, hp_rect)

            # ----- Points -----
            pt_text = self.game.font_small.render(f"PT: {tank.point}", True, Color.WHITE)
            if i == 0:
                pt_rect = pt_text.get_rect(
                    topleft=(x, y + bar_height + 6)
                )

            else:
                pt_rect = pt_text.get_rect(
                    topright=(x + bar_width, y + bar_height + 6)
                )
            surface.blit(pt_text, pt_rect)

            # ===== GOAL TEXT =====
            goal_text = self.game.font_big.render("GOAL: 400", True, Color.WHITE)
            goal_rect = goal_text.get_rect(
                midtop=(surface.get_width() // 2, 10)
            )
            surface.blit(goal_text, goal_rect)

            # ----- Viền -----
            pygame.draw.rect(surface, Color.WHITE, (x, y, bar_width, bar_height), 2)

    def draw_control_hints(self, surface):
        padding = 20
        bottom_y = surface.get_height() - 25

        # =========================
        # Helper format key
        # =========================
        def format_key(key):
            return f"[{pygame.key.name(key).upper()}]"

        def format_keys(keys):
            return ", ".join(format_key(k) for k in keys)

        # ===== PLAYER 1 =====
        p1_controls = self.game.config.get_controls(1)
        p1_fire = self.game.config.key_list_to_string(p1_controls["fire"])
        p1_text_str = (
            f"P1: "
            f"{self.game.config.key_to_string(p1_controls['up']).upper()} "
            f"{self.game.config.key_to_string(p1_controls['down']).upper()} "
            f"{self.game.config.key_to_string(p1_controls['left']).upper()} "
            f"{self.game.config.key_to_string(p1_controls['right']).upper()} "
            f"| GUN: "
            f"{self.game.config.key_to_string(p1_controls['gun_left']).upper()} "
            f"{self.game.config.key_to_string(p1_controls['gun_right']).upper()} "
            f"| FIRE: {p1_fire}"
        )
        p1_text = self.game.font_small.render(
            p1_text_str,
            True,
            (255, 255, 255)
        )
        p1_rect = p1_text.get_rect(
            bottomleft=(padding, bottom_y)
        )
        surface.blit(p1_text, p1_rect)

        # ===== PLAYER 2 =====
        p2_controls = self.game.config.get_controls(2)
        p2_fire = self.game.config.key_list_to_string(p2_controls["fire"])
        p2_text_str = (
            f"P2: "
            f"{self.game.config.key_to_string(p2_controls['up']).upper()} "
            f"{self.game.config.key_to_string(p2_controls['down']).upper()} "
            f"{self.game.config.key_to_string(p2_controls['left']).upper()} "
            f"{self.game.config.key_to_string(p2_controls['right']).upper()} "
            f"| GUN: "
            f"{self.game.config.key_to_string(p2_controls['gun_left']).upper()} "
            f"{self.game.config.key_to_string(p2_controls['gun_right']).upper()} "
            f"| FIRE: {p2_fire}"
        )
        p2_text = self.game.font_small.render(
            p2_text_str,
            True,
            Color.WHITE
        )
        p2_rect = p2_text.get_rect(
            bottomright=(surface.get_width() - padding, bottom_y)
        )
        surface.blit(p2_text, p2_rect)

    # ==========================================
    # DRAW
    # ==========================================
    def draw(self, surface):

        # Vẽ tilemap
        self.game.tile_map.draw(surface)
        self.draw_arcade_health_ui(surface)
        self.draw_control_hints(surface)

        # Vẽ object động
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
                pygame.draw.rect(surface, Color.Green, tank.rect, 2)
            for tree in self.trees:
                pygame.draw.rect(surface, Color.RED, tree.get_hitbox(), 2)
            for bullet in self.bullets:
                pygame.draw.rect(surface, Color.YELLOW, bullet.get_hitbox(), 2)