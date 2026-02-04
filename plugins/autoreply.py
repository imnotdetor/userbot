import asyncio
from datetime import datetime, timedelta
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.mongo import settings

print("✔ autoreply.py loaded (SMART V3 • FULL • FIXED)")

# =====================
# HELP
# =====================
register_help(
    "autoreply",
    ".autoreply on|off\n"
    ".autoreply status\n"
    ".autoreplydelay <sec>\n"
    ".autocooldown <sec>\n\n"
    ".seenonly on|off\n"
    ".firstreply on|off\n"
    ".autodisable on|off\n\n"
    ".officehours on|off\n"
    ".officehours set <start>-<end>\n\n"
    ".setmorning TEXT\n"
    ".setafternoon TEXT\n"
    ".setevening TEXT\n"
    ".setnight TEXT\n\n"
    ".awhitelist (reply)\n"
    ".ablacklist (reply)\n"
    ".awhitelistdel (reply)\n"
    ".ablacklistdel (reply)\n\n"
    ".keyword add <word> | <reply>\n"
    ".keyword del <word>\n"
    ".keyword list\n\n"
    ".scamfilter on|off\n"
    ".scamword add <word>\n"
    ".scamword del <word>\n"
    ".scamword list\n\n"
    "• DM only\n"
    "• Owner only\n"
    "• Mongo persistent"
)

# =====================
# DEFAULT TEXTS
# =====================
TIME_TEXTS = {
    "morning": "☀️ Good morning!\nI’ll reply soon 😊",
    "afternoon": "🌤 Hello!\nI’m busy right now.",
    "evening": "🌆 Good evening!\nWill get back to you.",
    "night": "🌙 Late night.\nPlease text, I’ll reply later 🙏"
}

FIRST_REPLY_TEXT = "👋 Hi! Thanks for messaging.\nI’ll reply shortly."

# =====================
# DB HELPERS (DUAL KEY)
# =====================
def get_var(*keys, default=None):
    for k in keys:
        d = settings.find_one({"_id": k})
        if d:
            return d["value"]
    return default

def set_var(k, v):
    settings.update_one({"_id": k}, {"$set": {"value": v}}, upsert=True)

def get_list(k):
    raw = get_var(k, default="")
    return [int(x) for x in raw.split(",") if x.strip().isdigit()]

def save_list(k, data):
    set_var(k, ",".join(str(x) for x in data))

def get_str_list(k):
    raw = get_var(k, default="")
    return [x.strip().lower() for x in raw.split(",") if x.strip()]

def save_str_list(k, data):
    set_var(k, ",".join(data))

# =====================
# FLAGS
# =====================
def enabled(): return get_var("AUTOREPLY_ON", "AR_ON", default="off") == "on"
def cooldown(): return int(get_var("AR_COOLDOWN", default="0"))
def delay(): return int(get_var("AUTOREPLY_DELAY", default="0"))
def seen_only(): return get_var("AR_SEENONLY", default="off") == "on"
def firstreply(): return get_var("AR_FIRST", default="off") == "on"
def autodisable(): return get_var("AR_AUTODISABLE", default="off") == "on"
def scamfilter(): return get_var("AR_SCAM", default="off") == "on"
def office_on(): return get_var("AR_OFFICE", default="off") == "on"

# =====================
# TIME TEXT
# =====================
def time_text():
    h = (datetime.utcnow() + timedelta(hours=5, minutes=30)).hour
    if 5 <= h <= 11:
        return get_var("AUTOREPLY_MORNING", "AR_MORNING", default=TIME_TEXTS["morning"])
    if 12 <= h <= 16:
        return get_var("AUTOREPLY_AFTERNOON", "AR_AFTERNOON", default=TIME_TEXTS["afternoon"])
    if 17 <= h <= 20:
        return get_var("AUTOREPLY_EVENING", "AR_EVENING", default=TIME_TEXTS["evening"])
    return get_var("AUTOREPLY_NIGHT", "AR_NIGHT", default=TIME_TEXTS["night"])

# =====================
# OFFICE HOURS
# =====================
def in_office_hours():
    if not office_on():
        return True
    rng = get_var("AR_OFFICE_RANGE", default="")
    if "-" not in rng:
        return True
    s, e = rng.split("-")
    h = (datetime.utcnow() + timedelta(hours=5, minutes=30)).hour
    return int(s) <= h <= int(e)

# =====================
# OWNER COMMANDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.autoreply (on|off)"))
async def _(e):
    if not is_owner(e): return
    set_var("AUTOREPLY_ON", e.pattern_match.group(1))
    set_var("AR_ON", e.pattern_match.group(1))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.autoreply status"))
