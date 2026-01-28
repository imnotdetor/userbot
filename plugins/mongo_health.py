from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    check_mongo_health,
    auto_delete,
    mark_plugin_loaded,
    mark_plugin_error,
    log_error
)

mark_plugin_loaded("mongo_health.py")


@Client.on_message(owner_only & filters.command("mongo", "."))
async def mongo_health_cmd(client: Client, m):
    try:
        try:
            await m.delete()
        except:
            pass

        health = check_mongo_health()

        if health["ok"]:
            text = (
                "🟢 MONGO DB STATUS: CONNECTED\n\n"
                f"Database: `{health['db']}`\n"
                f"Collection: `{health['collection']}`\n"
                f"Time: `{health['time']}`"
            )
        else:
            text = (
                "🔴 MONGO DB STATUS: ERROR\n\n"
                f"Reason:\n`{health['error']}`"
            )

        msg = await m.reply(text)
        await auto_delete(msg, 10)

    except Exception as e:
        mark_plugin_error("mongo_health.py", e)
        await log_error(client, "mongo_health.py", e)
