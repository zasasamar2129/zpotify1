from pyrogram import filters,Client as Mbot
from mbot import BUG as  LOG_GROUP, LOG_GROUP as DUMP_GROUP
import os,re,asyncio,bs4
import requests,wget,traceback
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

@Mbot.on_message(filters.regex(r'https?://.*twitter[^\s]+') & filters.incoming | filters.regex(r'https?://(?:www\.)?x\.com/\S+') & filters.incoming,group=-5)
async def twitter_handler(Mbot, message):

   if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text("🔧 The bot is under maintenance. Please try again later.")
        return
   
   # Check Banned Users
   if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) ")
        return

   try:            
      link=message.matches[0].group(0)
      if "x.com" in link:
         link=link.replace("x.com","fxtwitter.com")
      elif "twitter.com" in link:
         link = link.replace("twitter.com","fxtwitter.com")
      m=await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
      try:
          dump_file = await message.reply_video(link,caption="Thank you for using - @InstaReelsdownbot")
      except Exception as e:
          print(e)
          try:
             snd_message=await message.reply(link)
             await asyncio.sleep(1)
             dump_file = await message.reply_video(link,caption="Thank you for using - @InstaReelsdownbot")
             await snd_message.delete()
          except Exception as e:
              print(e)
              await snd_message.delete()
              get_api=requests.get(link).text
              soup=bs4.BeautifulSoup(get_api,"html.parser")
              meta_tag= soup.find("meta", attrs = {"property": "og:video"})
              if not meta_tag:
                  meta_tag = soup.find("meta", attrs={"property": "og:image"})
              content_value  = meta_tag['content']
              try:
                  dump_file = await message.reply_video(content_value,caption="Thank you for using - @InstaReelsdownbot")
              except Exception as e:
                  print(e)
                  try:
                     snd_msg=await message.reply(content_value)
                     await asyncio.sleep(1)
                     await message.reply_video(content_value,caption="Thank you for using - @InstaReelsdownbot")
                     await snd_msg.delete()
                  except Exception as e:
                      print(e)
                      await message.reply("Oops Invalid link or Media Is Not Available:)")
   except Exception as e:
        print(e)
        if LOG_GROUP:
           await Mbot.send_message(LOG_GROUP,e)
           await Mbot.send_message(LOG_GROUP,traceback.format_exc())
   finally:
       if DUMP_GROUP:
          if "dump_file" in locals():
             await dump_file.copy(DUMP_GROUP)
       await m.delete()
       await message.reply("Check out @z_downloadbot(music)  @Zpotify1(Channel) \n Please Support Us By /donate To Maintain This Project")               
                  
    
