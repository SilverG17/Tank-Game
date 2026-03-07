from states.gameover_state import GameOverState
from systems.item_spawner import spawn_coin, spawn_powerup
from constants import SCORE_LIMIT, TILE_SIZE

def update_bullets(game, bullets, tanks, trees, dt):
    for bullet in bullets[:]:
        bullet.update(
            dt,
            game.level_map,
            TILE_SIZE,
            game.screen.get_rect()
        )

        # Remove if inactive
        if not bullet.active:
            bullets.remove(bullet)
            continue

        # ===== Bullet vs Tank =====
        for tank in tanks:
            if not tank.alive:
                continue
            if tank != bullet.owner:
                if bullet.get_hitbox().colliderect(tank.get_hitbox()):
                    if not tank.has_shield:
                        tank.take_damage(10)
                        if tank.exploding:
                            game.audio.play_sfx("explosion.mp3")
                        else:
                            game.audio.play_sfx("get_hit.mp3")

                        bullet.owner.point += 15

                    bullets.remove(bullet)
                    continue

        # ===== Bullet vs Tree =====
        for tree in trees[:]:
            if bullet.get_hitbox().colliderect(tree.get_hitbox()):
                game.audio.play_sfx("hit.mp3")

                if tree.take_damage():
                    trees.remove(tree)
                    game.level_map[tree.gy][tree.gx] = 'g'

                bullets.remove(bullet)
                continue

def update_powerups(game, powerups, tanks, dt, timer, interval):
    timer += dt

    if timer >= interval:
        spawn_powerup(game, powerups)
        timer = 0

    for powerup in powerups[:]:
        for tank in tanks:
            if tank.get_hitbox().colliderect(powerup.rect):

                game.audio.play_sfx("coin.mp3")

                if powerup.type == "SPEED":
                    tank.speed_boost = 1.8
                    tank.powerup_timers["SPEED"] = powerup.duration

                elif powerup.type == "SHIELD":
                    tank.has_shield = True
                    tank.powerup_timers["SHIELD"] = powerup.duration

                elif powerup.type == "TRIPLE":
                    tank.powerup_timers["TRIPLE"] = powerup.duration

                powerups.remove(powerup)
                break

    return timer

def update_coins(game, coins, tanks, dt, timer, interval):
    timer += dt

    if timer >= interval:
        spawn_coin(game, coins)
        timer = 0

    for coin in coins[:]:
        for tank in tanks:
            if tank.rect.colliderect(coin.rect):

                tank.point += 20
                coins.remove(coin)
                game.audio.play_sfx("coin.mp3")
                break

    return timer

def check_game_over(game, tanks):
    p1 = tanks[0]
    p2 = tanks[1]

    if not p1.alive and p1.explosion_timer >= p1.explosion_duration:
        game.winner = "PLAYER 2"
        game.change_state(GameOverState(game))
        return True

    if not p2.alive and p2.explosion_timer >= p2.explosion_duration:
        game.winner = "PLAYER 1"
        game.change_state(GameOverState(game))
        return True

    if p1.point >= SCORE_LIMIT:
        game.winner = "PLAYER 1"
        game.change_state(GameOverState(game))
        return True

    if p2.point >= SCORE_LIMIT:
        game.winner = "PLAYER 2"
        game.change_state(GameOverState(game))
        return True

    return False