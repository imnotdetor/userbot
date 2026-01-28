from telethon import events
from userbot import bot
from utils.owner import is_owner

@bot.on(events.NewMessage(pattern=r"\.ownercheck$"))
async def owner_check(e):
    if is_owner(e):
        await e.reply("✅ You ARE owner")
    else:
        await e.reply(
            f"❌ NOT owner\nYour ID: {e.sender_id}"
        )
