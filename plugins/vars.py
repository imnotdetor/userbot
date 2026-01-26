from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    set_var, get_var, del_var, all_vars,
    auto_delete, log_error, mark_plugin_loaded
)

mark_plugin_loaded("vars.py")

@Client.on_message(owner_only & filters.command("setvar", "."))
async def setvar_cmd(client, m):
    try:
        if len(m.command) < 3:
            msg = await m.reply("Usage:\n.setvar KEY VALUE")
            await auto_delete(msg, 5)
            return

        key = m.command[1].upper()
        value = m.text.split(None, 2)[2]

        set_var(key, value)
        msg = await m.reply(f"✅ Variable set:\n{key}")
        await auto_delete(msg, 5)

    except Exception as e:
        await log_error(client, "vars.py", e)


@Client.on_message(owner_only & filters.command("getvar", "."))
async def getvar_cmd(client, m):
    try:
        if len(m.command) < 2:
            msg = await m.reply("Usage:\n.getvar KEY")
            await auto_delete(msg, 5)
            return

        key = m.command[1].upper()
        value = get_var(key)

        if value is None:
            msg = await m.reply("❌ Variable not found")
        else:
            msg = await m.reply(f"{key} = `{value}`")

        await auto_delete(msg, 8)

    except Exception as e:
        await log_error(client, "vars.py", e)


@Client.on_message(owner_only & filters.command("delvar", "."))
async def delvar_cmd(client, m):
    try:
        if len(m.command) < 2:
            msg = await m.reply("Usage:\n.delvar KEY")
            await auto_delete(msg, 5)
            return

        key = m.command[1].upper()
        del_var(key)

        msg = await m.reply(f"🗑️ Deleted:\n{key}")
        await auto_delete(msg, 5)

    except Exception as e:
        await log_error(client, "vars.py", e)


@Client.on_message(owner_only & filters.command("vars", "."))
async def vars_cmd(client, m):
    try:
        vars_data = all_vars()

        if not vars_data:
            msg = await m.reply("No variables set")
            await auto_delete(msg, 5)
            return

        text = "📦 VARIABLES\n\n"
        for k in vars_data:
            text += f"• {k}\n"

        msg = await m.reply(text)
        await auto_delete(msg, 10)

    except Exception as e:
        await log_error(client, "vars.py", e)
