# plugins/ship.py

import random
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.auto_delete import auto_delete

PLUGIN_NAME = "ship.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ ship.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "ship",
    ".ships\n\n"
    "• Randomly makes a couple\n"
    "• Picks 2 random users from chat\n"
    "• Owner only\n"
    "• Auto delete enabled"
)

# =====================
# SHIP COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.ships$"))
async def ship_cmd(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except:
            pass

        users = []

        # collect users safely
        async for user in bot.iter_participants(e.chat_id, limit=200):
            if user.bot or user.deleted:
                continue
            users.append(user)

        if len(users) < 2:
            return

        u1, u2 = random.sample(users, 2)

        name1 = u1.first_name or "User"
        name2 = u2.first_name or "User"

        percent = random.randint(1, 100)

        text = (
            f"💞 [{name1}](tg://user?id={u1.id}) "
            f"❤️ [{name2}](tg://user?id={u2.id})\n\n"
            f"Compatibility: **{percent}%**"
        )

        msg = await bot.send_message(
            e.chat_id,
            text,
            link_preview=False
        )

        await auto_delete(msg, 8)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
