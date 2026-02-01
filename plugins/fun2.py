# plugins/fun2.py

import asyncio
import random
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "fun2.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ fun2.py loaded (FUN + REPLY ANIMATION MODE)")

# =====================
# HELP
# =====================
register_help(
    "fun2",
    ".hack (reply)\n"
    ".hackip (reply)\n"
    ".decrypt (reply)\n"
    ".scan (reply)\n"
    ".pingpong\n"
    ".dice | .coin | .slot | .rps\n"
    ".race | .loading | .math | .love | .shoot\n\n"
    "• Reply-based fake hacking games\n"
    "• Animations via message edit\n"
    "• 100% fun, zero harm 😄"
)

# =====================
# UTILS
# =====================
async def animate(msg, frames, delay=0.7):
    for f in frames:
        await msg.edit(f)
        await asyncio.sleep(delay)

async def get_target(e):
    if e.is_reply:
        r = await e.get_reply_message()
        u = await r.get_sender()
        name = u.first_name or "User"
        return f"🎯 **Target:** {name}\n\n"
    return ""

# =====================
# HACK
# =====================
@bot.on(events.NewMessage(pattern=r"\.hack$"))
async def hack_game(e):
    try:
        target = await get_target(e)
        await e.delete()

        m = await e.reply("💻 Initializing hack module...")
        frames = [
            f"{target}💻 Connecting █▒▒▒▒▒ 10%",
            f"{target}💻 Firewall bypass ███▒▒ 30%",
            f"{target}💻 Injecting █████▒ 55%",
            f"{target}💻 Cracking ███████ 80%",
            f"{target}✅ **HACK COMPLETE** 🔓"
        ]
        await animate(m, frames, 0.8)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# HACK IP
# =====================
@bot.on(events.NewMessage(pattern=r"\.hackip$"))
async def hack_ip(e):
    try:
        target = await get_target(e)
        fake_ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
        await e.delete()

        m = await e.reply("📡 Tracing IP...")
        frames = [
            f"{target}📡 Routing packets...",
            f"{target}🔍 Scanning ports...",
            f"{target}🌍 IP FOUND: `{fake_ip}`",
            f"{target}✅ Trace complete 😎"
        ]
        await animate(m, frames, 0.9)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# DECRYPT
# =====================
@bot.on(events.NewMessage(pattern=r"\.decrypt$"))
async def decrypt_game(e):
    try:
        target = await get_target(e)
        await e.delete()

        m = await e.reply("🔐 Decryption started...")
        frames = [
            f"{target}🔐 AES module loaded",
            f"{target}🔐 Bruteforce ░░░░",
            f"{target}🔓 DECRYPTED ✔️",
        ]
        await animate(m, frames, 0.8)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# SCAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.scan$"))
async def scan_game(e):
    try:
        target = await get_target(e)
        await e.delete()

        m = await e.reply("🧪 Scanning system...")
        frames = [
            f"{target}🧪 Memory OK",
            f"{target}🧪 Network OK",
            f"{target}🧪 Security OK",
            f"{target}✅ No threats found"
        ]
        await animate(m, frames, 0.6)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# PING PONG
# =====================
@bot.on(events.NewMessage(pattern=r"\.pingpong$"))
async def pingpong(e):
    try:
        await e.delete()
        m = await e.reply("🏓 Match starting...")
        frames = [
            "🏓 |●        |",
            "🏓 |   ●     |",
            "🏓 |      ●  |",
            "🏓 |   ●     |",
            "🏓 |●        |",
        ]
        for _ in range(3):
            for f in frames:
                await m.edit(f"🎮 **PING PONG**\n\n`{f}`")
                await asyncio.sleep(0.35)
        await m.edit("🏁 **MATCH OVER** 🏓\nGG 😄")

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# SMALL GAMES
# =====================
@bot.on(events.NewMessage(pattern=r"\.dice$"))
async def dice(e):
    await e.reply(f"🎲 Dice: **{random.randint(1,6)}**")

@bot.on(events.NewMessage(pattern=r"\.coin$"))
async def coin(e):
    await e.reply(f"🪙 {random.choice(['HEADS','TAILS'])}")

@bot.on(events.NewMessage(pattern=r"\.slot$"))
async def slot(e):
    s = ["🍒","🍋","⭐","💎"]
    r = [random.choice(s) for _ in range(3)]
    txt = "🎰 " + " | ".join(r)
    if len(set(r)) == 1:
        txt += "\n🎉 JACKPOT!"
    await e.reply(txt)

@bot.on(events.NewMessage(pattern=r"\.rps$"))
async def rps(e):
    await e.reply(f"✊✋✌️ **{random.choice(['ROCK','PAPER','SCISSORS'])}**")

@bot.on(events.NewMessage(pattern=r"\.race$"))
async def race(e):
    m = await e.reply("🏎 Ready...")
    await animate(m, ["🏎💨","🏎💨💨","🏁 WINNER!"], 0.6)

@bot.on(events.NewMessage(pattern=r"\.loading$"))
async def loading(e):
    m = await e.reply("Loading ░░░")
    await animate(m, ["Loading █░░","Loading ██░","Loading ███","✅ Done"], 0.4)

@bot.on(events.NewMessage(pattern=r"\.math$"))
async def math(e):
    a,b = random.randint(1,50), random.randint(1,50)
    await e.reply(f"🧮 {a} + {b} = ?")

@bot.on(events.NewMessage(pattern=r"\.love$"))
async def love(e):
    await e.reply(f"❤️ Love: **{random.randint(1,100)}%**")

@bot.on(events.NewMessage(pattern=r"\.shoot$"))
async def shoot(e):
    m = await e.reply("🎯 Aiming...")
    await animate(m, ["🎯 Aim","💥 BOOM","☠️ Target down"], 0.6)
