def build_controls(config, player):
    raw = config.get_controls(player)

    return {
        "up": raw["up"],
        "down": raw["down"],
        "left": raw["left"],
        "right": raw["right"],
        "gun_left": raw["gun_left"],
        "gun_right": raw["gun_right"],
        "fire": raw["fire"],
    }