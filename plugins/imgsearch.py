# Reverse Image Search Plugin (Google)
# Converted for Telethon Userbot

import io
import os
import re
import urllib.request
import requests
from bs4 import BeautifulSoup
from PIL import Image
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "imgsearch.py"
print("✔ imgsearch.py loaded (Reverse Image Search)")

# User agent
opener = urllib.request.build_opener()
opener.addheaders = [
    (
        "User-agent",
        "Mozilla/5.0 (Linux; Android 9; Mobile) AppleWebKit/537.36 Chrome Safari",
    )
]


@bot.on(events.NewMessage(pattern=r"\.imgsearch(?:\s+(\d+))?$"))
async def imgsearch(e):
    try:
        limit = e.pattern_match.group(1) or 3

        reply = await e.get_reply_message()
        if not reply or not reply.media:
            return await e.edit("❌ Reply to a photo or sticker.")

        await e.edit("🔍 Processing image...")

        photo = io.BytesIO()
        await bot.download_media(reply, photo)

        try:
            image = Image.open(photo)
        except Exception:
            return await e.edit("❌ Unsupported image format.")

        filename = "reverse.png"
        image.save(filename, "PNG")
        image.close()

        search_url = "https://www.google.com/searchbyimage/upload"
        multipart = {
            "encoded_image": (filename, open(filename, "rb")),
            "image_content": "",
        }

        response = requests.post(search_url, files=multipart, allow_redirects=False)
        if response.status_code != 302:
            return await e.edit("❌ Google refused the image.")

        fetch_url = response.headers.get("Location")
        os.remove(filename)

        data = await parse_google(fetch_url)
        guess = data.get("best_guess")
        similar = data.get("similar_images")

        if not guess or not similar:
            return await e.edit("❌ No results found.")

        await e.edit(f"**Best Guess:** [{guess}]({fetch_url})\n\n📥 Fetching images...")

        images = await fetch_images(similar, int(limit))
        if images:
            await bot.send_file(e.chat_id, images, reply_to=e.id)

        await e.edit(
            f"🔎 **Best Guess:** [{guess}]({fetch_url})\n"
            f"🖼️ [Visually similar images]({similar})",
            link_preview=False,
        )

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        mark_plugin_error(PLUGIN_NAME)


async def parse_google(url):
    source = opener.open(url).read()
    soup = BeautifulSoup(source, "html.parser")

    result = {"best_guess": None, "similar_images": None}

    for tag in soup.find_all("div", {"class": "r5a77d"}):
        result["best_guess"] = tag.get_text()

    for inp in soup.find_all("input", {"class": "gLFyf"}):
        result["similar_images"] = (
            "https://www.google.com/search?tbm=isch&q="
            + urllib.parse.quote_plus(inp.get("value"))
        )

    return result


async def fetch_images(url, limit):
    html = opener.open(url).read().decode("utf-8")
    pattern = r',\["(https://[^"]+\.(?:jpg|jpeg|png))",'
    matches = re.findall(pattern, html, re.I)

    images = []
    for img in matches[:limit]:
        try:
            r = requests.get(img)
            images.append(r.content)
        except Exception:
            continue

    return images


mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "imgsearch",
    ".imgsearch (reply)\n"
    ".imgsearch <number>\n\n"
    "• Reverse image search using Google\n"
    "• Reply to photo or sticker\n"
    "• Optional limit for similar images",
)