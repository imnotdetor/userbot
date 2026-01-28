from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.plugin_status import (
    mark_plugin_loaded,
    mark_plugin_error,
    get_broken_plugins
)
from utils.help_registry import register_help
from utils.health import get_uptime, mongo_status
from utils.logger import log_error
from utils.auto_delete import auto_delete

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("health.py")
print("✔ health.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "info",
    ".health\n\n"
    "Show overall userbot health\n"
    "• Uptime\n"
    "• MongoDB status\n"
    "• Broken plugins list"
)

MAX_LEN = 3500  # telegram safe limit


# =====================
# SAFE LONG SEND
# =====================
async def send_long(e, text, delete_after=30):
    for i in range(0, len(text), MAX_LEN):
        msg = await e.reply(text[i:i + MAX_LEN])
        if delete_after:
            await auto_delete(msg, delete_after)


# =====================
# HEALTH COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.health$"))
async def health_cmd(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except:
            pass

        broken = get_broken_plugins()

        # -----------------
        # ALL OK
        # -----------------
        if not broken:
            text = (
                "🩺 USERBOT HEALTH\n\n"
                f"⏱ Uptime: {get_uptime()}\n"
                f"🗄 MongoDB: {mongo_status()}\n\n"
                "✅ All plugins working fine"
            )
            msg = await e.reply(text)
            await auto_delete(msg, 20)
            return

        # -----------------
        # BROKEN PLUGINS
        # -----------------
        text = (
            "🩺 USERBOT HEALTH\n\n"
            f"⏱ Uptime: {get_uptime()}\n"
            f"🗄 MongoDB: {mongo_status()}\n\n"
            "❌ BROKEN PLUGINS:\n"
        )

        for name, info in broken.items():
            err = info.get("error", "Unknown error")
            text += (
                "\n--------------------\n"
                f"• {name}\n"
                f"{err[:800]}"
            )

        await send_long(e, text, 30)

    except Exception as ex:
        mark_plugin_error("health.py", ex)
        await log_error(bot, "health.py", ex)
