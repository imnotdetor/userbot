import asyncio
from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error


@Client.on_message(owner_only & filters.command("tag", "."))
async def tag_user(client: Client, m):
    try:
        try:
            await m.delete()
        except:
            pass

        if len(m.command) < 3:
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.tag <count> <text> <@username>"
            )
            await auto_delete(msg, 5)
            return

        count = int(m.command[1])

        # full text after count
        full = m.text.split(None, 2)[2]

        # last word = username
        username = full.split()[-1]
        text = full.replace(username, "").strip()

        if not username.startswith("@"):
            username = "@" + username

        for _ in range(count):
            await client.send_message(
                m.chat.id,
                f"{text} {username}"
            )
            await asyncio.sleep(1.3)

    except Exception as e:
        await log_error(client, "tag.py", e)
