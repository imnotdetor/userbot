# plugins/utils.py
import asyncio
import traceback
from datetime import datetime
from pyrogram import Client

# 🔒 Error logs yahin jayenge (Saved Messages)
ERROR_CHAT = "me"

# =====================
# PLUGIN HEALTH STORAGE
# =====================
PLUGIN_STATUS = {}

# =====================
# HEALTH HELPERS
# =====================
def mark_plugin_loaded(plugin: str):
    PLUGIN_STATUS[plugin] = {
        "loaded": True,
        "last_error": None,
        "last_error_time": None
    }

def mark_plugin_error(plugin: str, error: Exception):
    if plugin not in PLUGIN_STATUS:
        PLUGIN_STATUS[plugin] = {"loaded": True}

    PLUGIN_STATUS[plugin]["last_error"] = str(error)
    PLUGIN_STATUS[plugin]["last_error_time"] = datetime.now().strftime(
        "%d %b %Y %I:%M %p"
    )

def get_plugin_health():
    return PLUGIN_STATUS


# =====================
# SAFE DELETE
# =====================
async def safe_delete(msg):
    try:
        await msg.delete()
    except:
        pass


# =====================
# AUTO DELETE MESSAGE
# =====================
async def auto_delete(msg, seconds: int):
    try:
        await asyncio.sleep(seconds)
        await msg.delete()
    except:
        pass


# =====================
# PLUGIN ERROR LOGGER
# =====================
async def log_error(client, plugin: str, error: Exception):
    print(f"[PLUGIN ERROR] {plugin}: {error}")
    mark_plugin_error(plugin, error)

    try:
        text = (
            "PLUGIN ERROR\n\n"
            f"Plugin: {plugin}\n"
            f"Time: {datetime.now().strftime('%d %b %Y %I:%M %p')}\n\n"
            f"Error:\n{str(error)}\n\n"
            f"Traceback:\n{traceback.format_exc(limit=5)}"
        )
        await client.send_message(ERROR_CHAT, text)
    except Exception as e:
        print("[LOG_ERROR FAILED]", e)


# =====================
# BOT MANAGER (MULTI-BOT)
# =====================
RUNNING_BOTS = {}   # name -> Client instance

async def start_bot(name: str, token: str, api_id: int, api_hash: str):
    if name in RUNNING_BOTS:
        raise RuntimeError("Bot already running")

    try:
        bot = Client(
            name=f"bot_{name}",
            bot_token=token,
            api_id=api_id,
            api_hash=api_hash,
            plugins=dict(root="bot_plugins")
        )

        await bot.start()
        RUNNING_BOTS[name] = bot

    except Exception as e:
        mark_plugin_error("bot_manager", e)
        raise


async def stop_bot(name: str):
    bot = RUNNING_BOTS.get(name)
    if not bot:
        raise RuntimeError("Bot not running")

    await bot.stop()
    del RUNNING_BOTS[name]


def list_running_bots():
    return list(RUNNING_BOTS.keys())
