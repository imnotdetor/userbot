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

# 🔥 Mongo access
from plugins.utils import db

mark_plugin_loaded("profilecopy.py")

# =====================
# HELP4 AUTO REGISTER
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

• Profile backup is permanent (MongoDB)
• DP stored via Telegram file_id
• Clone auto-restores
"""
)

# =====================
# MONGO COLLECTION
# =====================
profile_col = db["profile_backup"]

# =====================
# GLOBAL STATE
# =====================
CLONE_ACTIVE = False
CLONE_END_TIME = 0
SILENT_MODE = False


# =====================
# HELPERS
# =====================
async def get_user_bio(client, user_id):
    try:
        chat = await client.get_chat(user_id)
        return chat.bio or ""
    except:
        return ""


async def backup_profile(client, force=False):
    doc = profile_col.find_one({"_id": "owner"})

    if doc and not force:
        return False

    me = await client.get_me()
    bio = await get_user_bio(client, me.id)

    dp_file_id = None
    try:
        photos = await client.get_profile_photos("me", limit=1)
        if photos.total_count > 0:
            dp_file_id = photos.photos[0].file_id
    except:
        pass

    profile_col.update_one(
        {"_id": "owner"},
        {"$set": {
            "first_name": me.first_name,
            "last_name": me.last_name,
            "bio": bio,
            "dp_file_id": dp_file_id,
            "time": time.time()
        }},
        upsert=True
    )
    return True


async def restore_profile(client):
    doc = profile_col.find_one({"_id": "owner"})
    if not doc:
        return False

    await client.update_profile(
        first_name=doc.get("first_name"),
        last_name=doc.get("last_name"),
        bio=doc.get("bio")
    )

    dp = doc.get("dp_file_id")
    if dp:
        try:
            await client.set_profile_photo(dp)
        except:
            pass

    return True


# =====================
# BACKUP / RESTORE
# =====================
@Client.on_message(owner_only & filters.command("backupprofile", "."))
async def backup_cmd(client, m):
    try:
        await m.delete()
        force = len(m.command) > 1 and m.command[1].lower() == "force"
        ok = await backup_profile(client, force)

        if not SILENT_MODE:
            msg = await client.send_message(
                m.chat.id,
                "Profile backup saved permanently"
                if ok else "Backup already exists (use .backupprofile force)"
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
                "Profile restored successfully" if ok else "No backup found"
            )
            await auto_delete(msg, 4)

    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)


# =====================
# COPY BIO / NAME / DP
# =====================
@Client.on_message(owner_only & filters.command("copybio", ".") & filters.reply)
async def copy_bio(client, m):
    try:
        await m.delete()
        user = m.reply_to_message.from_user
        if not user:
            return

        await backup_profile(client)
        bio = await get_user_bio(client, user.id)
        await client.update_profile(bio=bio)

        if not SILENT_MODE:
            msg = await client.send_message(m.chat.id, "Bio copied")
            await auto_delete(msg, 3)

    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)


@Client.on_message(owner_only & filters.command("copyname", ".") & filters.reply)
async def copy_name(client, m):
    try:
        await m.delete()
        user = m.reply_to_message.from_user
        if not user:
            return

        await backup_profile(client)
        await client.update_profile(
            first_name=user.first_name,
            last_name=user.last_name
        )

        if not SILENT_MODE:
            msg = await client.send_message(m.chat.id, "Name copied")
            await auto_delete(msg, 3)

    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)


@Client.on_message(owner_only & filters.command("copydp", ".") & filters.reply)
async def copy_dp(client, m):
    try:
        await m.delete()
        user = m.reply_to_message.from_user
        if not user:
            return

        await backup_profile(client)
        photos = await client.get_profile_photos(user.id, limit=1)
        if photos.total_count == 0:
            return

        await client.set_profile_photo(photos.photos[0].file_id)

        if not SILENT_MODE:
            msg = await client.send_message(m.chat.id, "DP copied")
            await auto_delete(msg, 3)

    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)
