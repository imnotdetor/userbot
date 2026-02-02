import random
import asyncio
import time
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "minigames.py"
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# ACTIVE GAMES
# =====================
active_guess_games = {}
# key = message_id
# value = {number, end}

# =====================
# START GUESS (OWNER ONLY)
# =====================
@bot.on(events.NewMessage(pattern=r"\.guess(?: (\d+) (\d+))?$"))
async def start_guess(e):
    if not is_owner(e):
        return  # 🔒 owner only

    try:
        await e.delete()

        # range
        if e.pattern_match.group(1):
            low = int(e.pattern_match.group(1))
            high = int(e.pattern_match.group(2))
            if low >= high:
                return
        else:
            low, high = 1, 10

        number = random.randint(low, high)
        end_time = time.time() + 30

        msg = await e.reply(
            f"🎯 **GUESS THE NUMBER**\n\n"
            f"Number range: **{low} – {high}**\n"
            f"⏱ Time limit: **30 seconds**\n\n"
            "👉 Reply to this message with your guess"
        )

        active_guess_games[msg.id] = {
            "number": number,
            "end": end_time
        }

        await asyncio.sleep(30)

        if msg.id in active_guess_games:
            correct = active_guess_games[msg.id]["number"]
            await msg.reply(
                f"⏰ **TIME UP!**\n\n"
                f"❌ No one guessed it\n"
                f"🎯 Correct number: `{correct}`"
            )
            del active_guess_games[msg.id]

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# HANDLE REPLIES (MULTIPLAYER)
# =====================
@bot.on(events.NewMessage)
async def handle_guess(e):
    try:
        if not e.is_reply:
            return

        reply = await e.get_reply_message()
        if not reply or reply.id not in active_guess_games:
            return

        game = active_guess_games[reply.id]

        # time over
        if time.time() > game["end"]:
            del active_guess_games[reply.id]
            return

        try:
            guess = int(e.raw_text.strip())
        except ValueError:
            return

        correct = game["number"]

        if guess == correct:
            await e.reply(
                f"🎉 **CORRECT GUESS!**\n\n"
                f"👑 Winner: **{e.sender.first_name}**\n"
                f"🎯 Number: `{correct}`"
            )
            del active_guess_games[reply.id]
        else:
            await e.reply(f"❌ `{guess}` is wrong")

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
