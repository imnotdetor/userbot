from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help
)
import os, shutil

# 🔥 plugin health
mark_plugin_loaded("diskclean.py")

# =====================
# HELP REGISTRATION (HELP4)
# =====================
register_help(
    "diskclean",
    """
.diskusage
→ Show disk usage only (no delete)

.diskclean --dry
→ Preview clean (no delete)

.diskclean confirm
→ Clean disk with confirmation

Folders affected:
• saved_media
• assets/tmp
"""
)

# =====================
# CONFIG
# =====================
CLEAN_FOLDERS = [
    "saved_media",
    "assets/tmp"
]

# =====================
# HELPERS
# =====================
def get_folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total


def format_mb(size):
    return round(size / (1024 * 1024), 2)


def calculate_usage():
    total = 0
    details = {}
    for folder in CLEAN_FOLDERS:
        if os.path.isdir(folder):
            size = get_folder_size(folder)
            details[folder] = size
            total += size
        else:
            details[folder] = 0
    return total, details


# =====================
# DISK USAGE ONLY
# =====================
@Client.on_message(owner_only & filters.command("diskusage", "."))
async def disk_usage_cmd(client: Client, m):
    try:
        await m.delete()

        total, details = calculate_usage()

        text = "📊 **DISK USAGE**\n\n"
        for f, size in details.items():
            text += f"• {f}: `{format_mb(size)} MB`\n"

        text += f"\n🧮 **Total:** `{format_mb(total)} MB`"

        msg = await client.send_message(m.chat.id, text)
        await auto_delete(msg, 12)

    except Exception as e:
        mark_plugin_error("diskclean.py", e)
        await log_error(client, "diskclean.py", e)


# =====================
# DISK CLEAN
# =====================
@Client.on_message(owner_only & filters.command("diskclean", "."))
async def disk_clean_cmd(client: Client, m):
    try:
        await m.delete()

        arg = m.command[1].lower() if len(m.command) > 1 else None

        before_total, before_details = calculate_usage()

        # 🔍 DRY RUN
        if arg == "--dry":
            text = "🧪 **DISK CLEAN PREVIEW**\n\n"
            for f, size in before_details.items():
                text += f"• {f}: `{format_mb(size)} MB`\n"

            text += (
                f"\n🧮 **Total reclaimable:** `{format_mb(before_total)} MB`\n\n"
                "ℹ️ No files were deleted"
            )

            msg = await client.send_message(m.chat.id, text)
            await auto_delete(msg, 15)
            return

        # ❌ SAFETY CHECK
        if arg != "confirm":
            msg = await client.send_message(
                m.chat.id,
                "⚠️ **Confirmation required**\n\n"
                "Use:\n"
                "`.diskclean confirm`\n\n"
                "Or preview:\n"
                "`.diskclean --dry`"
            )
            await auto_delete(msg, 10)
            return

        # 🧹 CLEAN PROCESS
        cleaned = []
        skipped = []

        for folder in CLEAN_FOLDERS:
            if os.path.isdir(folder):
                try:
                    shutil.rmtree(folder)
                    os.makedirs(folder, exist_ok=True)
                    cleaned.append(folder)
                except:
                    skipped.append(folder)
            else:
                skipped.append(folder)

        after_total, _ = calculate_usage()
        freed = before_total - after_total

        # 📋 REPORT
        text = "🧹 **DISK CLEAN REPORT**\n\n"
        text += (
            f"📊 Before: `{format_mb(before_total)} MB`\n"
            f"📊 After: `{format_mb(after_total)} MB`\n"
            f"🆓 Freed: `{format_mb(freed)} MB`\n\n"
        )

        if cleaned:
            text += "✅ **Cleaned:**\n"
            for f in cleaned:
                text += f"• {f}\n"

        if skipped:
            text += "\n⚠️ **Skipped:**\n"
            for f in skipped:
                text += f"• {f}\n"

        msg = await client.send_message(m.chat.id, text)
        await auto_delete(msg, 15)

    except Exception as e:
        mark_plugin_error("diskclean.py", e)
        await log_error(client, "diskclean.py", e)
