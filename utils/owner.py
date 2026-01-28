from config import OWNER_ID

def is_owner(event):
    return event.sender_id == OWNER_ID