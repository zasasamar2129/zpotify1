from pyrogram import filters, Client as Mbot
import bs4, requests,re
import wget,os,traceback,asyncio
import time
from mbot import LOG_GROUP as DUMP_GROUP,BUG as LOG_GROUP
from mbot.utils.util import is_maintenance_mode
from mbot import LOG_GROUP, OWNER_ID, SUDO_USERS, Mbot, AUTH_CHATS
import json
import os
from mbot.utils.language_utils import get_user_language

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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
#    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Length": "99",
    "Origin": "https://saveig.app",
    "Connection": "keep-alive",
    "Referer": "https://saveig.app/en",
}
@Mbot.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming)
async def link_handler(Mbot, message):
    user_lang = get_user_language(message.from_user.id)
    INSTA_RESPONSES = {
    "en": {
        "maintenance": "🔧 The bot is under maintenance. Please try again later.",
        "banned": "You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) ",
        "thank_you": "Thank you for using - @z_downloadbot",
        "wrong": "Oops, something went wrong.",
        "went_wrong": "Oops, something went wrong.",
        "400": "400: Sorry, Unable To Find It. Make sure it's publicly available :)",
    },
    "fa": {  # Farsi
        "maintenance": "🔧 ربات در حال تعمیر است. لطفاً بعداً دوباره امتحان کنید.",
        "banned": "شما از استفاده از این ربات ممنوع شده‌اید  😔",
        "thank_you": "با تشکر از شما برای استفاده از - @z_downloadbot",
        "wrong": "اوه، مشکلی پیش آمد.",
        "went_wrong": "اوه، مشکلی پیش آمد.",
        "400": "400: متأسفم، امکان یافتن آن وجود ندارد. لطفاً مطمئن شوید که عمومی است :)",
    },
    "ru": {  # Russian
        "maintenance": "🔧 Бот на техническом обслуживании. Пожалуйста, попробуйте позже.",
        "banned": "Вам запрещено использовать этого бота 😔",
        "thank_you": "Спасибо за использование - @z_downloadbot",
        "wrong": "Ой, что-то пошло не так.",
        "went_wrong": "Ой, что-то пошло не так.",
        "400": "400: Извините, не удалось найти. Убедитесь, что это доступно публично :)",
    },
    "es": {  # Spanish
        "maintenance": "🔧 El bot está en mantenimiento. Por favor, inténtalo más tarde.",
        "banned": "Estás baneado de usar este bot 😔",
        "thank_you": "Gracias por usar - @z_downloadbot",
        "wrong": "Uy, algo salió mal.",
        "went_wrong": "Uy, algo salió mal.",
        "400": "400: Lo siento, no se pudo encontrar. Asegúrate de que sea público :)",
    },
    "ar": {  # Arabic
        "maintenance": "🔧 البوت تحت الصيانة. الرجاء المحاولة لاحقًا.",
        "banned": "تم حظرك من استخدام هذا البوت 😔",
        "thank_you": "شكرًا لاستخدامك - @z_downloadbot",
        "wrong": "عذرًا، حدث خطأ ما.",
        "went_wrong": "عذرًا، حدث خطأ ما.",
        "400": "400: آسف، لم يتم العثور عليه. تأكد من أنه متاح للجميع :)",
    },
    "hi": {  # Hindi
        "maintenance": "🔧 बॉट मेंटेनेंस में है। कृपया बाद में पुनः प्रयास करें।",
        "banned": "आप इस बॉट के उपयोग से प्रतिबंधित हैं 😔",
        "thank_you": "धन्यवाद - @z_downloadbot का उपयोग करने के लिए",
        "wrong": "उफ़, कुछ गलत हो गया।",
        "went_wrong": "उफ़, कुछ गलत हो गया।",
        "400": "400: क्षमा करें, इसे ढूंढा नहीं जा सका। कृपया सुनिश्चित करें कि यह सार्वजनिक रूप से उपलब्ध है :)",
    }
}

    if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text(INSTA_RESPONSES.get(user_lang, {}).get("maintenance","🔧 The bot is under maintenance. Please try again later."))
        return
    
    # Check Banned Users
    if message.from_user.id in banned_users:
        await message.reply_text(INSTA_RESPONSES.get(user_lang, {}).get("banned","You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
        return

    link = message.matches[0].group(0)
    try:
        m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
        url= link.replace("instagram.com","ddinstagram.com")
        url=url.replace("==","%3D%3D")
        if url.endswith("="):
            url = message.text  # Assuming the message contains the Instagram link
            caption = INSTA_RESPONSES.get(user_lang, {}).get("thank_you", "Thank you for using - @z_downloadbot")
    
    # Send the video with the localized caption
            dump_file = await message.reply_video(url[:-1], caption=caption)        
        else:
            caption = INSTA_RESPONSES.get(user_lang, {}).get("thank_you", "Thank you for using - @z_downloadbot")

    # Send the video with the localized caption
            dump_file = await message.reply_video(url, caption=caption)
        if 'dump_file' in locals():
           await dump_file.forward(DUMP_GROUP)
        await m.delete()
    except Exception as e:
        try:
            if "/reel/" in url:
               ddinsta=True 
               getdata = requests.get(url).text
               soup = bs4.BeautifulSoup(getdata, 'html.parser')
               meta_tag = soup.find('meta', attrs={'property': 'og:video'})
               try:
                  content_value =f"https://ddinstagram.com{meta_tag['content']}"
               except:
                   pass 
               if not meta_tag:
                  ddinsta=False
                  meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
             
                  if meta_tag.ok:
                     res=meta_tag.json()
               
                #     await message.reply(res)
                     meta=re.findall(r'href="(https?://[^"]+)"', res['data']) 
                     content_value = meta[0]
                  else:
                      return await message.reply(INSTA_RESPONSES.get(user_lang, {}).get("wrong", "oops something went wrong"))
               try:
                   if ddinsta:
                       caption = INSTA_RESPONSES.get(user_lang, {}).get("thank_you", "Thank you for using - @z_downloadbot")

    # Send the video with the localized caption
                       dump_file = await message.reply_video(url, caption=caption)
                   else:
                       caption = INSTA_RESPONSES.get(user_lang, {}).get("thank_you", "Thank you for using - @z_downloadbot")

    # Send the video with the localized caption
                       dump_file = await message.reply_video(url, caption=caption)
               except:
                   downfile=wget.download(content_value)
                   caption = INSTA_RESPONSES.get(user_lang, {}).get("thank_you", "Thank you for using - @z_downloadbot")

    # Send the video with the localized caption
                   dump_file = await message.reply_video(downfile, caption=caption) 
            elif "/p/" in url:
                  meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
                  if meta_tag.ok:
                     res=meta_tag.json()
                     meta=re.findall(r'href="(https?://[^"]+)"', res['data']) 
                  else:
                      return await message.reply(INSTA_RESPONSES.get(user_lang, {}).get("went_wrong", "oops something went wrong"))
              #    await message.reply(meta)
                  for i in range(len(meta) - 1):
                     com=await message.reply_text(meta[i])
                     await asyncio.sleep(1)
                     try:
                        downfile=wget.download(content_value)
                        caption = INSTA_RESPONSES.get(user_lang, {}).get("thank_you", "Thank you for using - @z_downloadbot")

    # Send the video with the localized caption
                        dump_file = await message.reply_video(com.text, caption=caption)
                        await com.delete()
                     except:
                         pass 
            elif "stories" in url:
                  meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
                  if meta_tag.ok:
                     res=meta_tag.json()
                     meta=re.findall(r'href="(https?://[^"]+)"', res['data']) 
                  else:
                      return await message.reply(INSTA_RESPONSES.get(user_lang, {}).get("went_wrong", "Oops something went wrong"))
                  try:
                     caption = INSTA_RESPONSES.get(user_lang, {}).get("thank_you", "Thank you for using - @z_downloadbot")

    # Send the video with the localized caption
                     dump_file = await message.reply_video(meta[0], caption=caption)
                  except:
                      com=await message.reply(meta[0])
                      await asyncio.sleep(1)
                      try:
                          caption = INSTA_RESPONSES.get(user_lang, {}).get("thank_you", "Thank you for using - @z_downloadbot")

    # Send the video with the localized caption
                          dump_file = await message.reply_video(com.text, caption=caption)
                          await com.delete()
                      except:
                          pass

        except KeyError:
            await message.reply(INSTA_RESPONSES.get(user_lang, {}).get(f"400","400: Sorry, Unable To Find It Make Sure Its Publically Available :)"))
        except Exception as e:
          #  await message.reply_text(f"https://ddinstagram.com{content_value}")
            if LOG_GROUP:
               await Mbot.send_message(LOG_GROUP,f"Instagram {e} {link}")
               await Mbot.send_message(LOG_GROUP, traceback.format_exc())
          #     await message.reply(tracemsg)
            ##optinal 
            await message.reply(INSTA_RESPONSES.get(user_lang, {}).get(f"400","400: Sorry, Unable To Find It Make Sure Its Publically Available :)"))

        finally:
            if 'dump_file' in locals():
               if DUMP_GROUP:
                  await dump_file.copy(DUMP_GROUP)
            await m.delete()
            if 'downfile' in locals():
                os.remove(downfile)
            
