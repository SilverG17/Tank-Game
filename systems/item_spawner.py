from entities.powerup import PowerUp
from entities.coin import Coin
from constants import TILE_SIZE


def spawn_powerup(game, powerups):
    powerup = PowerUp(
        tile_size=TILE_SIZE,
        level_map=game.level_map,
        images=game.POWERUP_IMG
    )
    powerups.append(powerup)


def spawn_coin(game, coins):
    coin = Coin(
        tile_size=TILE_SIZE,
        level_map=game.level_map,
        image=game.COIN_IMG
    )
    coins.append(coin)