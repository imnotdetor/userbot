from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded
)

mark_plugin_loaded("autoreply.py")

# =====================
# AUTO REPLY STATE
# =====================
AUTO_REPLY_ENABLED = False

# 🔔 Auto reply message (edit as you want)
AUTO_REPLY_TEXT = (
    "👋 Hello!\n\n"
    "I am currently unavailable.\n"
    "Please leave your message, I will reply soon 😊"
)

# =====================
# AUTO REPLY TO PRIVATE MSG
# =====================
@Client.on_message(filters.private & ~filters.bot & ~filters.me)
async def auto_reply_handler(client: Client, m):
    global AUTO_REPLY_ENABLED

    try:
        if not AUTO_REPLY_ENABLED:
            return

        # ignore service messages
        if not m.text and not m.caption:
            return

        await m.reply_text(AUTO_REPLY_TEXT)

    except Exception as e:
        await log_error(client, "autoreply.py", e)


# =====================
# AUTOREPLY ON
# =====================
@Client.on_message(owner_only & filters.command("autoreply on", "."))
async def autoreply_on(client: Client, m):
    global AUTO_REPLY_ENABLED

    try:
        AUTO_REPLY_ENABLED = True
        await m.delete()

        msg = await client.send_message(
            m.chat.id,
            "✅ Auto reply enabled"
        )
        await auto_delete(msg, 4)

    except Exception as e:
        await log_error(client, "autoreply.py", e)


# =====================
# AUTOREPLY OFF
# =====================
@Client.on_message(owner_only & filters.command("autoreply off", "."))
async def autoreply_off(client: Client, m):
    global AUTO_REPLY_ENABLED

    try:
        AUTO_REPLY_ENABLED = False
        await m.delete()

        msg = await client.send_message(
            m.chat.id,
            "❌ Auto reply disabled"
        )
        await auto_delete(msg, 4)

    except Exception as e:
        await log_error(client, "autoreply.py", e)
