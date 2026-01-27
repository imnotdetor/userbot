from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help      # 🔥 AUTO HELP
)

mark_plugin_loaded("help2.py")

# =====================
# HELP SECTIONS
# =====================

HELP_SECTIONS = {
    "profile": """
PROFILE COPY / CLONE

.backupprofile | exm: .backupprofile
Save current name + bio (recommended)

.backupprofile force | exm: .backupprofile force
Overwrite old backup

.restoreprofile | exm: .restoreprofile
Restore name + bio + dp

.copybio | exm: (reply) .copybio
Copy user's bio

.copyname | exm: (reply) .copyname
Copy user's name

.copydp | exm: (reply) .copydp
Copy user's profile photo
""",

    "clone": """
CLONE FEATURES

.clone <seconds> | exm: (reply) .clone 10
Clone name + bio + dp temporarily

.clonestatus | exm: .clonestatus
Check clone status

.silentclone on/off | exm: .silentclone on
Silent clone mode
""",

    "fun": """
FUN PROFILE

.steal | exm: (reply) .steal
Fun profile copy 😈
"""
}

# =====================
# FULL HELP TEXT
# =====================

FULL_HELP = """
USERBOT HELP 2 (EXTRA FEATURES)

Use:
.help2 profile
.help2 clone
.help2 fun

Or:
.help2
(for full list)

All commands are owner-only
Commands auto delete
"""

# =====================
# REGISTER AUTO HELP
# =====================

register_help(
    "help2",
    FULL_HELP + "\n".join(HELP_SECTIONS.values())
)

# =====================
# HELP2 COMMAND
# =====================

@Client.on_message(owner_only & filters.command("help2", "."))
async def help2_cmd(client: Client, m):
    try:
        try:
            await m.delete()
        except:
            pass

        if len(m.command) > 1:
            key = m.command[1].lower()
            text = HELP_SECTIONS.get(key, "No such help section ❌")
        else:
            text = FULL_HELP + "\n".join(HELP_SECTIONS.values())

        msg = await m.reply(text)
        await auto_delete(msg, 40)

    except Exception as e:
        mark_plugin_error("help2.py", e)
        await log_error(client, "help2.py", e)