async def _(e):
    if not is_owner(e): return
    txt = f"""**AutoReply Status**
ON: `{enabled()}`
Cooldown: `{cooldown()}s`
Delay: `{delay()}s`
SeenOnly: `{seen_only()}`
FirstReply: `{firstreply()}`
AutoDisable: `{autodisable()}`
OfficeHours: `{office_on()}`
ScamFilter: `{scamfilter()}`
"""
    await e.reply(txt)
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.autoreplydelay (\d+)"))
async def _(e):
    if not is_owner(e): return
    set_var("AUTOREPLY_DELAY", e.pattern_match.group(1))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.autocooldown (\d+)"))
async def _(e):
    if not is_owner(e): return
    set_var("AR_COOLDOWN", e.pattern_match.group(1))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.(seenonly|firstreply|autodisable|scamfilter|officehours) (on|off)"))
async def _(e):
    if not is_owner(e): return
    key = {
        "seenonly": "AR_SEENONLY",
        "firstreply": "AR_FIRST",
        "autodisable": "AR_AUTODISABLE",
        "scamfilter": "AR_SCAM",
        "officehours": "AR_OFFICE"
    }[e.pattern_match.group(1)]
    set_var(key, e.pattern_match.group(2))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.officehours set (\d+)-(\d+)"))
async def _(e):
    if not is_owner(e): return
    set_var("AR_OFFICE_RANGE", f"{e.pattern_match.group(1)}-{e.pattern_match.group(2)}")
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.set(morning|afternoon|evening|night) (.+)"))
async def _(e):
    if not is_owner(e): return
    key = f"AUTOREPLY_{e.pattern_match.group(1).upper()}"
    set_var(key, e.pattern_match.group(2))
    await e.delete()

# =====================
# KEYWORDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.keyword add (.+?) \| (.+)"))
async def _(e):
    if not is_owner(e): return
    data = dict(settings.find_one({"_id": "AR_KEYWORDS"}) or {}).get("value", {})
    data[e.pattern_match.group(1).lower()] = e.pattern_match.group(2)
    set_var("AR_KEYWORDS", data)
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.keyword del (.+)"))
async def _(e):
    if not is_owner(e): return
    data = dict(settings.find_one({"_id": "AR_KEYWORDS"}) or {}).get("value", {})
    data.pop(e.pattern_match.group(1).lower(), None)
    set_var("AR_KEYWORDS", data)
    await e.delete()

# =====================
# SCAM WORDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.scamword (add|del) (.+)"))
async def _(e):
    if not is_owner(e): return
    words = get_str_list("AR_SCAMWORDS")
    w = e.pattern_match.group(2).lower()
    if e.pattern_match.group(1) == "add" and w not in words:
        words.append(w)
    if e.pattern_match.group(1) == "del" and w in words:
        words.remove(w)
    save_str_list("AR_SCAMWORDS", words)
    await e.delete()

# =====================
# AUTOREPLY CORE
# =====================
@bot.on(events.NewMessage(incoming=True))
async def autoreply(e):
    try:
        if not e.is_private or is_owner(e):
            return

        sender = await e.get_sender()
        if sender and sender.bot:
            return

        if not enabled() or not in_office_hours():
            return

        uid = e.sender_id

        if uid in get_list("AUTOREPLY_BLACKLIST"):
            return

        wl = get_list("AUTOREPLY_WHITELIST")
        if wl and uid not in wl:
            return

        now = datetime.utcnow()
        last = get_var(f"AR_LAST_{uid}")

        if last:
            diff = (now - datetime.fromisoformat(last)).total_seconds()
            if diff < cooldown():
                return

        if seen_only() and e.is_unread:
            return

        if scamfilter():
            text = (e.raw_text or "").lower()
            for w in get_str_list("AR_SCAMWORDS"):
                if w in text:
                    return

        keywords = dict(settings.find_one({"_id": "AR_KEYWORDS"}) or {}).get("value", {})
        for k, r in keywords.items():
            if k in (e.raw_text or "").lower():
                await asyncio.sleep(delay())
                await e.reply(r)
                return

        if firstreply() and not last:
            msg = FIRST_REPLY_TEXT
        else:
            msg = time_text()

        await asyncio.sleep(delay())
        await e.reply(msg)

        set_var(f"AR_LAST_{uid}", now.isoformat())

        if autodisable():
            save_list("AUTOREPLY_BLACKLIST", get_list("AUTOREPLY_BLACKLIST") + [uid])

    except Exception as ex:
        await log_error(bot, "autoreply.py", ex)
