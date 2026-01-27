from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error, mark_plugin_loaded

mark_plugin_loaded("styletext.py")

# =====================
# TEXT STYLES MAP
# =====================
STYLES = {
    "bold": lambda t: f"**{t}**",
    "italic": lambda t: f"__{t}__",
    "mono": lambda t: f"`{t}`",
    "strike": lambda t: f"~~{t}~~",
    "spoiler": lambda t: f"||{t}||",
    "emoji": lambda t: " ".join(f"{c}️⃣" for c in t if c.isalnum()),
    "space": lambda t: " ".join(list(t)),
}

# =====================
# STYLE HANDLER
# =====================
@Client.on_message(owner_only & filters.command(list(STYLES.keys()), "."))
async def style_handler(client: Client, m):
    try:
        # ⚠️ delete baad me, pehle kaam hone do
        if len(m.command) < 2:
            msg = await m.reply(
                "Usage:\n"
                ".bold text\n"
                ".italic text\n"
                ".mono text\n"
                ".strike text\n"
                ".spoiler text\n"
                ".emoji text\n"
                ".space text"
            )
            await auto_delete(msg, 6)
            return

        cmd = m.command[0].lower()
        text = m.text.split(None, 1)[1]

        styled = STYLES[cmd](text)

        msg = await m.reply(styled)
        await auto_delete(msg, 40)

        # command delete LAST me
        try:
            await m.delete()
        except:
            pass

    except Exception as e:
        await log_error(client, "styletext.py", e)
