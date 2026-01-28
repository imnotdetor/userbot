import traceback
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("exec.py")
print("✔ exec.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "dev",
    ".exec CODE\n\n"
    "Execute python code (unsafe)\n"
    "• Owner only\n"
    "• Supports async / multiline code\n"
    "• Print output supported"
)

MAX_LEN = 3500  # telegram safe limit


# =====================
# SAFE SEND
# =====================
async def send_long(chat_id, text):
    for i in range(0, len(text), MAX_LEN):
        await bot.send_message(chat_id, text[i:i + MAX_LEN])


# =====================
# EXEC COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.exec(?:\s+([\s\S]+))?$"))
async def exec_cmd(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except:
            pass

        code = e.pattern_match.group(1)
        if not code:
            await bot.send_message(
                e.chat_id,
                "Usage:\n.exec python_code"
            )
            return

        stdout = []

        def fake_print(*args):
            stdout.append(" ".join(str(a) for a in args))

        env = {
            "bot": bot,
            "event": e,
            "e": e,
            "asyncio": asyncio,
            "print": fake_print
        }

        try:
            exec(
                f"async def __exec():\n"
                + "\n".join(f"    {line}" for line in code.split("\n")),
                env
            )

            await env["__exec"]()

            output = "\n".join(stdout) if stdout else "✅ Executed successfully"

            await send_long(
                e.chat_id,
                f"✅ OUTPUT:\n{output}"
            )

        except Exception:
            err = traceback.format_exc()
            await send_long(
                e.chat_id,
                f"❌ ERROR:\n{err}"
            )

    except Exception as ex:
        mark_plugin_error("exec.py", ex)
        await log_error(bot, "exec.py", ex)
