# userbot.py
import os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
STRING_SESSION = os.environ["STRING_SESSION"]

bot = TelegramClient(
    StringSession(STRING_SESSION),
    API_ID,
    API_HASH
)
