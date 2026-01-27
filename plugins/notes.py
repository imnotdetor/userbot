from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help
)
from database import set_note, get_note, del_note

# 🔥 mark plugin loaded (health system)
mark_plugin_loaded("notes.py")

# 🔥 auto help registration (help4.py)
register_help(
    "notes",
    """
.setnote <name> <text>
exm: .setnote test hello

.getnote <name>
exm: .getnote test

.delnote <name>
exm: .delnote test

• Notes are stored persistently
• Owner only
• Auto delete enabled
"""
)

# ======================
# SET NOTE
# ======================
@Client.on_message(owner_only & filters.command("setnote", "."))
async def setnote(_, m):
    try:
        if len(m.command) < 3:
            await m.delete()
            msg = await m.reply("Usage: `.setnote name text`")
            return await auto_delete(msg, 6)

        name = m.command[1]
        text = m.text.split(None, 2)[2]

        await m.delete()
        set_note(name, text)

        msg = await m.reply("✅ Note saved")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("notes.py", e)
        await log_error(_, "notes.py", e)

# ======================
# GET NOTE
# ======================
@Client.on_message(owner_only & filters.command("getnote", "."))
async def getnote(_, m):
    try:
        if len(m.command) < 2:
            await m.delete()
            msg = await m.reply("Usage: `.getnote name`")
            return await auto_delete(msg, 6)

        await m.delete()
        note = get_note(m.command[1])

        if not note:
            msg = await m.reply("❌ Note not found")
            return await auto_delete(msg, 5)

        msg = await m.reply(note)
        await auto_delete(msg, 15)

    except Exception as e:
        mark_plugin_error("notes.py", e)
        await log_error(_, "notes.py", e)

# ======================
# DELETE NOTE
# ======================
@Client.on_message(owner_only & filters.command("delnote", "."))
async def delnote(_, m):
    try:
        if len(m.command) < 2:
            await m.delete()
            msg = await m.reply("Usage: `.delnote name`")
            return await auto_delete(msg, 6)

        await m.delete()
        del_note(m.command[1])

        msg = await m.reply("🗑 Note deleted")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("notes.py", e)
        await log_error(_, "notes.py", e)
