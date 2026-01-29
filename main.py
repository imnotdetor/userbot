# main.py
import asyncio
from userbot import bot
from loader import load_plugins

async def main():
    print("🚀 Starting userbot...")

    # ✅ FIRST: connect & authorize
    await bot.start()
    print("✅ Userbot logged in")

    # ✅ SECOND: load plugins AFTER login
    load_plugins()

    # ✅ keep alive
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
