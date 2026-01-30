import json
import os

FILE = "utils/antipm_data.json"

def _load():
    if not os.path.exists(FILE):
        return {"state": {"enabled": True, "silent": False}, "users": {}}
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_state():
    return _load()["state"]

def set_state(k, v):
    d = _load()
    d["state"][k] = v
    _save(d)

def get_user(uid):
    return _load()["users"].get(str(uid))

def save_user(uid, data):
    d = _load()
    d["users"][str(uid)] = data
    _save(d)

def reset_user(uid):
    d = _load()
    d["users"].pop(str(uid), None)
    _save(d)

def list_users():
    return _load()["users"]
