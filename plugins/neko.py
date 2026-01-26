from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error, mark_plugin_loaded
import os
import random

mark_plugin_loaded("neko.py")

NEKO_FOLDERS = {
    "neko": "assets/neko",
    "nekokiss": "assets/nekokiss",
    "nekohug": "assets/nekohug",
    "nekofuck": "assets/nekofuck",
    "nekoslap": "assets/nekoslap",
}

SUPPORTED_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4")


@Client.on_message(owner_only & filters.command(
    ["neko", "nekokiss", "nekohug", "nekofuck", "nekoslap"], "."
))
async def neko_handler(client: Client, m):
    try:
        try:
            await m.delete()
        except:
            pass

        cmd = m.command[0].lower()
        folder = NEKO_FOLDERS.get(cmd)

        if not folder or not os.path.isdir(folder):
            msg = await client.send_message(
                m.chat.id,
                f"❌ Folder missing for `{cmd}`"
            )
            await auto_delete(msg, 5)
            return

        files = [
            f for f in os.listdir(folder)
            if f.lower().endswith(SUPPORTED_EXT)
        ]

        if not files:
            msg = await client.send_message(
                m.chat.id,
                f"❌ No media found for `{cmd}`"
            )
            await auto_delete(msg, 5)
            return

        file_path = os.path.join(folder, random.choice(files))

        sent = await client.send_document(
            m.chat.id,
            file_path,
            caption=f"😺 {cmd}~"
        )

        # auto delete after 30 sec
        await auto_delete(sent, 30)

    except Exception as e:
        await log_error(client, "neko.py", e)
