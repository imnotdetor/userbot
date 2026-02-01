import asyncio
import random
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "fun_games.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ fun_games.py loaded (GAMES MODE)")

# =====================
# HELP
# =====================
register_help(
    "fungames",
    ".tictactoe (reply)\n"
    ".battle @user\n"
    ".emojiwar\n"
    ".casino\n"
    ".virus\n\n"
    "• Reply based games\n"
    "• Fake animations\n"
    "• Auto delete commands 😄"
)

# =====================
# COMMON ANIMATION HELPER
# =====================
async def reply_animate(e, frames, delay=0.7):
    if e.is_reply:
        r = await e.get_reply_message()
        m = await r.reply(frames[0])
    else:
        m = await e.reply(frames[0])

    await e.delete()

    for f in frames[1:]:
        await asyncio.sleep(delay)
        await m.edit(f)

# =====================
# TIC TAC TOE (REPLY VS USER)
# =====================
@bot.on(events.NewMessage(pattern=r"\.tictactoe$"))
async def tictactoe(e):
    try:
        frames = [
            "❌ ⭕ ❌\n⭕ ❌ ⭕\n⬜ ⭕ ❌",
            "❌ ⭕ ❌\n⭕ ❌ ⭕\n❌ ⭕ ❌",
            "🏁 **GAME OVER**\nYou Wins 😎"
        ]
        await reply_animate(e, frames, 0.9)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# BATTLE GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.battle(?: (.*))?$"))
async def battle(e):
    try:
        target = e.pattern_match.group(1) or "Enemy"
        frames = [
            f"⚔️ Battle started vs {target}",
            "⚔️ Attacking...",
            "🛡 Enemy defending...",
            "💥 Critical hit!",
            "🏆 **YOU WON THE BATTLE**"
        ]
        await reply_animate(e, frames, 0.8)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# EMOJI WAR
# =====================
@bot.on(events.NewMessage(pattern=r"\.emojiwar$"))
async def emojiwar(e):
    try:
        frames = [
            "😀 😃 😄",
            "😡 😠 🤬",
            "💥 💣 💥",
            "😂 🤣 😂",
            "🏁 **EMOJI WAR OVER**"
        ]
        await reply_animate(e, frames, 0.6)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# CASINO GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.casino$"))
async def casino(e):
    try:
        slots = ["🍒", "🍋", "🍉", "⭐", "💎"]
        result = [random.choice(slots) for _ in range(3)]

        frames = [
            "🎰 Spinning...",
            f"🎰 {' '.join(result)}",
            "🎉 **JACKPOT!**" if len(set(result)) == 1 else "😢 You lost"
        ]
        await reply_animate(e, frames, 1.0)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# FAKE VIRUS PRANK
# =====================
@bot.on(events.NewMessage(pattern=r"\.virus$"))
async def fake_virus(e):
    try:
        frames = [
            "🦠 Virus detected...",
            "🦠 Infecting system...",
            "📂 Deleting files...",
            "⚠️ System unstable...",
            "💥 System crashed...",
            "😈 Just kidding!\n❌ No virus detected"
        ]
        await reply_animate(e, frames, 0.8)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
