# plugins/rpg_duel.py

import random
from telethon import events

from userbot import bot
from utils.players_helper import get_player, save_players
from utils.inventory_helper import get_equipped, damage_items, repair_item
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "rpg_duel.py"

mark_plugin_loaded(PLUGIN_NAME)
print("✔ rpg_duel.py loaded (RPG DUEL MODE)")

# =====================
# HELP
# =====================
register_help(
    "rpg",
    ".challenge (reply)\n"
    ".repair weapon\n"
    ".repair defense\n\n"
    "• RPG text-based duel\n"
    "• Weapon & defense durability\n"
    "• Coin loss & repair system"
)

# =====================
# CHALLENGE
# =====================
@bot.on(events.NewMessage(pattern=r"\.challenge$"))
async def challenge(e):
    if not e.is_reply:
        return

    try:
        await e.delete()

        me = await e.get_sender()
        opp_msg = await e.get_reply_message()
        opp = await opp_msg.get_sender()

        data, p1 = get_player(me.id, me.first_name)
        _, p2 = get_player(opp.id, opp.first_name)

        eq1 = get_equipped(p1)
        eq2 = get_equipped(p2)

        atk1 = p1["attack"] + (eq1["weapon"]["attack"] if eq1["weapon"] else 0)
        def1 = p1["defense"] + (eq1["defense"]["defense"] if eq1["defense"] else 0)

        atk2 = p2["attack"] + (eq2["weapon"]["attack"] if eq2["weapon"] else 0)
        def2 = p2["defense"] + (eq2["defense"]["defense"] if eq2["defense"] else 0)

        dmg1 = max(1, atk1 - def2 + random.randint(-2, 2))
        dmg2 = max(1, atk2 - def1 + random.randint(-2, 2))

        # decide winner
        if dmg1 > dmg2:
            winner, loser = p1, p2
            win_dmg, lose_dmg = dmg1, dmg2
        else:
            winner, loser = p2, p1
            win_dmg, lose_dmg = dmg2, dmg1

        # effects
        loser["coins"] = max(0, loser["coins"] - 10)
        winner["coins"] += 15

        damage_items(loser, weapon_dmg=10, defense_dmg=8)
        damage_items(winner, weapon_dmg=4, defense_dmg=3)

        save_players(data)

        await e.reply(
            f"⚔️ **RPG DUEL RESULT** ⚔️\n\n"
            f"🥇 Winner: **{winner['name']}** (+15 💰)\n"
            f"💀 Loser: {loser['name']} (-10 💰)\n\n"
            f"🗡 Weapon damage taken\n"
            f"🛡 Defense damage taken\n\n"
            f"🔧 Use `.repair weapon` or `.repair defense`"
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# REPAIR
# =====================
@bot.on(events.NewMessage(pattern=r"\.repair (weapon|defense)$"))
async def repair(e):
    try:
        item = e.pattern_match.group(1)
        user = await e.get_sender()

        data, p = get_player(user.id, user.first_name)

        cost = 20
        if p["coins"] < cost:
            await e.reply("❌ Not enough coins to repair")
            return

        p["coins"] -= cost
        repair_item(p, item, 40)

        save_players(data)

        await e.reply(
            f"🔧 **REPAIRED {item.upper()}**\n"
            f"💰 Cost: 20 coins"
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
