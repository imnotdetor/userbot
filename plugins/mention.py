from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import log_error, mark_plugin_loaded

mark_plugin_loaded("mention.py")

MAX_MENTIONS_ADMIN = 25
MAX_MENTIONS_USER = 10


async def is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in ("administrator", "creator")
    except:
        return False


@Client.on_message(owner_only & filters.command("mention", "."))
async def mention_cmd(client: Client, m):
    try:
        if len(m.command) < 2:
            return

        chat_id = m.chat.id
        user_id = m.from_user.id
        text = m.text.split(None, 1)[1]

        try:
            await m.delete()
        except:
            pass

        admin = await is_admin(client, chat_id, user_id)
        limit = MAX_MENTIONS_ADMIN if admin else MAX_MENTIONS_USER

        users = []
        seen = set()

        async for msg in client.get_chat_history(chat_id, limit=200):
            u = msg.from_user
            if not u:
                continue
            if u.is_bot:
                continue
            if u.id in seen:
                continue

            seen.add(u.id)

            if u.username:
                users.append(f"@{u.username}")
            else:
                users.append(f"[{u.first_name}](tg://user?id={u.id})")

            if len(users) >= limit:
                break

        if not users:
            return

        mention_text = text + "\n\n" + " ".join(users)

        await client.send_message(
            chat_id,
            mention_text,
            disable_web_page_preview=True
        )

    except Exception as e:
        await log_error(client, "mention.py", e)
