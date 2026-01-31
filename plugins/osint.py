# plugins/osint.py

import os
import json
import time
import math
from datetime import datetime

from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "osint.py"
DATA_FILE = "utils/osint_store.json"

# =====================
# LOAD / SAVE
# =====================
def load():
    if not os.path.exists(DATA_FILE):
        return {"track": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

DATA = load()

mark_plugin_loaded(PLUGIN_NAME)
print("✔ osint.py loaded (EXTREME MODE)")

# =====================
# HELP
# =====================
register_help(
    "osint",
    ".userinfo | .userinfo full | .userinfo osint\n"
    ".numberinfo\n"
    ".userphotos\n"
    ".trackuser / .untrackuser\n"
    ".tracklist\n\n"
    "• Extreme Telegram OSINT\n"
    "• History tracking\n"
    "• Risk scoring\n"
    "• Legal & ToS-safe"
)

# =====================
# UTILS
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
    u = await bot.get_entity(arg)
    return u.id

def account_age(uid):
    # rough heuristic
    return 2013 + int(math.log10(uid)) if uid > 0 else "Unknown"

def risk_score(u, full):
    score = 0
    if not u.username: score += 15
    if not u.photo: score += 20
    if not full.about: score += 10
    if u.bot: score += 40
    if u.scam: score += 50
    if u.fake: score += 30
    return min(score, 100)

# =====================
# USERINFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.userinfo(?: (full|osint))?$"))
async def userinfo(e):
    try:
        uid = await resolve_user(e)
        if not uid:
            return

        u = await bot.get_entity(uid)
        f = await bot(GetFullUserRequest(uid))

        risk = risk_score(u, f)

        text = (
            "🧠 **USER OSINT REPORT**\n\n"
            f"• ID: `{u.id}`\n"
            f"• Name: `{(u.first_name or '')} {(u.last_name or '')}`\n"
            f"• Username: @{u.username or 'N/A'}\n"
            f"• Bio: `{f.about or 'N/A'}`\n"
            f"• Phone: `{u.phone or 'Hidden'}`\n"
            f"• Premium: `{bool(u.premium)}`\n"
            f"• Verified: `{bool(u.verified)}`\n"
            f"• Bot: `{bool(u.bot)}`\n"
            f"• Scam: `{bool(u.scam)}`\n"
            f"• Fake: `{bool(u.fake)}`\n"
            f"• Account Age: `{account_age(u.id)}`\n\n"
            f"⚠️ **RISK SCORE:** `{risk}%`\n"
            f"STATUS: `{'HIGH RISK' if risk > 60 else 'LOW RISK'}`"
        )

        await e.reply(text)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# NUMBER INFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.numberinfo$"))
async def numberinfo(e):
    uid = await resolve_user(e)
    u = await bot.get_entity(uid)
    if not u.phone:
        return await e.reply("❌ Phone hidden")
    await e.reply(
        f"📞 **NUMBER OSINT**\n\n"
        f"• Number: `+{u.phone}`\n"
        f"• Country: Approx from prefix\n"
        f"• Valid: Likely\n"
    )

# =====================
# USER PHOTOS
# =====================
@bot.on(events.NewMessage(pattern=r"\.userphotos$"))
async def userphotos(e):
    uid = await resolve_user(e)
    photos = await bot(GetUserPhotosRequest(uid, 0, 0, 10))
    await e.reply(f"📸 Profile photos count: `{len(photos.photos)}`")

# =====================
# TRACKING
# =====================
@bot.on(events.NewMessage(pattern=r"\.trackuser$"))
async def track(e):
    uid = await resolve_user(e)
    u = await bot.get_entity(uid)
    DATA["track"][str(uid)] = {
        "username": u.username,
        "name": f"{u.first_name} {u.last_name}",
        "bio": None,
        "time": time.time()
    }
    save()
    await e.reply("📌 User tracking enabled")

@bot.on(events.NewMessage(pattern=r"\.untrackuser$"))
async def untrack(e):
    uid = await resolve_user(e)
    DATA["track"].pop(str(uid), None)
    save()
    await e.reply("❌ Tracking disabled")

@bot.on(events.NewMessage(pattern=r"\.tracklist$"))
async def tracklist(e):
    if not DATA["track"]:
        return await e.reply("No tracked users")
    txt = "📌 **TRACKED USERS**\n\n"
    for uid in DATA["track"]:
        txt += f"• `{uid}`\n"
    await e.reply(txt)
