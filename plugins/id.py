from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help
)
import asyncio

# =====================
# PLUGIN INIT
# =====================
mark_plugin_loaded("id.py")

register_help(
    "info",
    """
.id
Get your ID, chat ID, replied user ID, or channel ID.
"""
)

# =====================
# ID COMMAND
# =====================
@Client.on_message(owner_only & filters.command("id", "."))
async def get_id(client: Client, m):
    try:
        text = "🆔 **ID INFO**\n\n"

        # 👤 YOUR ID
        if m.from_user:
            text += f"🙋‍♂️ Your ID: `{m.from_user.id}`\n"

        # 💬 CHAT INFO
        if m.chat:
            text += f"💬 Chat ID: `{m.chat.id}`\n"
            text += f"📌 Chat Type: `{m.chat.type}`\n"

        # 🔐 PRIVATE CHAT → OTHER USER
        if m.chat.type == "private" and m.chat.id != m.from_user.id:
            text += f"\n👤 Other User ID: `{m.chat.id}`"

        # ↩️ REPLY CASE
        if m.reply_to_message:
            if m.reply_to_message.from_user:
                text += (
                    f"\n↩️ Replied User ID: "
                    f"`{m.reply_to_message.from_user.id}`"
                )
            elif m.reply_to_message.sender_chat:
                text += (
                    f"\n↩️ Replied Channel ID: "
                    f"`{m.reply_to_message.sender_chat.id}`"
                )

        result = await m.reply(text)

        # ❌ delete command after 1 sec
        async def delete_cmd():
            await asyncio.sleep(1)
            try:
                await m.delete()
            except:
                pass

        # ⏱ delete result after 15 sec
        async def delete_result():
            await asyncio.sleep(15)
            try:
                await result.delete()
            except:
                pass

        asyncio.create_task(delete_cmd())
        asyncio.create_task(delete_result())

    except Exception as e:
        mark_plugin_error("id.py", e)
        await log_error(client, "id.py", e)
