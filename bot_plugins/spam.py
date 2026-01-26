from pyrogram import Client, filters

@Client.on_message(filters.command("spam"))
async def spam(_, m):
    await m.reply("I am a spam bot 😈")
