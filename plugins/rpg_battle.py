import asyncio, random
from telethon import events
from userbot import bot
from utils.players_helper import get_player, save_players
from utils.owner import is_owner

@bot.on(events.NewMessage(pattern=r"\.fight$"))
async def fight(e):
    if not e.is_reply:
        return

    await e.delete()

    me = await e.get_sender()
    opp_msg = await e.get_reply_message()
    opp = await opp_msg.get_sender()

    data, p1 = get_player(me.id, me.first_name)
    _, p2 = get_player(opp.id, opp.first_name)

    hp1, hp2 = p1["hp"], p2["hp"]

    msg = await e.reply(f"⚔️ **BATTLE START**\n{p1['name']} vs {p2['name']}")

    while hp1 > 0 and hp2 > 0:
        dmg1 = max(5, p1["attack"] - p2["defense"] + random.randint(-3,3))
        dmg2 = max(5, p2["attack"] - p1["defense"] + random.randint(-3,3))

        hp2 -= dmg1
        hp1 -= dmg2

        await msg.edit(
            f"⚔️ **BATTLE**\n\n"
            f"{p1['name']} ❤️ {max(0,hp1)}\n"
            f"{p2['name']} ❤️ {max(0,hp2)}"
        )
        await asyncio.sleep(1)

    if hp1 > hp2:
        winner, loser = p1, p2
        winner["coins"] += 20
        result = f"🏆 **WINNER:** {winner['name']} (+20 💰)"
    else:
        winner, loser = p2, p1
        winner["coins"] += 20
        result = f"🏆 **WINNER:** {winner['name']} (+20 💰)"

    save_players(data)
    await msg.edit(result)
