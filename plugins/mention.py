import asyncio
import random
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.auto_delete import auto_delete

PLUGIN_NAME = "mention.py"
print("✔ mention.py loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# CONFIG
# =====================
BATCH_SIZE = 5
MAX_USERS = 50
DELAY_BETWEEN_BATCH = 3

RANDOM_TEXTS = [
    "Kaha ho sab log 🤨",
    "Online bhi aa jao 👀",
    "Sab gayab ho kya 😑",
    "Attendance lagao jaldi 😤",
    "Zinda ho ya nahi 😏"
]

# =====================
# STATE
# =====================
MENTION_RUNNING = False
MENTIONED_USERS = set()

# =====================
# HELP REGISTER
# =====================
register_help(
    "mention",
    ".mention TEXT\n"
    ".rdmention\n"
    ".stopm\n\n"
    "• Batch mention (5 users)\n"
    "• Flood safe (max 50)\n"
    "• Skips already mentioned users\n"
    "• Owner only"
)

# =====================
# HELPER: ADMIN CHECK
# =====================
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        p = await bot(GetParticipantRequest(chat_id, user_id))
        return isinstance(
            p.participant,
            (ChannelParticipantAdmin, ChannelParticipantCreator)
        )
    except Exception:
        return False

# =====================
# CORE MENTION LOGIC
# =====================
async def run_mentions(chat_id: int, base_text: str):
    global MENTION_RUNNING, MENTIONED_USERS

    MENTION_RUNNING = True
    count = 0
    batch = []

    async for msg in bot.iter_messages(chat_id, limit=500):
        if not MENTION_RUNNING:
            break

        uid = msg.sender_id
        if not uid or uid in MENTIONED_USERS:
            continue

        MENTIONED_USERS.add(uid)
        count += 1

        try:
            user = await bot.get_entity(uid)
            name = user.first_name or "User"
            batch.append(f"[{name}](tg://user?id={uid})")
        except:
            continue

        if len(batch) == BATCH_SIZE:
            text = f"{base_text}\n\n" + " ".join(batch)
            await bot.send_message(chat_id, text, link_preview=False)
            batch.clear()
            await asyncio.sleep(DELAY_BETWEEN_BATCH)

        if count >= MAX_USERS:
            break

    if batch and MENTION_RUNNING:
        text = f"{base_text}\n\n" + " ".join(batch)
        await bot.send_message(chat_id, text, link_preview=False)

    MENTION_RUNNING = False
    await bot.send_message(chat_id, "✅ Mention completed")

# =====================
# .mention COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.mention (.+)"))
async def mention_cmd(e):
    if not is_owner(e):
        return

    global MENTION_RUNNING

    if MENTION_RUNNING:
        return await e.reply("⚠️ Mention already running")

    try:
        await e.delete()
    except:
        pass

    text = e.pattern_match.group(1)
    asyncio.create_task(run_mentions(e.chat_id, text))

# =====================
# .rdmention COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.rdmention$"))
async def rdmention_cmd(e):
    if not is_owner(e):
        return

    global MENTION_RUNNING

    if MENTION_RUNNING:
        return await e.reply("⚠️ Mention already running")

    try:
        await e.delete()
    except:
        pass

    text = random.choice(RANDOM_TEXTS)
    asyncio.create_task(run_mentions(e.chat_id, text))

# =====================
# .stopm COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.stopm$"))
async def stop_mention(e):
    global MENTION_RUNNING

    if not is_owner(e):
        return

    MENTION_RUNNING = False

    try:
        await e.delete()
    except:
        pass

    msg = await bot.send_message(
        e.chat_id,
        "🛑 Mention stopped"
    )

    # ✅ auto delete after 6 seconds
    await auto_delete(msg, 6)
