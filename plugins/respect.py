import json
import os
import asyncio
from datetime import date
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "respect.py"
DB_FILE = "utils/respect.json"

mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "respect",
    ".+ (reply)\n"
    ".- (reply)\n"
    ".respecttop\n\n"
    "• Respect system\n"
    "• 1 respect per user per day\n"
)

# =====================
# DB HELPERS
# =====================
def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "cooldown": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

# =====================
# RESPECT HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"\.([+-])$"))
async def respect_handler(e):
    if not e.is_reply:
        return

    try:
        await e.delete()
        action = e.pattern_match.group(1)

        giver = e.sender_id
        reply = await e.get_reply_message()
        target = reply.sender_id

        if giver == target:
            return

        today = str(date.today())
        key = f"{giver}:{target}"

        db = load_db()

        # cooldown
        if db["cooldown"].get(key) == today:
            m = await e.reply("⏳ You already gave respect today")
            await asyncio.sleep(5)
            await m.delete()
            return

        user = db["users"].setdefault(
            str(target),
            {
                "name": reply.sender.first_name or "User",
                "respect": 0
            }
        )

        user["respect"] += 1 if action == "+" else -1
        db["cooldown"][key] = today
        save_db(db)

        emoji = "⬆️" if action == "+" else "⬇️"
        m = await e.reply(
            f"{emoji} **Respect Updated**\n\n"
            f"👤 {user['name']}\n"
            f"⭐ Respect: `{user['respect']}`"
        )
        await asyncio.sleep(6)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# RESPECT TOP
# =====================
@bot.on(events.NewMessage(pattern=r"\.respecttop$"))
async def respect_top(e):
    try:
        await e.delete()
        db = load_db()
        users = db["users"]

        if not users:
            m = await e.reply("⭐ No respect data yet")
            await asyncio.sleep(5)
            await m.delete()
            return

        sorted_users = sorted(
            users.values(),
            key=lambda u: u["respect"],
            reverse=True
        )

        text = "🏆 **TOP RESPECT** 🏆\n\n"
        for i, u in enumerate(sorted_users[:5], 1):
            text += f"**{i}. {u['name']}** → ⭐ `{u['respect']}`\n"

        m = await e.reply(text)
        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
