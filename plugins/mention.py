import asyncio
import random
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error

print("✔ mention.py loaded")

# =====================
# CONFIG
# =====================
BATCH_SIZE = 5
MAX_MENTIONS = 50
DELAY = 3  # seconds

RANDOM_TEXTS = [
    "Kaha ho sab log 🤨",
    "Online aa jao bhai 😶",
    "Sab gayab ho kya 👀",
    "Attendance lagao 😏",
    "Zinda ho sab? 😭",
    "Hello hello 👋",
]

# =====================
# GLOBAL STATE
# =====================
MENTION_RUNNING = False
MENTIONED_USERS = set()

# =====================
# HELPERS
# =====================
async def collect_users(chat_id):
    users = []
    async for msg in bot.iter_messages(chat_id, limit=500):
        if msg.sender_id and msg.sender_id not in MENTIONED_USERS:
            users.append(msg.sender_id)
        if len(users) >= MAX_MENTIONS:
            break
    return users

async def run_mentions(chat_id, users, text):
    global MENTION_RUNNING

    for i in range(0, len(users), BATCH_SIZE):
        if not MENTION_RUNNING:
            break

        batch = users[i:i + BATCH_SIZE]
        mentions = " ".join(f"[User](tg://user?id={u})" for u in batch)

        await bot.send_message(
            chat_id,
            f"{text}\n\n{mentions}",
            link_preview=False
        )

        MENTIONED_USERS.update(batch)
        await asyncio.sleep(DELAY)

    MENTION_RUNNING = False

# =====================
# .MENTION (TEXT BASED)
# =====================
@bot.on(events.NewMessage(pattern=r"\.mention (.+)$"))
async def mention_cmd(e):
    global MENTION_RUNNING

    if not is_owner(e) or MENTION_RUNNING:
        return

    try:
        await e.delete()
        MENTION_RUNNING = True

        text = e.pattern_match.group(1)
        users = await collect_users(e.chat_id)

        if not users:
            MENTION_RUNNING = False
            return

        await run_mentions(e.chat_id, users, text)

    except Exception as ex:
        MENTION_RUNNING = False
        await log_error(bot, "mention.py", ex)

# =====================
# .RDMENTION (RANDOM TEXT)
# =====================
@bot.on(events.NewMessage(pattern=r"\.rdmention$"))
async def rdmention_cmd(e):
    global MENTION_RUNNING

    if not is_owner(e) or MENTION_RUNNING:
        return

    try:
        await e.delete()
        MENTION_RUNNING = True

        text = random.choice(RANDOM_TEXTS)
        users = await collect_users(e.chat_id)

        if not users:
            MENTION_RUNNING = False
            return

        await run_mentions(e.chat_id, users, text)

    except Exception as ex:
        MENTION_RUNNING = False
        await log_error(bot, "mention.py", ex)

# =====================
# STOP MENTION
# =====================
@bot.on(events.NewMessage(pattern=r"\.stopm$"))
async def stop_mention(e):
    global MENTION_RUNNING

    if not is_owner(e):
        return

    await e.delete()
    MENTION_RUNNING = False
    await bot.send_message(e.chat_id, "🛑 Mention stopped")
