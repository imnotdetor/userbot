import asyncio
from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error


@Client.on_message(owner_only & filters.command("tag", "."))
async def tag_user(client: Client, m):
    try:
        # delete command safely
        try:
            await m.delete()
        except:
            pass

        if len(m.command) < 3:
            msg = await client.send_message(
                m.chat.id,
                "❌ Usage:\n.tag <count> <text> <@username>"
            )
            await auto_delete(msg, 5)
            return

        # validate count
        if not m.command[1].isdigit():
            msg = await client.send_message(
                m.chat.id,
                "❌ Count must be a number"
            )
            await auto_delete(msg, 4)
            return

        count = int(m.command[1])

        if count < 1 or count > 20:
            msg = await client.send_message(
                m.chat.id,
                "❌ Count must be between 1 and 20"
            )
            await auto_delete(msg, 4)
            return

        full_text = m.text.split(None, 2)[2]
        parts = full_text.split()

        username = parts[-1]
        text = " ".join(parts[:-1])

        if not username.startswith("@"):
            username = "@" + username

        if not text:
            text = "Hey"

        for i in range(count):
            await client.send_message(
                m.chat.id,
                f"{text} {username}"
            )
            await asyncio.sleep(1.5)  # flood safe

    except Exception as e:
        await log_error(client, "tag.py", e)
