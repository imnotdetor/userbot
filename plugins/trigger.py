# Triggered Meme Plugin
# Converted for Telethon Userbot
# Original credits respected

import os
from requests import get
from telegraph import upload_file as uplu
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "ptrigger.py"
print("✔ ptrigger.py loaded (Triggered Meme)")


@bot.on(events.NewMessage(pattern=r"\.ptrigger$"))
async def ptrigger(e):
    try:
        if not e.is_reply:
            return await e.edit("❌ Reply to a message!")

        msg = await e.edit("⚙️ Processing...")

        reply = await e.get_reply_message()
        user = await reply.get_sender()

        # Download profile photo
        foto = await bot.download_profile_photo(user.id)
        if not foto:
            return await msg.edit("❌ Replied user has no profile photo!")

        # Upload to telegraph
        avatar = uplu(foto)
        img_url = f"https://telegra.ph{avatar[0]}"

        # Triggered GIF via working API
        r = get(
            f"https://api.popcat.xyz/triggered?image={img_url}",
            allow_redirects=True
        )

        with open("triggered.gif", "wb") as f:
            f.write(r.content)

        # Send GIF
        await bot.send_file(
            e.chat_id,
            "triggered.gif",
            caption="**Triggered 😡**",
            reply_to=reply.id
        )

        await msg.delete()

        # Cleanup
        os.remove(foto)
        os.remove("triggered.gif")

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        mark_plugin_error(PLUGIN_NAME)


mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "ptrigger",
    ".ptrigger (reply)\n\n"
    "• Creates a triggered meme from user's profile photo\n"
    "• Reply required\n"
    "• Uses working API"
)