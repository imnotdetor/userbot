from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    set_var,
    get_var,
    del_var,
    all_vars,
    auto_delete,
    log_error,
    mark_plugin_loaded,
    register_help          # 🔥 HELP4
)

# 🔥 mark plugin loaded (health system)
mark_plugin_loaded("vars.py")

# 🔥 HELP4 AUTO REGISTER
register_help(
    "vars",
    """
VARIABLES / CONFIG

.setvar <KEY> <VALUE>
exm: .setvar API_TOKEN 123456

.getvar <KEY>
exm: .getvar API_TOKEN

.delvar <KEY>
exm: .delvar API_TOKEN

.vars
exm: .vars

• Variables are stored permanently
• Used by botmanager, autoreply, etc.
"""
)

# =====================
# SET VAR
# =====================
@Client.on_message(owner_only & filters.command("setvar", "."))
async def setvar_cmd(client, m):
    try:
        await m.delete()

        if len(m.command) < 3:
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.setvar KEY VALUE"
            )
            await auto_delete(msg, 5)
            return

        key = m.command[1].upper()
        value = m.text.split(None, 2)[2]

        set_var(key, value)

        msg = await client.send_message(
            m.chat.id,
            f"✅ Variable saved\n`{key}`"
        )
        await auto_delete(msg, 5)

    except Exception as e:
        await log_error(client, "vars.py", e)


# =====================
# GET VAR
# =====================
@Client.on_message(owner_only & filters.command("getvar", "."))
async def getvar_cmd(client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.getvar KEY"
            )
            await auto_delete(msg, 5)
            return

        key = m.command[1].upper()
        value = get_var(key)

        if value is None:
            msg = await client.send_message(
                m.chat.id,
                "❌ Variable not found"
            )
        else:
            msg = await client.send_message(
                m.chat.id,
                f"`{key}` = `{value}`"
            )

        await auto_delete(msg, 10)

    except Exception as e:
        await log_error(client, "vars.py", e)


# =====================
# DELETE VAR
# =====================
@Client.on_message(owner_only & filters.command("delvar", "."))
async def delvar_cmd(client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.delvar KEY"
            )
            await auto_delete(msg, 5)
            return

        key = m.command[1].upper()
        del_var(key)

        msg = await client.send_message(
            m.chat.id,
            f"🗑 Variable deleted: `{key}`"
        )
        await auto_delete(msg, 5)

    except Exception as e:
        await log_error(client, "vars.py", e)


# =====================
# LIST VARS
# =====================
@Client.on_message(owner_only & filters.command("vars", "."))
async def vars_cmd(client, m):
    try:
        await m.delete()

        data = all_vars()

        if not data:
            msg = await client.send_message(
                m.chat.id,
                "No variables saved"
            )
            await auto_delete(msg, 5)
            return

        text = "📦 SAVED VARIABLES\n\n"
        for k in data:
            text += f"• `{k}`\n"

        msg = await client.send_message(m.chat.id, text)
        await auto_delete(msg, 15)

    except Exception as e:
        await log_error(client, "vars.py", e)
