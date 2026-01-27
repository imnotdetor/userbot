from pyrogram import Client, filters

@Client.on_message(filters.command("spambot"))
async def spam(_, m):
    await m.reply("I am a spam bot 😈")
