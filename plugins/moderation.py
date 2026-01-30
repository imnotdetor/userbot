# plugins/moderation.py

import time, json, os, asyncio
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "moderation.py"
DATA_FILE = "utils/moderation_data.json"

# =====================
# LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ moderation.py loaded (FIXED)")

def load():
    if not os.path.exists(DATA_FILE):
        return {"gmutes": {}, "gbans": {}}
    return json.load(open(DATA_FILE))

def save(d):
    json.dump(d, open(DATA_FILE, "w"), indent=2)

DATA = load()

def now():
    return int(time.time())

def parse_time(t):
    if not t:
        return None
    try:
        n, u = int(t[:-1]), t[-1]
        return n * 60 if u == "m" else n * 3600 if u == "h" else n * 86400
    except:
        return None

async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id
    arg = (e.pattern_match.group(1) or "").strip()
    if arg.isdigit():
        return int(arg)
    u = await bot.get_entity(arg)
    return u.id

# =====================
# RIGHTS
# =====================
MUTE = ChatBannedRights(send_messages=True)
UNMUTE = ChatBannedRights(send_messages=False)
BAN = ChatBannedRights(view_messages=True)
UNBAN = ChatBannedRights(view_messages=False)

# =====================
# HELP
# =====================
register_help(
    "moderation",
    ".gmute [10m|1h|1d] [reason]\n"
    ".ungmute\n"
    ".gban [reason]\n"
    ".ungban\n"
    ".gmutelist\n"
    ".gbanlist\n\n"
    "• REAL global moderation\n"
    "• Multi-group ban/mute\n"
    "• Auto-unmute supported"
)

# =====================
# GMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.gmute(?: (\S+))?(?: (.*))?$"))
async def gmute(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    dur = parse_time(e.pattern_match.group(1))
    reason = e.pattern_match.group(2) or "No reason"

    DATA["gmutes"][str(uid)] = {
        "until": now() + dur if dur else None,
        "reason": reason
    }
    save(DATA)

    await e.delete()
    await e.respond(f"🔕 GMUTED `{uid}` | {reason}")

# =====================
# UNGMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.ungmute(?: (.*))?$"))
async def ungmute(e):
    if not is_owner(e):
        return
    uid = await resolve_user(e)
    DATA["gmutes"].pop(str(uid), None)
    save(DATA)
    await e.delete()
    await e.respond("🔔 GMUTE removed")

# =====================
# GBAN (REAL)
# =====================
@bot.on(events.NewMessage(pattern=r"\.gban(?: (.*))?$"))
async def gban(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    reason = e.pattern_match.group(1) or "No reason"
    DATA["gbans"][str(uid)] = {"time": now(), "reason": reason}
    save(DATA)

    async for d in bot.iter_dialogs():
        if d.is_group or d.is_channel:
            try:
                await bot(EditBannedRequest(d.id, uid, BAN))
            except:
                pass

    await e.delete()
    await e.respond(f"🚫 GBANNED `{uid}` | {reason}")

# =====================
# UNGBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.ungban(?: (.*))?$"))
async def ungban(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    DATA["gbans"].pop(str(uid), None)
    save(DATA)

    async for d in bot.iter_dialogs():
        if d.is_group or d.is_channel:
            try:
                await bot(EditBannedRequest(d.id, uid, UNBAN))
            except:
                pass

    await e.delete()
    await e.respond("✅ GBAN removed")

# =====================
# LISTS
# =====================
@bot.on(events.NewMessage(pattern=r"\.gmutelist$"))
async def gmutelist(e):
    if not is_owner(e):
        return
    txt = "🔕 GMUTES\n\n"
    for u, d in DATA["gmutes"].items():
        txt += f"• `{u}` → {d.get('reason')}\n"
    await e.reply(txt or "Empty")

@bot.on(events.NewMessage(pattern=r"\.gbanlist$"))
async def gbanlist(e):
    if not is_owner(e):
        return
    txt = "🚫 GBANS\n\n"
    for u, d in DATA["gbans"].items():
        txt += f"• `{u}` → {d.get('reason')}\n"
    await e.reply(txt or "Empty")

# =====================
# WATCHER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def watcher(e):
    try:
        uid = str(e.sender_id)

        if uid in DATA["gbans"]:
            await e.delete()
            return

        gm = DATA["gmutes"].get(uid)
        if gm:
            if gm["until"] and now() > gm["until"]:
                DATA["gmutes"].pop(uid)
                save(DATA)
            else:
                await e.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
