import traceback
import asyncio
import ast
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error

PLUGIN_NAME = "eval.py"
print("✔ eval.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "dev",
    ".eval CODE\n\n"
    "• Execute python code dynamically\n"
    "• Auto return last expression\n"
    "• Async + multiline supported\n"
    "• Owner only"
)

MAX_LEN = 3500  # telegram safe limit

# =====================
# SAFE SEND
# =====================
async def send_long(chat_id, text):
    for i in range(0, len(text), MAX_LEN):
        await bot.send_message(chat_id, text[i:i + MAX_LEN])

# =====================
# AUTO RETURN FIX
# =====================
def wrap_code(code: str) -> str:
    """
    Automatically returns last expression if not explicit return
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
            await bot.send_message(
                e.chat_id,
                "Usage:\n.eval python_code"
            )
            return

        # execution environment
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
                f"✅ OUTPUT:\n{output}"
            )

        except Exception:
            err = traceback.format_exc()
            await send_long(
                e.chat_id,
                f"❌ ERROR:\n{err}"
            )

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
