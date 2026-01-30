# plugins/moderation.py

import re
import json
import asyncio
from datetime import timedelta
from telethon import events
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "moderation.py"
DATA_FILE = "data/moderation.json"

# =====================
# LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ moderation.py loaded")

# =====================
# DATA STORE
# =====================
def load():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"gmute": {}, "gban": {}, "block": {}}

def save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

DATA = load()

# =====================
# HELP
# =====================
register_help(
    "moderation",
    ".block (reply/user/id) [reason]\n"
    ".unblock (reply/user/id)\n"
    ".blocklist\n\n"
    ".gmute [time] (reply/user/id) [reason]\n"
    ".ungmute (reply/user/id)\n"
    ".gmutelist\n\n"
    ".gban (reply/user/id) [reason]\n"
    ".ungban (reply/user/id)\n"
    ".gbanlist\n\n"
    "Time: 10m / 1h / 1d\n"
    "• Group admin rights required"
)

# =====================
# RIGHTS
# =====================
MUTE = ChatBannedRights(send_messages=True)
UNMUTE = ChatBannedRights(send_messages=False)
BAN = ChatBannedRights(view_messages=True)
UNBAN = ChatBannedRights(view_messages=False)

# =====================
# UTILS
# =====================
def parse_time(t):
    if not t:
        return None
    m = re.match(r"(\d+)(m|h|d)", t)
    if not m:
        return None
    v, u = int(m.group(1)), m.group(2)
    return (
        timedelta(minutes=v) if u == "m" else
        timedelta(hours=v) if u == "h" else
        timedelta(days=v)
    )

async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id
    arg = e.pattern_match.group(2)
    if not arg:
        return None
    try:
        return int(arg) if arg.isdigit() else (await bot.get_entity(arg)).id
    except:
        return None

# =====================
# BLOCK / UNBLOCK (DM)
# =====================
@bot.on(events.NewMessage(pattern=r"\.block(?:\s+(.+))?$"))
async def block_user(e):
    if not is_owner(e):
        return
    try:
        uid = await resolve_user(e)
        reason = e.pattern_match.group(1) or "No reason"
        if not uid:
            return
        await bot(BlockRequest(uid))
        DATA["block"][str(uid)] = reason
        save(DATA)
        await e.delete()
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

@bot.on(events.NewMessage(pattern=r"\.unblock(?:\s+(.+))?$"))
async def unblock_user(e):
    if not is_owner(e):
        return
    uid = await resolve_user(e)
    if uid:
        DATA["block"].pop(str(uid), None)
        save(DATA)
        await bot(BlockRequest(uid, False))
        await e.delete()

@bot.on(events.NewMessage(pattern=r"\.blocklist$"))
async def blocklist(e):
    if not is_owner(e):
        return
    text = "🚫 **Blocked Users**\n\n"
    for u, r in DATA["block"].items():
        text += f"• `{u}` → {r}\n"
    await e.delete()
    await bot.send_message(e.chat_id, text or "No blocked users")

# =====================
# GMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.gmute(?:\s+(\d+[mhd]))?(?:\s+(.+))?$"))
async def gmute(e):
    if not is_owner(e) or not e.is_group:
        return
    uid = await resolve_user(e)
    if not uid:
        return

    delta = parse_time(e.pattern_match.group(1))
    reason = e.pattern_match.group(2) or "No reason"
    until = int((e.date + delta).timestamp()) if delta else None

    rights = ChatBannedRights(
        until_date=until,
        send_messages=True
    )

    await bot(EditBannedRequest(e.chat_id, uid, rights))

    DATA["gmute"][str(uid)] = {
        "chat": e.chat_id,
        "until": until,
        "reason": reason
    }
    save(DATA)
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.ungmute(?:\s+(.+))?$"))
async def ungmute(e):
    if not is_owner(e) or not e.is_group:
        return
    uid = await resolve_user(e)
    if uid:
        DATA["gmute"].pop(str(uid), None)
        save(DATA)
        await bot(EditBannedRequest(e.chat_id, uid, UNMUTE))
        await e.delete()

@bot.on(events.NewMessage(pattern=r"\.gmutelist$"))
async def gmutelist(e):
    if not is_owner(e):
        return
    text = "🔇 **Muted Users**\n\n"
    for u, d in DATA["gmute"].items():
        text += f"• `{u}` → {d['reason']}\n"
    await e.delete()
    await bot.send_message(e.chat_id, text or "No muted users")

# =====================
# GBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.gban(?:\s+(.+))?$"))
async def gban(e):
    if not is_owner(e) or not e.is_group:
        return
    uid = await resolve_user(e)
    reason = e.pattern_match.group(1) or "No reason"
    if not uid:
        return
    await bot(EditBannedRequest(e.chat_id, uid, BAN))
    DATA["gban"][str(uid)] = reason
    save(DATA)
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.ungban(?:\s+(.+))?$"))
async def ungban(e):
    if not is_owner(e) or not e.is_group:
        return
    uid = await resolve_user(e)
    if uid:
        DATA["gban"].pop(str(uid), None)
        save(DATA)
        await bot(EditBannedRequest(e.chat_id, uid, UNBAN))
        await e.delete()

@bot.on(events.NewMessage(pattern=r"\.gbanlist$"))
async def gbanlist(e):
    if not is_owner(e):
        return
    text = "⛔ **Group Banned Users**\n\n"
    for u, r in DATA["gban"].items():
        text += f"• `{u}` → {r}\n"
    await e.delete()
    await bot.send_message(e.chat_id, text or "No banned users")
