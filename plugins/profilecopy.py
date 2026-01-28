from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help
)
import asyncio
import time
import os
from pymongo import MongoClient

mark_plugin_loaded("profilecopy.py")

# =====================
# HELP
# =====================
register_help(
    "profilecopy",
    """
.backupprofile
.backupprofile force
.restoreprofile

.copybio   (reply)
.copyname  (reply)
.copydp    (reply)

.clone <seconds> (reply)
.clonestatus

.steal (reply)

.silentclone on/off
"""
)

# =====================
# MONGO
# =====================
from plugins.utils import mongo
db = mongo["userbot"]
profile_col = db["profile_backup"]

# =====================
# GLOBAL STATE
# =====================
CLONE_ACTIVE = False
CLONE_END_TIME = 0
SILENT_MODE = False
CLONE_TASK = None

# =====================
# HELPERS
# =====================
async def _apply_name(client, user):
    await client.update_profile(
        first_name=user.first_name,
        last_name=user.last_name
    )

async def _apply_bio(client, user):
    chat = await client.get_chat(user.id)
    await client.update_profile(bio=chat.bio or "")

async def _apply_dp(client, user):
    photos = await client.get_profile_photos(user.id, limit=1)
    if photos.total_count == 0:
        return False
    file = await client.download_media(photos.photos[0].file_id)
    await client.set_profile_photo(photo=file)
    os.remove(file)
    return True

async def backup_profile(client, force=False):
    if profile_col.find_one({"_id": "backup"}) and not force:
        return False

    me = await client.get_me()
    chat = await client.get_chat(me.id)

    profile_col.update_one(
        {"_id": "backup"},
        {"$set": {
            "first_name": me.first_name,
            "last_name": me.last_name,
            "bio": chat.bio or ""
        }},
        upsert=True
    )
    return True

async def restore_profile(client):
    data = profile_col.find_one({"_id": "backup"})
    if not data:
        return False

    await client.update_profile(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        bio=data.get("bio")
    )
    return True

# =====================
# BACKUP / RESTORE
# =====================
@Client.on_message(owner_only & filters.command("backupprofile", "."))
async def backup_cmd(client, m):
    try:
        await m.delete()
        force = len(m.command) > 1 and m.command[1] == "force"
        ok = await backup_profile(client, force)

        if not SILENT_MODE:
            msg = await client.send_message(
                m.chat.id,
                "Profile backup saved" if ok else "Backup exists (use force)"
            )
            await auto_delete(msg, 4)

    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)

@Client.on_message(owner_only & filters.command("restoreprofile", "."))
async def restore_cmd(client, m):
    try:
        await m.delete()
        ok = await restore_profile(client)
        if not SILENT_MODE:
            msg = await client.send_message(
                m.chat.id,
                "Profile restored" if ok else "No backup found"
            )
            await auto_delete(msg, 4)
    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)

# =====================
# COPY
# =====================
@Client.on_message(owner_only & filters.command("copybio", ".") & filters.reply)
async def copybio_cmd(client, m):
    await m.delete()
    await backup_profile(client)
    await _apply_bio(client, m.reply_to_message.from_user)

@Client.on_message(owner_only & filters.command("copyname", ".") & filters.reply)
async def copyname_cmd(client, m):
    await m.delete()
    await backup_profile(client)
    await _apply_name(client, m.reply_to_message.from_user)

@Client.on_message(owner_only & filters.command("copydp", ".") & filters.reply)
async def copydp_cmd(client, m):
    await m.delete()
    await backup_profile(client)
    await _apply_dp(client, m.reply_to_message.from_user)

# =====================
# SILENT MODE
# =====================
@Client.on_message(owner_only & filters.command("silentclone", "."))
async def silent_cmd(client, m):
    global SILENT_MODE
    await m.delete()
    SILENT_MODE = m.command[1] == "on"

# =====================
# CLONE
# =====================
@Client.on_message(owner_only & filters.command("clone", ".") & filters.reply)
async def clone_cmd(client, m):
    global CLONE_ACTIVE, CLONE_END_TIME, CLONE_TASK

    await m.delete()
    if CLONE_ACTIVE:
        return

    seconds = int(m.command[1])
    user = m.reply_to_message.from_user

    await backup_profile(client)
    await _apply_name(client, user)
    await _apply_bio(client, user)
    await _apply_dp(client, user)

    CLONE_ACTIVE = True
    CLONE_END_TIME = time.time() + seconds

    async def restore_later():
        await asyncio.sleep(seconds)
        await restore_profile(client)
        global CLONE_ACTIVE, CLONE_END_TIME
        CLONE_ACTIVE = False
        CLONE_END_TIME = 0

    CLONE_TASK = asyncio.create_task(restore_later())

# =====================
# CLONE STATUS
# =====================
@Client.on_message(owner_only & filters.command("clonestatus", "."))
async def status_cmd(client, m):
    await m.delete()
    if not CLONE_ACTIVE:
        msg = await client.send_message(m.chat.id, "No active clone")
    else:
        rem = max(0, int(CLONE_END_TIME - time.time()))
        msg = await client.send_message(m.chat.id, f"Time left: {rem}s")
    await auto_delete(msg, 4)

# =====================
# STEAL
# =====================
@Client.on_message(owner_only & filters.command("steal", ".") & filters.reply)
async def steal_cmd(client, m):
    await m.delete()
    await backup_profile(client)
    user = m.reply_to_message.from_user
    await _apply_name(client, user)
    await _apply_bio(client, user)
    await _apply_dp(client, user)
