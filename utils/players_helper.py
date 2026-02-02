import json
import os
import time

DB = "utils/players.json"

# =====================
# LOAD
# =====================
def load_players():
    if not os.path.exists(DB):
        return {}
    with open(DB, "r") as f:
        return json.load(f)

# =====================
# SAVE
# =====================
def save(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=2)

# backward safe alias
def save_players(data):
    save(data)

# =====================
# DEFAULT ABILITIES
# =====================
def default_abilities():
    return {
        "coin_bonus": 0,          # VIP bonus coins
        "reaction_bonus": 0.0,    # seconds advantage
        "defuse_bomb": 0,         # bomb saves
        "lucky_chance": 0.0,      # % boost (low)
        "highlight": False        # VIP highlight
    }

# =====================
# GET PLAYER
# =====================
def get_player(uid, name):
    data = load_players()
    uid = str(uid)

    if uid not in data:
        data[uid] = {
            "name": name,
            "coins": 0,
            "level": 1,
            "xp": 0,

            # base stats
            "attack": 10,
            "defense": 8,
            "hp": 100,

            # inventory
            "items": {},

            # 🔥 ABILITIES
            "abilities": default_abilities(),

            # cooldown / runtime data
            "last_play": 0
        }
        save(data)

    # 🔥 SAFETY: old users upgrade
    player = data[uid]
    if "abilities" not in player:
        player["abilities"] = default_abilities()
        save(data)

    return data, player

# =====================
# APPLY ITEM ABILITY
# =====================
def apply_ability(player, ability_dict):
    """
    ability_dict example:
    {
        "coin_bonus": 5,
        "reaction_bonus": 0.5
    }
    """
    for key, val in ability_dict.items():
        if isinstance(val, bool):
            player["abilities"][key] = val
        else:
            player["abilities"][key] += val

# =====================
# CONSUME ABILITY (ONE TIME)
# =====================
def consume_ability(player, key):
    if player["abilities"].get(key, 0) > 0:
        player["abilities"][key] -= 1
        return True
    return False
