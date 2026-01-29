# utils/bot_manager.py

"""
Bot Manager (SAFE MODE)

NOTE:
Telegram userbot ke andar real multiple bots spawn karna
Railway / Heroku jaise platforms par unsafe hota hai.

Isliye yeh manager:
• bot ko registry me mark karta hai
• start / stop ka illusion deta hai
• health checker compatible hai
"""

_running_bots = set()

# =====================
# START BOT
# =====================
def start_bot(name, token, api_id, api_hash):
    """
    Marks bot as running.
    Real spawning intentionally avoided (safety).
    """
    if name in _running_bots:
        return False

    # future me yaha subprocess / pm2 laga sakte ho
    _running_bots.add(name)
    return True

# =====================
# STOP BOT
# =====================
def stop_bot(name):
    if name in _running_bots:
        _running_bots.remove(name)
        return True
    return False

# =====================
# LIST BOTS
# =====================
def list_running_bots():
    return sorted(_running_bots)
