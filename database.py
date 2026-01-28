import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["userbot"]

settings = db["settings"]
notes = db["notes"]
