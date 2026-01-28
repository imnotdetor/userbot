from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.auto_delete import auto_delete
from database import settings
from config import API_ID, API_HASH

from utils.bot_manager import (
    start_bot,
    stop_bot,
    list_running_bots
)

print("✔ botmanager.py loaded")

register_help(
    "botmanager",
    ".addbot NAME TOKEN\n"
    ".startbot NAME\n"
    ".stopbot NAME\n"
    ".delbot NAME\n"
    ".bots"
)

def set_var(key, value):
    settings.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)

def get_var(key):
    d = settings.find_one({"_id": key})
    return d["value"] if d else None

def del_var(key):
    settings.delete_one({"_id": key})

@bot.on(events.NewMessage(pattern=r"^\.addbot(\s|$)"))
async def add_bot(e):
    if not is_owner(e):
        return
    try:
        parts = e.raw_text.split(maxsplit=2)
        if len(parts) < 3:
            msg = await e.respond("Usage: .addbot NAME TOKEN")
            return await auto_delete(msg, 5)

        set_var(f"BOT_{parts[1].upper()}", parts[2])
        msg = await e.respond("✅ Bot added")
        await auto_delete(msg, 5)
    except Exception as ex:
        await log_error(bot, "botmanager.py", ex)

@bot.on(events.NewMessage(pattern=r"^\.startbot(\s|$)"))
async def start_bot_cmd(e):
    if not is_owner(e):
        return
    try:
        name = e.raw_text.split(maxsplit=1)[1].lower()
        token = get_var(f"BOT_{name.upper()}")
        if not token:
            return await e.respond("❌ Bot not found")

        await start_bot(name, token, API_ID, API_HASH)
        msg = await e.respond(f"🚀 Bot started: {name}")
        await auto_delete(msg, 5)
    except Exception as ex:
        await log_error(bot, "botmanager.py", ex)

@bot.on(events.NewMessage(pattern=r"^\.stopbot(\s|$)"))
async def stop_bot_cmd(e):
    if not is_owner(e):
        return
    try:
        name = e.raw_text.split(maxsplit=1)[1].lower()
        await stop_bot(name)
        msg = await e.respond(f"🛑 Bot stopped: {name}")
        await auto_delete(msg, 5)
    except Exception as ex:
        await log_error(bot, "botmanager.py", ex)

@bot.on(events.NewMessage(pattern=r"^\.bots$"))
async def bots_cmd(e):
    if not is_owner(e):
        return
    try:
        bots = list_running_bots()
        msg = await e.respond("🤖 Bots:\n" + "\n".join(bots) if bots else "No bots running")
        await auto_delete(msg, 8)
    except Exception as ex:
        await log_error(bot, "botmanager.py", ex)

@bot.on(events.NewMessage(pattern=r"^\.delbot(\s|$)"))
async def del_bot(e):
    if not is_owner(e):
        return
    try:
        name = e.raw_text.split(maxsplit=1)[1].lower()
        del_var(f"BOT_{name.upper()}")
        msg = await e.respond("🗑 Bot removed")
        await auto_delete(msg, 5)
    except Exception as ex:
        await log_error(bot, "botmanager.py", ex)
