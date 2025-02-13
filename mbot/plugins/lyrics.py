from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from mbot import Mbot
import requests 
from mbot.utils.util import is_maintenance_mode
from mbot import LOG_GROUP, OWNER_ID, SUDO_USERS, Mbot, AUTH_CHATS
import os
import json
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


API = "https://apis.xditya.me/lyrics?song="

@Mbot.on_message(filters.text & filters.command(["lyrics"]) & filters.private)
async def sng(bot, message):

          user_lang = get_user_language(message.from_user.id)
          LYRIC_RESPONSES = {
    "en": {
        "maintenance": "🔧 The bot is under maintenance. Please try again later.",
        "banned": "You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) ",
        "thank_you": "Thank you for using - @z_downloadbot",
        "wrong": "Oops, something went wrong.",
        "went_wrong": "Oops, something went wrong.",
        "400": "400: Sorry, Unable To Find It. Make sure it's publicly available :)",
        "Done": "Check out @z_downloadbot(music)  @Zpotify1(News)",
        "lyrics_not_found": "Lyrics not found for `{song}` ❌",
        "Searching": "`Searching`",
        "query": "give me a query eg `lyrics faded`"

    },
    "fa": {  # Farsi
        "maintenance": "🔧 ربات در حال تعمیر است. لطفاً بعداً دوباره امتحان کنید.",
        "banned": "شما از استفاده از این ربات ممنوع شده‌اید  😔",
        "thank_you": "با تشکر از شما برای استفاده از - @z_downloadbot",
        "wrong": "اوه، مشکلی پیش آمد.",
        "went_wrong": "اوه، مشکلی پیش آمد.",
        "400": "400: متأسفم، امکان یافتن آن وجود ندارد. لطفاً مطمئن شوید که عمومی است :)",
        "Done": "از @z_downloadbot (موسیقی) و @Zpotify1 (اخبار) دیدن کنید.",
        "lyrics_not_found": "متن ترانه برای `{song}` یافت نشد ❌",
        "Searching": "`در حال جستجو`",
        "query": "یک کوئری به من بدهید، مثلاً `lyrics faded`"
    },
    "ru": {  # Russian
        "maintenance": "🔧 Бот на техническом обслуживании. Пожалуйста, попробуйте позже.",
        "banned": "Вам запрещено использовать этого бота 😔",
        "thank_you": "Спасибо за использование - @z_downloadbot",
        "wrong": "Ой, что-то пошло не так.",
        "went_wrong": "Ой, что-то пошло не так.",
        "400": "400: Извините, не удалось найти. Убедитесь, что это доступно публично :)",
        "Done": "Проверьте @z_downloadbot (музыка) и @Zpotify1 (новости).",
        "lyrics_not_found": "Текст песни не найден для `{song}` ❌",
        "Searching": "`Поиск`",
        "query": "дайте мне запрос, например `lyrics faded`"

    },
    "es": {  # Spanish
        "maintenance": "🔧 El bot está en mantenimiento. Por favor, inténtalo más tarde.",
        "banned": "Estás baneado de usar este bot 😔",
        "thank_you": "Gracias por usar - @z_downloadbot",
        "wrong": "Uy, algo salió mal.",
        "went_wrong": "Uy, algo salió mal.",
        "400": "400: Lo siento, no se pudo encontrar. Asegúrate de que sea público :)",
        "Done": "Echa un vistazo a @z_downloadbot (música) y @Zpotify1 (noticias).",
        "lyrics_not_found": "No se encontraron letras para `{song}` ❌",
        "Searching": "`Buscando`",
        "query": "dame una consulta, por ejemplo `lyrics faded`"
    },
    "ar": {  # Arabic
        "maintenance": "🔧 البوت تحت الصيانة. الرجاء المحاولة لاحقًا.",
        "banned": "تم حظرك من استخدام هذا البوت 😔",
        "thank_you": "شكرًا لاستخدامك - @z_downloadbot",
        "wrong": "عذرًا، حدث خطأ ما.",
        "went_wrong": "عذرًا، حدث خطأ ما.",
        "400": "400: آسف، لم يتم العثور عليه. تأكد من أنه متاح للجميع :)",
        "Done": "تحقق من @z_downloadbot (موسيقى) و @Zpotify1 (أخبار).",
        "lyrics_not_found": "لم يتم العثور على كلمات الأغنية لـ `{song}` ❌",
        "Searching": "`جارٍ البحث`",
        "query": "أعطني استعلامًا، مثل `lyrics faded`"
    },
    "hi": {  # Hindi
        "maintenance": "🔧 बॉट मेंटेनेंस में है। कृपया बाद में पुनः प्रयास करें।",
        "banned": "आप इस बॉट के उपयोग से प्रतिबंधित हैं 😔",
        "thank_you": "धन्यवाद - @z_downloadbot का उपयोग करने के लिए",
        "wrong": "उफ़, कुछ गलत हो गया।",
        "went_wrong": "उफ़, कुछ गलत हो गया।",
        "400": "400: क्षमा करें, इसे ढूंढा नहीं जा सका। कृपया सुनिश्चित करें कि यह सार्वजनिक रूप से उपलब्ध है :)",
        "Done": "@z_downloadbot (संगीत) और @Zpotify1 (समाचार) देखें।",
        "lyrics_not_found": "`{song}` के लिए लिरिक्स नहीं मिले ❌",
        "Searching": "`खोज रहा है`",
        "query": "मुझे एक क्वेरी दें, उदाहरण के लिए `lyrics faded`"
    }
}

          if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
            await message.reply_text(LYRIC_RESPONSES.get(user_lang, {}).get("maintenance","🔧 The bot is under maintenance. Please try again later."))
            return
          
          # Check Banned Users
          if message.from_user.id in banned_users:
            await message.reply_text(LYRIC_RESPONSES.get(user_lang, {}).get("banned","You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
            return       
               
          mee = await message.reply_text(LYRIC_RESPONSES.get(user_lang, {}).get("Searching", "`Searching`"))
          try:
              song = message.text.split(None, 1)[1].lower().strip().replace(" ", "%20")
          except IndexError:
              await message.reply(LYRIC_RESPONSES.get(user_lang, {}).get("query", "give me a query eg `lyrics faded`"))
          chat_id = message.from_user.id
          rpl = lyrics(song)
          await mee.delete()
          try:
            await mee.delete()
            await message.reply(rpl)
          except Exception as e:                            
             await message.reply_text(
    INSTA_RESPONSES.get(user_lang, {}).get("lyrics_not_found", f"Lyrics not found for `{song}` ❌"),
    quote=True,
    reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url="https://t.me/zpotify1")]
    ])
)
          finally:
            await message.reply(LYRIC_RESPONSES.get(user_lang, {}).get("Done", "Check out @z_downloadbot(music)  @Zpotify1(News)"))



def search(song):
        r = requests.get(API + song)
        find = r.json()
        return find
       
def lyrics(song):
        fin = search(song)
        text = fin["lyrics"]
        return text
