# utils/mongo.py

from pymongo import MongoClient
import os
import time

# =====================
# CONFIG
# =====================
MONGO_URL = os.environ.get("MONGO_URL")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL is missing in environment variables")

# =====================
# CONNECT
# =====================
mongo = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)

# default database
db = mongo["userbot"]

# =====================
# HEALTH CHECK
# =====================
def check_mongo_health():
    try:
        start = time.time()
        mongo.admin.command("ping")
        return {
            "ok": True,
            "db": db.name,
            "collection": "vars / notes / others",
            "time": f"{round(time.time() - start, 2)}s"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }