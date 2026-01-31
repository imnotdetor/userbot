# plugins/userinfo.py

import asyncio
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "userinfo.py"

# =====================
# LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ userinfo.py loaded")

# =====================
# HELP
# =====================
register_help(
    "userinfo",
    ".userinfo (reply / username / id)\n\n"
    "• Full Telegram user info\n"
    "• ID, name, username\n"
    "• Bio (about)\n"
    "• Phone (if visible)\n"
    "• Scam / Fake / Bot flags"
)

# =====================
# RESOLVE USER
# =====================
async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id

    arg = (e.pattern_match.group(1) or "").strip()
    if not arg:
        return None

    if arg.isdigit():
        return int(arg)

    try:
        u = await bot.get_entity(arg)
        return u.id
    except:
        return None

# =====================
# USERINFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.userinfo(?: (.*))?$"))
async def userinfo(e):
    if not is_owner(e):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        full = await bot(GetFullUserRequest(uid))

        user = full.users[0]          # ✅ FIX
        about = full.full_user.about

        text = (
            "👤 **USER INFO**\n\n"
            f"• ID: `{user.id}`\n"
            f"• Name: `{(user.first_name or '')} {(user.last_name or '')}`\n"
            f"• Username: `@{user.username}`\n"
            f"• Phone: `{user.phone or 'Hidden'}`\n"
            f"• Bio: `{about or 'None'}`\n\n"
            f"• Bot: `{user.bot}`\n"
            f"• Scam: `{user.scam}`\n"
            f"• Fake: `{user.fake}`"
        )

        await e.delete()
        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(12)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
