# plugins/exec.py

import traceback
import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import register_explain
from utils.logger import log_error
from utils.auto_delete import auto_delete
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "exec.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ exec.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "dev",
    ".exec CODE\n\n"
    "Execute raw python code (unsafe)\n"
    "• No auto return\n"
    "• Async + multiline supported\n"
    "• Owner only"
)

# =====================
# EXPLANATION REGISTER
# =====================
register_explain(
    "exec",
    {
        "title": "Exec – Raw Python Executor",
        "description": (
            "Exec plugin raw python code execute karta hai.\n"
            "Isme koi auto return ya safety check nahi hota.\n\n"
            "⚠️ Ye eval se zyada powerful aur zyada dangerous hai."
        ),
        "commands": [
            ".exec print('Hello')",
            ".exec await bot.send_message(event.chat_id, 'Hi')",
            ".exec for i in range(3): print(i)"
        ],
        "use_cases": [
            "Deep debugging",
            "Direct Telegram API calls",
            "Emergency fixes",
            "Advanced testing"
        ],
        "notes": [
            "Infinite loop bot ko hang kar sakta hai",
            "System damage possible",
            "Public groups me use mat karo",
            "Eval zyada safe option hai"
        ]
    }
)

MAX_LEN = 3500  # Telegram safe limit

# =====================
# SAFE SEND (AUTO DELETE)
# =====================
async def send_long(chat_id, text, delete_after=12):
    msgs = []
    for i in range(0, len(text), MAX_LEN):
        msg = await bot.send_message(chat_id, text[i:i + MAX_LEN])
        msgs.append(msg)

    for m in msgs:
        await auto_delete(m, delete_after)

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
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.exec python_code"
            )
            return await auto_delete(msg, 6)

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
                "async def __exec_func():\n"
                + "\n".join(f"    {line}" for line in code.split("\n")),
                env
            )

            await env["__exec_func"]()

            output = "\n".join(stdout) if stdout else "✅ Executed successfully"

            await send_long(
                e.chat_id,
                f"✅ OUTPUT:\n{output}",
                delete_after=12
            )

        except Exception:
            err = traceback.format_exc()
            await send_long(
                e.chat_id,
                f"❌ ERROR:\n{err}",
                delete_after=18
            )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
