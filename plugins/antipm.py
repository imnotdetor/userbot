# plugins/antipm.py

import time
import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.functions.contacts import BlockRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

from utils.local_store import (
    get_state,
    set_state,
    get_user,
    save_user,
    reset_user,
    list_users
)

PLUGIN_NAME = "antipm.py"

# =====================
# PLUGIN LOAD + HEALTH
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ antipm.py loaded (local_store backend)")

WARNING_LIMIT = 3
SPAM_LIMIT = 5
SPAM_WINDOW = 10


# =====================
# UTILS
# =====================
def ts(t):
    if not t:
        return "N/A"
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id

    arg = e.pattern_match.group(1)
    if not arg:
        return None

    try:
        if arg.isdigit():
            return int(arg)
        u = await bot.get_entity(arg)
        return u.id
    except:
        return None


# =====================
# HELP
# =====================
register_help(
    "antipm",
    ".antipm on | off\n"
    ".antipms on | off\n"
    ".antipmstatus\n"
    ".antipmlist\n"
    ".approve (reply / user / id)\n"
    ".disapprove (reply / user / id)\n"
    ".resetwarn (reply / user / id)\n\n"
    "• Local disk based (NO Mongo)\n"
    "• Warning replace system\n"
    "• Spam detection\n"
    "• DM only"
)


# =====================
# TOGGLES
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipm (on|off)$"))
async def toggle_antipm(e):
    if not is_owner(e):
        return

    val = e.pattern_match.group(1) == "on"
    set_state("enabled", val)

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        f"🛡 Anti-PM {'ENABLED' if val else 'DISABLED'}"
    )
    await asyncio.sleep(5)
    await m.delete()


@bot.on(events.NewMessage(pattern=r"\.antipms (on|off)$"))
async def toggle_silent(e):
    if not is_owner(e):
        return

    set_state("enabled", True)
    set_state("silent", e.pattern_match.group(1) == "on")

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        f"🔇 Silent mode {'ON' if get_state()['silent'] else 'OFF'}"
    )
    await asyncio.sleep(5)
    await m.delete()


# =====================
# STATUS
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipmstatus$"))
async def antipm_status(e):
    if not is_owner(e):
        return

    s = get_state()
    users = list_users()

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        "🛡 **Anti-PM Status**\n\n"
        f"• Enabled: `{s.get('enabled', True)}`\n"
        f"• Silent: `{s.get('silent', False)}`\n"
        f"• Tracked users: `{len(users)}`\n"
        f"• Last blocked: `{s.get('last_blocked_user') or 'N/A'}`\n"
        f"• Last warning: `{ts(s.get('last_warning_time'))}`"
    )
    await asyncio.sleep(10)
    await m.delete()


# =====================
# LIST USERS
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipmlist$"))
async def antipm_list(e):
    if not is_owner(e):
        return

    users = list_users()
    await e.delete()

    if not users:
        m = await bot.send_message(e.chat_id, "📭 No tracked users")
        await asyncio.sleep(5)
        return await m.delete()

    text = "🛡 **Anti-PM Users**\n\n"
    for uid, u in users.items():
        text += (
            f"• `{uid}` | "
            f"warn: `{u.get('warnings',0)}` | "
            f"approved: `{u.get('approved',False)}` | "
            f"last warn: `{ts(u.get('last_warning_time'))}`\n"
        )

    m = await bot.send_message(e.chat_id, text)
    await asyncio.sleep(15)
    await m.delete()


# =====================
# APPROVE / DISAPPROVE / RESET
# =====================
@bot.on(events.NewMessage(pattern=r"\.approve(?:\s+(.+))?$"))
async def approve_user(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    save_user(uid, {
        "approved": True,
        "warnings": 0,
        "msgs": [],
        "last_warn_msg": None,
        "last_warning_time": None
    })

    await e.delete()


@bot.on(events.NewMessage(pattern=r"\.disapprove(?:\s+(.+))?$"))
async def disapprove_user(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if uid:
        reset_user(uid)
    await e.delete()


@bot.on(events.NewMessage(pattern=r"\.resetwarn(?:\s+(.+))?$"))
async def resetwarn(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    save_user(uid, {
        "approved": False,
        "warnings": 0,
        "msgs": [],
        "last_warn_msg": None,
        "last_warning_time": None
    })
    await e.delete()


# =====================
# MAIN HANDLER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def antipm_handler(e):
    if not e.is_private or is_owner(e):
        return

    s = get_state()
    if not s.get("enabled", True):
        return

    try:
        sender = await e.get_sender()
        uid = sender.id

        if sender.bot or sender.verified:
            return

        u = get_user(uid)
        now = time.time()

        if u and u.get("approved"):
            return

        if not u:
            save_user(uid, {
                "approved": False,
                "warnings": 0,
                "msgs": [now],
                "last_warn_msg": None,
                "last_warning_time": None
            })
            if not s.get("silent"):
                await bot.send_message(uid, "👋 DMs are restricted.")
            return

        msgs = [t for t in u.get("msgs", []) if now - t < SPAM_WINDOW] + [now]

        if len(msgs) >= SPAM_LIMIT:
            set_state("last_blocked_user", uid)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        warnings = u.get("warnings", 0) + 1
        set_state("last_warning_time", now)

        if warnings >= WARNING_LIMIT:
            set_state("last_blocked_user", uid)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        warn_msg = None
        if not s.get("silent"):
            warn_msg = await bot.send_message(
                uid, f"⚠️ Warning {warnings}/{WARNING_LIMIT}"
            )

        save_user(uid, {
            "approved": False,
            "warnings": warnings,
            "msgs": msgs,
            "last_warn_msg": warn_msg.id if warn_msg else None,
            "last_warning_time": now
        })

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
