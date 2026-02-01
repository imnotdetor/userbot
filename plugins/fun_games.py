import asyncio
import random
from telethon import events
from utils.leaderboard_helper import record_match, get_mvp, load_lb

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
    ".snake\n"
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

                
# =====================
# ADVANCED SNAKE GAME
# =====================

# =====================
# HELPERS
# =====================
def hp_bar(hp):
    blocks = max(0, min(10, hp // 10))
    return "█" * blocks + "░" * (10 - blocks)

# =====================
# SNAKE GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.snake$"))
async def snake_game(e):
    try:
        await e.delete()

        # opponent detect
        if e.is_reply:
            r = await e.get_reply_message()
            u = await r.get_sender()
            opp_id = str(u.id)
            opp_name = u.first_name or "User"
        else:
            opp_id = "anaconda"
            opp_name = "Anaconda 🐍"

        cobra_id = "cobra"
        cobra_name = "King Cobra 🐍"

        # init animation
        m = await e.reply("🐍 **SNAKE BATTLE INITIALIZING...**")
        for f in [
            "🐍 Loading venom modules...",
            "🐍 Preparing arena...",
            "🐍 Calculating abilities...",
            "🐍 **BATTLE STARTING** ⚔️"
        ]:
            await m.edit(f)
            await asyncio.sleep(0.6)

        wins_cobra = 0
        wins_opp = 0

        # ===== BEST OF 3 =====
        for round_no in range(1, 4):
            hp_cobra, hp_opp = 100, 100
            poison_opp = 0

            await m.edit(
                f"🎮 **ROUND {round_no}**\n\n"
                f"🐍 **{cobra_name}**\n`[{hp_bar(hp_cobra)}]` {hp_cobra}%\n\n"
                f"🐍 **{opp_name}**\n`[{hp_bar(hp_opp)}]` {hp_opp}%"
            )
            await asyncio.sleep(1)

            while hp_cobra > 0 and hp_opp > 0:
                attacker = random.choice(["cobra", "opp"])
                dmg = random.randint(10, 20)

                crit = random.random() < 0.25
                poison = random.random() < 0.20
                regen = random.random() < 0.15

                if crit:
                    dmg *= 2

                if attacker == "cobra":
                    hp_opp -= dmg
                    text = f"🐍 {cobra_name} attacks `{opp_name}`"
                    if poison:
                        poison_opp = 2
                else:
                    hp_cobra -= dmg
                    text = f"🐍 {opp_name} attacks {cobra_name}"

                if poison_opp > 0:
                    hp_opp -= 5
                    poison_opp -= 1
                    text += " ☠️ POISON"

                if regen:
                    hp_cobra = min(100, hp_cobra + 5)
                    text += " 💚 REGEN"

                hp_cobra = max(0, hp_cobra)
                hp_opp = max(0, hp_opp)

                await m.edit(
                    f"{text}{' 💥 CRIT' if crit else ''}\n\n"
                    f"🐍 **{cobra_name}**\n`[{hp_bar(hp_cobra)}]` {hp_cobra}%\n\n"
                    f"🐍 **{opp_name}**\n`[{hp_bar(hp_opp)}]` {hp_opp}%"
                )
                await asyncio.sleep(1.2)

            if hp_cobra > hp_opp:
                wins_cobra += 1
                await m.edit(f"🏆 **ROUND {round_no} WINNER:** {cobra_name}")
            else:
                wins_opp += 1
                await m.edit(f"🏆 **ROUND {round_no} WINNER:** {opp_name}")

            await asyncio.sleep(1.4)

        # ===== RECORD MATCH (UNIVERSAL) =====
        if wins_opp > wins_cobra:
            record_match(
                game="snake",
                winner_id=opp_id,
                winner_name=opp_name,
                loser_id=cobra_id,
                loser_name=cobra_name
            )
            winner = opp_name
        else:
            record_match(
                game="snake",
                winner_id=cobra_id,
                winner_name=cobra_name,
                loser_id=opp_id,
                loser_name=opp_name
            )
            winner = cobra_name

        await m.edit(
            f"🏁 **MATCH OVER**\n\n"
            f"🐍 {cobra_name} Wins: `{wins_cobra}`\n"
            f"🐍 {opp_name} Wins: `{wins_opp}`\n\n"
            f"🥇 **FINAL WINNER:** `{winner}`\n"
            f"📊 Stats saved ✔"
        )
        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# BATTLE STATS
# =====================
@bot.on(events.NewMessage(pattern=r"\.battlestats$"))
async def battlestats(e):
    try:
        await e.delete()

        db = load_lb()
        game = db.get("snake", {}).get("players", {})

        if not game:
            m = await e.reply("📊 No snake battles yet")
            await asyncio.sleep(8)
            await m.delete()
            return

        players = sorted(
            game.values(),
            key=lambda p: (p["wins"], -p["losses"], p["battles"]),
            reverse=True
        )

        text = "🐍 **SNAKE LEADERBOARD** 🏆\n\n"
        for i, p in enumerate(players[:10], 1):
            text += (
                f"**{i}. {p['name']}**\n"
                f"🏆 Wins: `{p['wins']}` | ❌ Losses: `{p['losses']}`\n"
                f"⚔ Battles: `{p['battles']}`\n\n"
            )

        m = await e.reply(text)
        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# MVP
# =====================
@bot.on(events.NewMessage(pattern=r"\.mvp$"))
async def mvp_stats(e):
    try:
        await e.delete()
        best = get_mvp("snake")

        if not best:
            m = await e.reply("🏆 No MVP yet")
            await asyncio.sleep(8)
            await m.delete()
            return

        win_rate = round((best["wins"] / best["battles"]) * 100, 1) if best["battles"] else 0
        score = (best["wins"] * 3) + best["battles"]

        text = (
            "🏆 **MVP OF THE SNAKE BATTLES** 🏆\n\n"
            f"👑 **{best['name']}**\n\n"
            f"🏆 Wins: `{best['wins']}`\n"
            f"❌ Losses: `{best['losses']}`\n"
            f"⚔ Battles: `{best['battles']}`\n"
            f"📊 Win Rate: `{win_rate}%`\n"
            f"⭐ MVP Score: `{score}`"
        )

        m = await e.reply(text)
        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
