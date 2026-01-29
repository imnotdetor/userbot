# main.py
import os
import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

from loader import load_plugins
from utils.auto_delete import auto_delete

# =====================
# ENV VARIABLES
# =====================
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
STRING_SESSION = os.environ["STRING_SESSION"]

# =====================
# TELETHON CLIENT
# =====================
bot = TelegramClient(
    StringSession(STRING_SESSION),
    API_ID,
    API_HASH
)

# =====================
# MAIN STARTUP
# =====================
async def main():
    print("🚀 Starting userbot...")

    # ✅ LOGIN FIRST (VERY IMPORTANT)
    await bot.start()
    print("✅ Userbot logged in")

    # ✅ LOAD PLUGINS AFTER LOGIN
    load_plugins()

    # 🔔 restart success message
    restart_chat = os.environ.pop("RESTART_CHAT", None)
    if restart_chat:
        try:
            msg = await bot.send_message(
                int(restart_chat),
                "✅ Restarted successfully"
            )
            asyncio.create_task(auto_delete(msg, 5))
        except Exception:
            pass

    # ✅ KEEP ALIVE
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
