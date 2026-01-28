# database/notes.py

from database import notes as _notes

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
    if not data:
        return None
    return data.get("text")

# =====================
# DELETE NOTE
# =====================
def del_note(name: str):
    _notes.delete_one({"_id": name})

# =====================
# LIST ALL NOTES
# =====================
def all_notes():
    result = {}
    for x in _notes.find():
        result[x["_id"]] = x.get("text")
    return result
