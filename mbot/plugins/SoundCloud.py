from pyrogram import filters,enums
from mbot import AUTH_CHATS, LOG_GROUP,Mbot
from os import mkdir
#from utils import temp
from random import randint
#from database.users_chats_db import db
from yt_dlp import YoutubeDL
from spotipy.oauth2 import SpotifyClientCredentials
from mbot.utils.util import is_maintenance_mode
from mbot import LOG_GROUP, OWNER_ID, SUDO_USERS, Mbot, AUTH_CHATS
import spotipy
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mbot.utils.mainhelper import fetch_spotify_track

##Load banned users from file######
BAN_LIST_FILE = "banned_users.json"
# Load banned users from file
def load_banned_users():
    if os.path.exists(BAN_LIST_FILE):
        with open(BAN_LIST_FILE, "r") as f:
            return set(json.load(f))
    return set()
banned_users = load_banned_users()
####################################

client_credentials_manager = SpotifyClientCredentials()
client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
async def get_data(query):
    ydl_opts = {
        'format': "bestaudio/best",
        'default_search': 'ytsearch',
        'noplaylist': True,
        "nocheckcertificate": True,
        "outtmpl": f"(title)s.mp3",
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,

        "nocheckcertificate": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(query, download=False)
            return video 

async def down_data(item,query):
    ydl_opts = {
        'format': "bestaudio/best",
        'default_search': 'ytsearch',
        'noplaylist': True,
        "nocheckcertificate": True,
        "outtmpl": f"{item['title']} {item['uploader']}.mp3",
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,

        "nocheckcertificate": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(query, download=True)
            return ydl.prepare_filename(video)

@Mbot.on_message(filters.regex(r'https?://.*soundcloud[^\s]+'))
async def link_handler(Mbot, message):

    if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text("🔧 The bot is under maintenance. Please try again later.")
        return
    
    # Check Banned Users
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) ")
        return

    try:
      # if message.from_user.id in temp.BANNED_USERS:
       #   return
       m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
       await message.reply_chat_action(enums.ChatAction.TYPING)
       link = message.matches[0].group(0)
     #  get_s = await db.get_set(message.from_user.id)
    #   if get_s['http'] == "False":
     #     return
       item=await get_data(link)
       path=await down_data(item,link)
       await message.reply_audio(path)
       await m.delete()
       os.remove(path)
    except Exception as e:
        pass
        await message.reply(e)
    #    await Mbot.send_message(BUG,f"SoundCloud  {e}")
        await m.delete()
        os.remove(path)
