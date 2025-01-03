from __future__ import unicode_literals
from pyrogram import Client , filters 
from os import environ,execl
from datetime import datetime
from sys import executable
from pyrogram.errors import FloodWait 
from pyrogram.types import Message , InlineKeyboardMarkup, InlineKeyboardButton ,CallbackQuery
from pyrogram.errors import FloodWait 
from asyncio import sleep
from mbot.utils.util import is_maintenance_mode
from mbot import LOG_GROUP, OWNER_ID, SUDO_USERS, Mbot, AUTH_CHATS
#from database.users_chats_db import db
#from utils import get_size
from shazamio import Shazam
#import math
import asyncio
import time
#import shlex
#import aiofiles
#import aiohttp
import wget
import os
#from asgiref.sync import sync_to_async
from requests import get
from mbot.utils.util import run_cmd as runcmd
import datetime
from json import JSONDecodeError
import requests
#import ffmpeg 
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
#from youtubesearchpython import VideosSearch
import yt_dlp
#from youtube_search import YoutubeSearch
import requests
from typing import Tuple
from pyrogram import filters
from pyrogram import Client
#from mbot import OWNER_ID as ADMINS
import time
from mutagen.id3 import ID3, APIC,error
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from apscheduler.schedulers.background import BackgroundScheduler
from mbot.utils.shazam import humanbytes, edit_or_reply, fetch_audio
import json
import os
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
NOT_SUPPORT = [ ]
ADMINS = 5337964165
def get_arg(message):
    msg = message.text
    msg = msg.replace(" ", "", 1) if msg[1] == " " else msg
    split = msg[1:].replace("\n", " \n").split(" ")
    if " ".join(split[1:]).strip() == "":
        return ""
    return " ".join(split[1:])
#@sync_to_async
def thumb_down(album_id,img):
    with open(f"/tmp/thumbnails/{album_id}.jpg","wb") as file:
        file.write(get(img).content)
    return f"/tmp/thumbnails/{album_id}.jpg"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


async def shazam(file):
    shazam = Shazam()
    try:
        r = await shazam.recognize(file)
    except:
        return None, None, None
    if not r:
        return None, None, None
    track = r.get("track")
    nt = track.get("images")
    image = nt.get("coverarthq")
    by = track.get("subtitle")
    title = track.get("title")
    return image, by, title

async def convert_to_audio(vid_path):
    stark_cmd = f"ffmpeg -i {vid_path} -map 0:a friday.mp3"
    await runcmd(stark_cmd)
    final_warner = "friday.mp3"
    if not os.path.exists(final_warner):
        return None
    return final_warner

@Client.on_message(filters.command(["find", "shazam"] ))
async def shazam_(client, message):

    if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text("🔧 The bot is under maintenance. Please try again later.")
        return
    
    # Check Banned Users
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) ")
        return
    
    stime = getime.time()
    sts=await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
    msg = await message.reply_text("`Shazaming This Song.")
    if not message.reply_to_message:
        return await msg.edit("`Reply To Song File`")
    if not (message.reply_to_message.audio or message.reply_to_message.voice or message.reply_to_message.video):
        return await msg.edit("`Reply To Audio File.`")
    if message.reply_to_message.video:
        video_file = await message.reply_to_message.download()
        music_file = await convert_to_audio(video_file)
        dur = message.reply_to_message.video.duration
        if not music_file:
            return await msg.edit("`Unable To Convert To Song File. Is This A Valid File?`")
    elif (message.reply_to_message.voice or message.reply_to_message.audio):
        dur = message.reply_to_message.voice.duration if message.reply_to_message.voice else message.reply_to_message.audio.duration
        music_file = await message.reply_to_message.download()
    size_ = humanbytes(os.stat(music_file).st_size)
    dur = datetime.timedelta(seconds=dur)
    thumbnail, by, title = await shazam(music_file)
    if thumbnail:
       thumb=wget.download(thumbnail)
    if title is None:
        return await msg.edit("`No Results Found.`")
    etime = getime.time()
    t_k = round(etime - stime)
    caption = f"""<b><u>Shazamed Song</b></u>
    
<b>Song Name :</b> <code>{title}</code>
<b>Singer :</b> <code>{by}</code>
<b>Duration :</b> <code>{dur}</code>
<b>Size :</b> <code>{size_}</code>
<b>Time Taken :</b> <code>{t_k} Seconds</code>

<b><u>Shazamed By @z_downloadbot</b></u>
    """
    await sts.delete()
    if thumb:
        await msg.delete()
        await message.reply_to_message.reply_photo(thumb, caption=caption, quote=True)
    else:
        await msg.edit(caption)
    os.remove(music_file)
    if thumb:
       path=await download_songs(title)
       audio = EasyID3(path)
       try:
           audio['title']=title
           audio['artist']=by
       except:
           pass
       audio.save()
       try:
           audio = MP3(path, ID3=ID3)
           audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(thumb,'rb').read()))
           audio.save()
       except Exception :
           pass   
       await message.reply_audio(path,title=title,performer=by,caption=f"{title} - {by}",thumb=thumb)
       os.remove(path)
       os.remove(thumb)
    else:
         path=await download_songs(title)
         await message.reply_audio(path,title=title,performer=by,caption=f"{title} - {by}") 
         try:
           audio['title']=title
           audio['artist']=by
         except:
             pass
         audio.save()
         try:
           audio = MP3(path, ID3=ID3)
           audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(thumb,'rb').read()))
           audio.save()
         except Exception :
           pass   
         os.remove(path)
