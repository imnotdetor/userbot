# database/notes.py

from utils.mongo import db

# collection
_notes = db["notes"]

# =====================
# SET NOTE
# =====================
def set_note(name: str, text: str):
    _notes.update_one(
        {"_id": name},
        {"$set": {"text": text}},
        upsert=True
    )

# =====================
# GET NOTE
# =====================
def get_note(name: str):
    data = _notes.find_one({"_id": name})
    return data["text"] if data else None

# =====================
# DELETE NOTE
# =====================
def del_note(name: str):
    _notes.delete_one({"_id": name})

# =====================
# LIST NOTES
# =====================
def all_notes():
    return {x["_id"]: x.get("text") for x in _notes.find()}
