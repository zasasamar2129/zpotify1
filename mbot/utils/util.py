import shlex
import math
import asyncio
import time
import aiofiles
import aiohttp
#import wget
import os
import datetime
from json import JSONDecodeError
import requests
#import ffmpeg
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from youtubesearchpython import VideosSearch
import yt_dlp
from youtube_search import YoutubeSearch
import requests
from typing import Tuple
from pyrogram import filters
from pyrogram import Client
from mbot.utils.shazam import humanbytes, edit_or_reply, fetch_audio
import json
import os
# File to store maintenance status
MAINTENANCE_FILE = "maintenance_status.json"

# Load maintenance status
def is_maintenance_mode():
    """Check if the bot is in maintenance mode."""
    if os.path.exists(MAINTENANCE_FILE):
        with open(MAINTENANCE_FILE, "r") as f:
            return json.load(f).get("maintenance", False)
    return False

# Save maintenance status
def save_maintenance_status(status):
    """Enable or disable maintenance mode."""
    with open(MAINTENANCE_FILE, "w") as f:
        json.dump({"maintenance": status}, f)

help_message = []

async def run_cmd(cmd: str) -> Tuple[str, str, int, int]:
    """Run Commands"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )
