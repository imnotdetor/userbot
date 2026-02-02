import json
import os

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
def save_players(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=2)

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
            "attack": 10,
            "defense": 8,
            "hp": 100
        }
        save_players(data)   # ✅ FIXED

    return data, data[uid]
