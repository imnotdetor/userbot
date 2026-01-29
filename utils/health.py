import time
from utils.mongo import check_mongo_health

START_TIME = time.time()

def get_uptime():
    seconds = int(time.time() - START_TIME)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}h {m}m {s}s"

def mongo_status():
    info = check_mongo_health()
    if info["ok"]:
        return "✅ Connected"
    return f"❌ {info.get('error')}"
