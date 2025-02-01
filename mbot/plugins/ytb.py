from pyrogram import filters, Client as Mbot
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from os import mkdir, environ
from random import randint
from mbot import BUG as LOG_GROUP, LOG_GROUP as DUMP_GROUP
from shutil import rmtree
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL
from requests import get
import traceback, os
from mbot.utils.util import is_maintenance_mode
from mbot import LOG_GROUP, OWNER_ID, SUDO_USERS, Mbot, AUTH_CHATS
import json

## Load banned users from file ######
BAN_LIST_FILE = "banned_users.json"

# Load banned users from file
def load_banned_users():
    if os.path.exists(BAN_LIST_FILE):
        with open(BAN_LIST_FILE, "r") as f:
            return set(json.load(f))
    return set()

banned_users = load_banned_users()
####################################

FIXIE_SOCKS_HOST = environ.get('FIXIE_SOCKS_HOST')

async def thumb_down(videoId):
    with open(f"/tmp/{videoId}.jpg", "wb") as file:
        file.write(get(f"https://img.youtube.com/vi/{videoId}/default.jpg").content)
    return f"/tmp/{videoId}.jpg"

async def ytdl_video(path, video_url, id):
    print(video_url)
    qa = "mp4"  # Set to MP4 format
    file = f"{path}/%(title)s.%(ext)s"
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'default_search': 'ytsearch',
        'noplaylist': True,
        "nocheckcertificate": True,
        "outtmpl": file,
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "cache-dir": "/tmp/",
        "nocheckcertificate": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            video = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(video)
            print(filename)
            return filename
        except (IOError, BrokenPipeError):
            pass
            video = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(video)
            print(filename)
            return filename
        except Exception as e:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'default_search': 'ytsearch',
                'noplaylist': True,
                "nocheckcertificate": True,
                "outtmpl": file,
                "quiet": True,
                "addmetadata": True,
                "prefer_ffmpeg": True,
                "geo_bypass": True,
                "cache-dir": "/tmp/",
                "nocheckcertificate": True,
                "proxy": f"socks5://{FIXIE_SOCKS_HOST}"
            }
            with YoutubeDL(ydl_opts) as ydl:
                try:
                    video = ydl.extract_info(video_url, download=True)
                    filename = ydl.prepare_filename(video)
                    print(filename)
                    return filename
                except Exception as e:
                    print(e)

async def ytdl_down(path, video_url, id):
    print(video_url)
    qa = "mp3"
    query = f"{video_url[3]} - {video_url[2]}".replace(":", "").replace("\"", "")
    file = f"{path}/{query}"
    results = YoutubeSearch(f"{query}", max_results=1).to_dict()
    video_url = f"https://www.youtube.com/watch?v={results[0]['id']}"
    ydl_opts = {
        'format': "bestaudio",
        'default_search': 'ytsearch',
        'noplaylist': True,
        "nocheckcertificate": True,
        "outtmpl": file,
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "cache-dir": "/tmp/",
        "nocheckcertificate": True,
        "postprocessors": [{'key': 'FFmpegExtractAudio', 'preferredcodec': qa, 'preferredquality': '693'}],
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            video = ydl.extract_info(video_url, download=True)
            return f"{file}.{qa}"
        except (IOError, BrokenPipeError):
            pass
            video = ydl.extract_info(video_url, download=True)
            info = ydl.extract_info(video)
            filename = ydl.prepare_filename(video)
            print(filename)
            return f"{filename}.{qa}"
        except Exception as e:
            if FIXIE_SOCKS_HOST:
                try:
                    ydl_opts = {
                        'format': "bestaudio",
                        'default_search': 'ytsearch',
                        'noplaylist': True,
                        "nocheckcertificate": True,
                        "outtmpl": file,
                        "quiet": True,
                        "addmetadata": True,
                        "prefer_ffmpeg": True,
                        "geo_bypass": True,
                        "cache-dir": "/tmp/",
                        "nocheckcertificate": True,
                        "proxy": f"socks5://{FIXIE_SOCKS_HOST}",
                        "postprocessors": [{'key': 'FFmpegExtractAudio', 'preferredcodec': qa, 'preferredquality': '693'}],
                    }
                    with YoutubeDL(ydl_opts) as ydl:
                        video = ydl.extract_info(video_url, download=True)
                        return f"{file}.{qa}"
                except Exception as e:
                    print(e)

async def getIds(video):
    ids = []
    with YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(video, download=False)
        try:
            info_dict = info_dict['entries']
            ids.extend([x.get('id'), x.get('playlist_index'), x.get('creator') or x.get('uploader'), x.get('title'), x.get('duration'), x.get('thumbnail')] for x in info_dict)
        except:
            ids.append([info_dict.get('id'), info_dict.get('playlist_index'), info_dict.get('creator') or info_dict.get('uploader'), info_dict.get('title'), info_dict.get('duration'), info_dict.get('thumbnail')])
    return ids

@Mbot.on_message(filters.regex(r'https?://.*youtube[^\s]+') & filters.incoming | filters.regex(r'(https?:\/\/(?:www\.)?youtu\.?be(?:\.com)?\/.*)') & filters.incoming)
async def _(Mbot, message):
    if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text("🔧 The bot is under maintenance. Please try again later.")
        return
    
    # Check Banned Users
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) ")
        return

    try:
        m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
    except:
        pass

    link = message.matches[0].group(0)
    if "channel" in link or "/c/" in link:
        return await m.edit_text("**Channel** Download Not Available. ")

    # Inline keyboard for choosing between video and audio
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Download Video 📽️", callback_data=f"video_{link}")],
            [InlineKeyboardButton("Download Audio 🎵", callback_data=f"audio_{link}")]
        ]
    )
    await message.reply_text("Choose the format you want to download:", reply_markup=keyboard)
    await m.delete()

@Mbot.on_callback_query(filters.regex(r'^(video|audio)_'))
async def handle_download_choice(Mbot, callback_query):
    choice, link = callback_query.data.split('_', 1)
    user_id = callback_query.from_user.id

    if is_maintenance_mode() and user_id not in SUDO_USERS:
        await callback_query.answer("🔧 The bot is under maintenance. Please try again later.", show_alert=True)
        return

    if user_id in banned_users:
        await callback_query.answer("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) ", show_alert=True)
        return

    try:
        if choice == "video":
            randomdir = "/tmp/" + str(randint(1, 100000000))
            mkdir(randomdir)
            fileLink = await ytdl_video(randomdir, link, user_id)
            await callback_query.message.reply_video(fileLink)
            if os.path.exists(randomdir):
                rmtree(randomdir)
        elif choice == "audio":
            randomdir = "/tmp/" + str(randint(1, 100000000))
            mkdir(randomdir)
            fileLink = await ytdl_down(randomdir, link, user_id)
            await callback_query.message.reply_audio(fileLink)
            if os.path.exists(randomdir):
                rmtree(randomdir)
    except Exception as e:
        await callback_query.message.reply_text(f"400: Sorry, Unable To Find It  try another or report it  to @itachi2129 or support chat @z_support1 🤖  ")
        if LOG_GROUP:
            await Mbot.send_message(LOG_GROUP, f"Youtube {e} {link}")
            await Mbot.send_message(LOG_GROUP, traceback.format_exc())

    await callback_query.answer()
