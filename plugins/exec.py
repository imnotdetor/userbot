from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    log_error,
    mark_plugin_loaded,
    mark_plugin_error
)
import traceback

# 🔥 mark plugin loaded
mark_plugin_loaded("exec.py")


@Client.on_message(owner_only & filters.command("exec", prefixes="."))
async def exec_cmd(client: Client, m):
    try:
        await m.delete()

        code = m.text.split(" ", 1)
        if len(code) < 2:
            await m.reply("Usage: `.exec python_code`")
            return

        exec(code[1], globals())
        await m.reply("✅ Executed successfully")

    except Exception as e:
        mark_plugin_error("exec.py", e)
        await log_error(client, "exec.py", e)
        await m.reply(f"❌ Error:\n`{traceback.format_exc(limit=4)}`")
