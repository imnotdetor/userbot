from telethon import events
from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded

PLUGIN_NAME = "phishing_demo.py"
mark_plugin_loaded(PLUGIN_NAME)

register_help(
    "phishingdemo",
    ".phishdemo\n\n"
    "• Shows how phishing captures credentials\n"
    "• Redacted & safe demo"
)

@bot.on(events.NewMessage(pattern=r"\.phishdemo$"))
async def phishdemo(e):
    await e.reply(
        "🧪 **PHISHING AWARENESS DEMO**\n\n"
        "If this were a real phishing page:\n"
        "• Username would be captured\n"
        "• Password would be stolen\n\n"
        "In this demo:\n"
        "✔ Password is never stored\n"
        "✔ Only masked info shown\n\n"
        "Stay safe online 🔐"
    )
