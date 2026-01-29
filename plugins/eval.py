# plugins/eval.py

import traceback
import asyncio
import ast
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import register_explain
from utils.logger import log_error
from utils.auto_delete import auto_delete

PLUGIN_NAME = "eval.py"
print("✔ eval.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "dev",
    ".eval CODE\n\n"
    "Execute python code dynamically\n"
    "• Auto return last expression\n"
    "• Async + multiline supported\n"
    "• Owner only"
)

# =====================
# EXPLANATION REGISTER
# =====================
register_explain(
    "eval",
    {
        "title": "Eval – Live Python Executor",
        "description": (
            "Eval plugin live Python code execute karta hai.\n"
            "Ye debugging, testing aur quick experiments ke liye use hota hai.\n\n"
            "⚠️ Extremely powerful command – sirf OWNER ke liye."
        ),
        "commands": [
            ".eval 1 + 1",
            ".eval print('Hello')",
            ".eval await bot.get_me()",
            ".eval for i in range(3): print(i)"
        ],
        "use_cases": [
            "Bot debugging",
            "Live variable inspection",
            "Quick math & logic test",
            "Telegram API experiments"
        ],
        "notes": [
            "Public groups me use mat karo",
            "Infinite loop bot ko hang kar sakta hai",
            "Sensitive data leak ho sakta hai"
        ]
    }
)

MAX_LEN = 3500  # Telegram safe limit

# =====================
# SAFE SEND (AUTO DELETE)
# =====================
async def send_long(chat_id, text, delete_after=10):
    msgs = []
    for i in range(0, len(text), MAX_LEN):
        msg = await bot.send_message(chat_id, text[i:i + MAX_LEN])
        msgs.append(msg)

    for m in msgs:
        await auto_delete(m, delete_after)

# =====================
# AUTO RETURN FIX
# =====================
def wrap_code(code: str) -> str:
    """
    Automatically return last expression if no explicit return
    """
    tree = ast.parse(code)

    if tree.body and isinstance(tree.body[-1], ast.Expr):
        tree.body[-1] = ast.Return(tree.body[-1].value)

    return ast.unparse(tree)

# =====================
# EVAL COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.eval(?:\s+([\s\S]+))?$"))
async def eval_cmd(e):
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
                "Usage:\n.eval python_code"
            )
            return await auto_delete(msg, 6)

        env = {
            "bot": bot,
            "event": e,
            "e": e,
            "asyncio": asyncio
        }

        stdout = []

        def fake_print(*args):
            stdout.append(" ".join(str(a) for a in args))

        env["print"] = fake_print

        try:
            fixed_code = wrap_code(code)

            exec(
                "async def __eval_func():\n"
                + "\n".join(f"    {line}" for line in fixed_code.split("\n")),
                env
            )

            result = await env["__eval_func"]()

            output = ""
            if stdout:
                output += "\n".join(stdout)

            if result is not None:
                output += f"\n{result}" if output else str(result)

            if not output.strip():
                output = "✅ Executed successfully"

            await send_long(
                e.chat_id,
                f"✅ OUTPUT:\n{output}",
                delete_after=10
            )

        except Exception:
            err = traceback.format_exc()
            await send_long(
                e.chat_id,
                f"❌ ERROR:\n{err}",
                delete_after=15
            )

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
