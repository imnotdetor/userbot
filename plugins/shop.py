import asyncio
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.coins_helper import get_coins, spend
from utils.plugin_status import mark_plugin_loaded

PLUGIN_NAME = "shop.py"
mark_plugin_loaded(PLUGIN_NAME)

SHOP = {
    "emoji": 30,
    "vip": 200,
    "immunity": 100
}

register_help(
    "shop",
    ".coins\n"
    ".shop\n"
    ".buy <item>\n\n"
    "• Game coins system"
)

@bot.on(events.NewMessage(pattern=r"\.coins$"))
async def coins(e):
    c = get_coins(e.sender_id)
    await e.reply(f"💰 **Your Coins:** `{c}`")

@bot.on(events.NewMessage(pattern=r"\.shop$"))
async def shop(e):
    text = "🛒 **SHOP**\n\n"
    for i, p in SHOP.items():
        text += f"• `{i}` → 💰 {p}\n"
    await e.reply(text)

@bot.on(events.NewMessage(pattern=r"\.buy (\w+)"))
async def buy(e):
    item = e.pattern_match.group(1).lower()
    price = SHOP.get(item)

    if not price:
        await e.reply("❌ Item not found")
        return

    if not spend(e.sender_id, price):
        await e.reply("❌ Not enough coins")
        return

    await e.reply(f"✅ Bought **{item}** for 💰 {price}")
