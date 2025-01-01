from pyrogram import filters, Client as Mbot
import bs4, requests,re,asyncio
import wget,os,traceback
from mbot import BUG as LOG_GROUP,LOG_GROUP as DUMP_GROUP
from mbot.utils.util import is_maintenance_mode
from mbot import LOG_GROUP, OWNER_ID, SUDO_USERS, Mbot, AUTH_CHATS
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

@Mbot.on_message(filters.regex(r'https?://.*tiktok[^\s]+') & filters.incoming)
async def link_handler(Mbot, message):

    if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text("🔧 The bot is under maintenance. Please try again later.")
        return
    
    # Check Banned Users
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) ")
        return

    link = message.matches[0].group(0)
    try:
        m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
        get_api= requests.post("https://lovetik.com/api/ajax/search",data={"query":link}).json()
        if get_api['status'] and "Invalid TikTok video url" in get_api['mess']: 
           return await message.reply("Oops Invalid TikTok video url. Please try again :) ")
        if get_api.get('links'):
           try:
              if "MP3" in get_api['links'][0]['t']:
                 try:
                     await message.reply_photo(get_api['cover'])
                 except:
                     pass 
              dump_file = await message.reply_video(get_api['links'][0]['a'], caption="Thank you for using - @z_downloadbot")
           except KeyError:
               return await message.reply("Invalid TikTok video url. Please try again.")
           except Exception:
               snd_msg=await message.reply(get_api['links'][0]['a'])
               await asyncio.sleep(1)
               try:
                  dump_file = await message.reply_video(get_api['links'][0]['a'],caption="Thank you for using - @z_downloadbot")
                  await snd_msg.delete()
               except Exception:
                   pass
    except Exception as e:      
        if LOG_GROUP:
               await Mbot.send_message(LOG_GROUP,f"TikTok {e} {link}")
               await Mbot.send_message(LOG_GROUP, traceback.format_exc())          
    finally:
        if 'dump_file' in locals():
            if DUMP_GROUP:
               await dump_file.copy(DUMP_GROUP)
            await m.delete()
        await message.reply("Check out @z_downloadbot(music)  @Zpotify1(Channel) \n Please Support Us By /donate To Maintain This Project")
