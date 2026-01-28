from pyrogram import filters
import os

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

def owner_check(_, __, m):
    if not m.from_user:
        return False
    return m.from_user.id == OWNER_ID

owner_only = filters.create(owner_check)
