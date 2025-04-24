from pyrogram.errors import FloodWait,Forbidden,UserIsBlocked,MessageNotModified,ChatWriteForbidden
from requests.exceptions import MissingSchema
from asyncio import sleep
#from mbot.utils.progress import progress
import time
from mutagen.id3 import ID3, APIC,error
from mutagen.easyid3 import EasyID3
from mbot import AUTH_CHATS, LOGGER, Mbot,LOG_GROUP,BUG
from pyrogram import filters,enums
from mbot.utils.mainhelper import parse_spotify_url,fetch_spotify_track,download_songs,thumb_down,copy,forward 
from mbot.utils.ytdl import getIds,ytdl_down,audio_opt
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
#import psutil
from os import mkdir
from os import environ
from shutil import rmtree
#from Script import script
from random import randint
#import random
#import eyed3 
from mutagen.easyid3 import EasyID3
#import eyed3
from lyricsgenius import Genius 
from pyrogram.types import Message
from pyrogram.errors.rpc_error import RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
#import psutil
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
#from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS
#from database.users_chats_db import db
#from database.ia_filterdb import Media
#from utils import temp
#from Script import script
from pyrogram.errors import ChatAdminRequired
from mbot import BUG,Mbot
import json
import os
from mutagen.mp3 import MP3
ADMINS = 5337964165
from requests.exceptions import MissingSchema
client = Spotify(auth_manager=SpotifyClientCredentials())
PICS = ("mbot/1162775.jpg mbot/danny-howe-bn-D2bCvpik-unsplash.jpg mbot/saurabh-gill-38RthwbB3nE-unsplash.jpg").split()
MAIN = bool(environ.get('MAIN', None))
genius = Genius("api_key")
LOG_TEXT_P = """
ID - <code>{}</code>
Name - {}
"""
pre = []
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
from mbot.utils.util import is_maintenance_mode
from mbot.utils.language_utils import get_user_language


SPOTIFY_RESPONSES = {
    "en": {
        "start_download": "🎧 Downloading your request... Please wait!",
        "download_complete": "✅ Download complete! Enjoy your music.",
        "error": "❌ Sorry, an error occurred. Please try again or report this issue.",
        "banned": "🚫 You are banned from using this bot.",
        "maintenance": "🔧 The bot is under maintenance. Please try again later.",
        "invalid_link": "⚠️ Are you sure this is a valid Spotify link?",
        "track_not_found": "⚠️ Track not found. Please try another link.",
        "playlist_info": "▶️ Playlist: {name}\n📝 Description: {description}\n👤 Owner: {owner}\n❤️ Followers: {followers}\n🔢 Total Tracks: {total_tracks}\n\n[IMAGE]({image_url})",
        "album_info": "💽 Album: {name}\n👥 Artists: {artists}\n🎧 Total Tracks: {total_tracks}\n🗂 Category: {album_type}\n📆 Published on: {release_date}\n\n[IMAGE]({image_url})",
        "artist_info": "👤 Artist: {name}\n❤️ Followers: {followers}\n🎶 Genres: {genres}\n🗂 Category: {type}\n❤️ Popularity: {popularity}\n\n[IMAGE]({image_url})",
        "thumbnail_error": "⚠️ Thumbnail download is not available for this track.",
        "preview_error": "⚠️ Audio preview is not available for this track.",
        "Under": "Bot Is Under Maintenance ⚠️",
        "301": "301 Use @y2mate_api_bot Insted Of Me 🚫",
        "417": "417 Not Critical, Retrying Again  🚫",
        "404": "404: sorry, audio preview is not available for this track 😔",
        "sorry": "sorry we removed support of  episode 😔 pls send other types album/playlist/track",
        "telegram says 500": "telegram says 500 error,so please try again later.❣️",
        "Unable To Procced": "Sorry, We Are Unable To Procced It 🤕❣️",
        "Flood_Wait": "Telegram says: [420 FLOOD_WAIT_X] - A wait of {e.value} seconds is required !",
        "Done": "Check out @z_downloadbot(music)  @Zpotify1(News)",
        "Report": 'please report to the dev say "private version" with above  error occurred message',
        "Rights Check": "Dude check weather I have enough rights😎⚠️",
        "title": "🎧 Title",
        "artist": "🎤 Artist",
        "album": "💽 Album",
        "release_year": "🗓 Release Year",
        "image": "IMAGE",
        "track_id": "Track ID"
    },
    "fa": {
        "start_download": "🎧 درخواست شما در حال دانلود... لطفا منتظر بمانید!",
        "download_complete": "✅ دانلود کامل شد! از موسیقی خود لذت ببرید.",
        "error": "❌ متاسفانه خطایی رخ داد. لطفا دوباره امتحان کنید یا مشکل را گزارش دهید.",
        "banned": "🚫 شما از استفاده از این ربات محروم شده‌اید.",
        "maintenance": "🔧 ربات در حال تعمیر و نگهداری است. لطفا بعدا تلاش کنید.",
        "invalid_link": "⚠️ آیا مطمئن هستید که این لینک معتبر است؟",
        "track_not_found": "⚠️ آهنگ پیدا نشد. لطفا لینک دیگری را امتحان کنید.",
        "playlist_info": "▶️ پلی‌لیست: {name}\n📝 توضیحات: {description}\n👤 مالک: {owner}\n❤️ دنبال‌کنندگان: {followers}\n🔢 تعداد آهنگ‌ها: {total_tracks}\n\n[IMAGE]({image_url})",
        "album_info": "💽 آلبوم: {name}\n👥 هنرمندان: {artists}\n🎧 تعداد آهنگ‌ها: {total_tracks}\n🗂 دسته‌بندی: {album_type}\n📆 تاریخ انتشار: {release_date}\n\n[IMAGE]({image_url})",
        "artist_info": "👤 هنرمند: {name}\n❤️ دنبال‌کنندگان: {followers}\n🎶 ژانرها: {genres}\n🗂 دسته‌بندی: {type}\n❤️ محبوبیت: {popularity}\n\n[IMAGE]({image_url})",
        "thumbnail_error": "⚠️ دانلود تصویر برای این آهنگ امکان‌پذیر نیست.",
        "preview_error": "⚠️ پیش‌نمایش صوتی برای این آهنگ موجود نیست.",
        "Under": "ربات در حال تعمیر و نگهداری است ⚠️",
        "301": "301 به جای من از @y2mate_api_bot استفاده کنید 🚫",
        "417": "417 بحرانی نیست، دوباره تلاش می‌کنیم 🚫",
        "404": "404: متاسفانه پیش‌نمایش صوتی برای این آهنگ موجود نیست 😔",
        "sorry": "متاسفانه پشتیبانی از اپیزود حذف شده است 😔 لطفاً انواع دیگر مانند آلبوم/پلی‌لیست/آهنگ ارسال کنید.",
        "telegram says 500": "تلگرام می‌گوید خطای 500، لطفاً بعداً دوباره تلاش کنید.❣️",
        "Unable To Procced": "متاسفانه، ما قادر به پردازش آن نیستیم 🤕❣️",
        "Flood_Wait": "تلگرام می‌گوید: [420 FLOOD_WAIT_X] - نیاز به انتظار {e.value} ثانیه است!",
        "Done": "از @z_downloadbot (موسیقی) و @Zpotify1 (اخبار) دیدن کنید.",
        "Report": 'لطفاً به توسعه‌دهنده گزارش دهید و بگویید "نسخه خصوصی" به همراه پیام خطای بالا.',
        "Rights Check": "دوست، بررسی کن که آیا من به اندازه کافی حقوق دارم 😎⚠️",
        "title": "🎧 عنوان",
        "artist": "🎤 هنرمند",
        "album": "💽 آلبوم",
        "release_year": "🗓 سال انتشار",
        "image": "تصویر",
        "track_id": "شناسه آهنگ"
    },
    "es": {
        "start_download": "🎧 Descargando tu solicitud... ¡Por favor espera!",
        "download_complete": "✅ ¡Descarga completa! Disfruta de tu música.",
        "error": "❌ Lo siento, ocurrió un error. Inténtalo de nuevo o informa del problema.",
        "banned": "🚫 Estás prohibido de usar este bot.",
        "maintenance": "🔧 El bot está en mantenimiento. Inténtalo más tarde.",
        "invalid_link": "⚠️ ¿Estás seguro de que este enlace de Spotify es válido?",
        "track_not_found": "⚠️ Pista no encontrada. Intenta con otro enlace.",
        "playlist_info": "▶️ Lista de reproducción: {name}\n📝 Descripción: {description}\n👤 Propietario: {owner}\n❤️ Seguidores: {followers}\n🔢 Total de pistas: {total_tracks}\n\n[IMAGE]({image_url})",
        "album_info": "💽 Álbum: {name}\n👥 Artistas: {artists}\n🎧 Total de pistas: {total_tracks}\n🗂 Categoría: {album_type}\n📆 Publicado el: {release_date}\n\n[IMAGE]({image_url})",
        "artist_info": "👤 Artista: {name}\n❤️ Seguidores: {followers}\n🎶 Géneros: {genres}\n🗂 Categoría: {type}\n❤️ Popularidad: {popularity}\n\n[IMAGE]({image_url})",
        "thumbnail_error": "⚠️ No se puede descargar la miniatura de esta pista.",
        "preview_error": "⚠️ La vista previa de audio no está disponible para esta pista.",
        "Under": "El bot está en mantenimiento ⚠️",
        "301": "301 Usa @y2mate_api_bot en lugar de mí �",
        "417": "417 No es crítico, reintentando de nuevo 🚫",
        "404": "404: Lo siento, la vista previa de audio no está disponible para esta pista 😔",
        "sorry": "Lo siento, eliminamos el soporte para episodios 😔 Por favor, envía otros tipos como álbum/lista de reproducción/pista.",
        "telegram says 500": "Telegram dice error 500, por favor, inténtalo de nuevo más tarde.❣️",
        "Unable To Procced": "Lo siento, no podemos procesarlo 🤕❣️",
        "Flood_Wait": "Telegram dice: [420 FLOOD_WAIT_X] - Se requiere una espera de {e.value} segundos.",
        "Done": "Echa un vistazo a @z_downloadbot (música) y @Zpotify1 (noticias).",
        "Report": 'Por favor, informa al desarrollador diciendo "versión privada" con el mensaje de error anterior.',
        "Rights Check": "Amigo, verifica si tengo suficientes derechos 😎⚠️",
        "title": "🎧 Título",
        "artist": "🎤 Artista",
        "album": "💽 Álbum",
        "release_year": "🗓 Año de lanzamiento",
        "image": "IMAGEN",
        "track_id": "ID de pista"
    },
    "ru": {
        "start_download": "🎧 Загружается ваш запрос... Пожалуйста, подождите!",
        "download_complete": "✅ Загрузка завершена! Наслаждайтесь вашей музыкой.",
        "error": "❌ Извините, произошла ошибка. Попробуйте еще раз или сообщите о проблеме.",
        "banned": "🚫 Вам запрещено использовать этого бота.",
        "maintenance": "🔧 Бот на техническом обслуживании. Попробуйте позже.",
        "invalid_link": "⚠️ Вы уверены, что это действительная ссылка на Spotify?",
        "track_not_found": "⚠️ Трек не найден. Попробуйте другую ссылку.",
        "playlist_info": "▶️ Плейлист: {name}\n📝 Описание: {description}\n👤 Владелец: {owner}\n❤️ Подписчики: {followers}\n🔢 Всего треков: {total_tracks}\n\n[IMAGE]({image_url})",
        "album_info": "💽 Альбом: {name}\n👥 Исполнители: {artists}\n🎧 Всего треков: {total_tracks}\n🗂 Категория: {album_type}\n📆 Дата выхода: {release_date}\n\n[IMAGE]({image_url})",
        "artist_info": "👤 Исполнитель: {name}\n❤️ Подписчики: {followers}\n🎶 Жанры: {genres}\n🗂 Категория: {type}\n❤️ Популярность: {popularity}\n\n[IMAGE]({image_url})",
        "thumbnail_error": "⚠️ Миниатюра для этого трека недоступна.",
        "preview_error": "⚠️ Аудио-превью для этого трека недоступно.",
        "Under": "Бот на техническом обслуживании ⚠️",
        "301": "301 Используйте @y2mate_api_bot вместо меня 🚫",
        "417": "417 Не критично, пробуем снова 🚫",
        "404": "404: Извините, аудио-превью для этого трека недоступно 😔",
        "sorry": "Извините, поддержка эпизодов удалена 😔 Пожалуйста, отправьте другие типы, такие как альбом/плейлист/трек.",
        "telegram says 500": "Telegram сообщает об ошибке 500, пожалуйста, попробуйте позже.❣️",
        "Unable To Procced": "Извините, мы не можем обработать это 🤕❣️",
        "Flood_Wait": "Telegram сообщает: [420 FLOOD_WAIT_X] - Требуется ожидание {e.value} секунд!",
        "Done": "Проверьте @z_downloadbot (музыка) и @Zpotify1 (новости).",
        "Report": 'Пожалуйста, сообщите разработчику, сказав "частная версия" с сообщением об ошибке выше.',
        "Rights Check": "Чувак, проверь, есть ли у меня достаточно прав 😎⚠️",
        "title": "🎧 Название",
        "artist": "🎤 Исполнитель",
        "album": "💽 Альбом",
        "release_year": "🗓 Год выпуска",
        "image": "ИЗОБРАЖЕНИЕ",
        "track_id": "ID трека"
    },
    "ar": {
        "start_download": "🎧 يتم تنزيل طلبك... يرجى الانتظار!",
        "download_complete": "✅ تم اكتمال التنزيل! استمتع بموسيقاك.",
        "error": "❌ عذرًا، حدث خطأ. يرجى المحاولة مرة أخرى أو الإبلاغ عن المشكلة.",
        "banned": "🚫 أنت محظور من استخدام هذا البوت.",
        "maintenance": "🔧 البوت تحت الصيانة. يرجى المحاولة لاحقًا.",
        "invalid_link": "⚠️ هل أنت متأكد أن هذا رابط سبوتيفاي صالح؟",
        "track_not_found": "⚠️ لم يتم العثور على المسار. يرجى تجربة رابط آخر.",
        "playlist_info": "▶️ قائمة التشغيل: {name}\n📝 الوصف: {description}\n👤 المالك: {owner}\n❤️ المتابعون: {followers}\n🔢 إجمالي المسارات: {total_tracks}\n\n[IMAGE]({image_url})",
        "album_info": "💽 الألبوم: {name}\n👥 الفنانون: {artists}\n🎧 إجمالي المسارات: {total_tracks}\n🗂 الفئة: {album_type}\n📆 تاريخ الإصدار: {release_date}\n\n[IMAGE]({image_url})",
        "artist_info": "👤 الفنان: {name}\n❤️ المتابعون: {followers}\n🎶 الأنواع: {genres}\n🗂 الفئة: {type}\n❤️ الشعبية: {popularity}\n\n[IMAGE]({image_url})",
        "thumbnail_error": "⚠️ لا يمكن تنزيل الصورة المصغرة لهذا المسار.",
        "preview_error": "⚠️ المعاينة الصوتية غير متاحة لهذا المسار.",
        "Under": "البوت تحت الصيانة ⚠️",
        "301": "301 استخدم @y2mate_api_bot بدلاً مني 🚫",
        "417": "417 ليس حرجًا، يتم إعادة المحاولة مرة أخرى 🚫",
        "404": "404: عذرًا، المعاينة الصوتية غير متاحة لهذا المسار 😔",
        "sorry": "عذرًا، لقد أزلنا دعم الحلقات 😔 يرجى إرسال أنواع أخرى مثل الألبوم/قائمة التشغيل/المسار.",
        "telegram says 500": "Telegram يقول خطأ 500، يرجى المحاولة مرة أخرى لاحقًا.❣️",
        "Unable To Procced": "عذرًا، لا يمكننا معالجة ذلك 🤕❣️",
        "Flood_Wait": "Telegram يقول: [420 FLOOD_WAIT_X] - يلزم انتظار {e.value} ثانية!",
        "Done": "تحقق من @z_downloadbot (موسيقى) و @Zpotify1 (أخبار).",
        "Report": 'يرجى الإبلاغ إلى المطور بقول "نسخة خاصة" مع رسالة الخطأ أعلاه.',
        "Rights Check": "يا صديقي، تحقق مما إذا كان لدي الصلاحيات الكافية 😎⚠️",
        "title": "🎧 العنوان",
        "artist": "🎤 الفنان",
        "album": "💽 الألبوم",
        "release_year": "🗓 سنة الإصدار",
        "image": "صورة",
        "track_id": "معرف المسار"
    },
    "hi": {
        "start_download": "🎧 आपका अनुरोध डाउनलोड हो रहा है... कृपया प्रतीक्षा करें!",
        "download_complete": "✅ डाउनलोड पूरा हुआ! अपने संगीत का आनंद लें।",
        "error": "❌ क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें या इस समस्या की रिपोर्ट करें।",
        "banned": "🚫 आपको इस बॉट के उपयोग से प्रतिबंधित किया गया है।",
        "maintenance": "🔧 बॉट का रखरखाव किया जा रहा है। कृपया बाद में प्रयास करें।",
        "invalid_link": "⚠️ क्या आपको यकीन है कि यह एक मान्य स्पॉटीफाई लिंक है?",
        "track_not_found": "⚠️ ट्रैक नहीं मिला। कृपया किसी अन्य लिंक का प्रयास करें।",
        "playlist_info": "▶️ प्लेलिस्ट: {name}\n📝 विवरण: {description}\n👤 मालिक: {owner}\n❤️ अनुयायी: {followers}\n🔢 कुल ट्रैक: {total_tracks}\n\n[IMAGE]({image_url})",
        "album_info": "💽 एल्बम: {name}\n👥 कलाकार: {artists}\n🎧 कुल ट्रैक: {total_tracks}\n🗂 श्रेणी: {album_type}\n📆 प्रकाशित तिथि: {release_date}\n\n[IMAGE]({image_url})",
        "artist_info": "👤 कलाकार: {name}\n❤️ अनुयायी: {followers}\n🎶 शैलियाँ: {genres}\n🗂 श्रेणी: {type}\n❤️ लोकप्रियता: {popularity}\n\n[IMAGE]({image_url})",
        "thumbnail_error": "⚠️ इस ट्रैक के लिए थंबनेल डाउनलोड उपलब्ध नहीं है।",
        "preview_error": "⚠️ इस ट्रैक के लिए ऑडियो पूर्वावलोकन उपलब्ध नहीं है।",
        "Under": "बॉट का रखरखाव चल रहा है ⚠️",
        "301": "301 मेरे बजाय @y2mate_api_bot का उपयोग करें 🚫",
        "417": "417 गंभीर नहीं है, फिर से प्रयास कर रहे हैं 🚫",
        "404": "404: क्षमा करें, इस ट्रैक के लिए ऑडियो पूर्वावलोकन उपलब्ध नहीं है 😔",
        "sorry": "क्षमा करें, हमने एपिसोड का समर्थन हटा दिया है 😔 कृपया अन्य प्रकार जैसे एल्बम/प्लेलिस्ट/ट्रैक भेजें।",
        "telegram says 500": "Telegram कहता है 500 त्रुटि, कृपया बाद में पुनः प्रयास करें।❣️",
        "Unable To Procced": "क्षमा करें, हम इसे संसाधित करने में असमर्थ हैं 🤕❣️",
        "Flood_Wait": "Telegram कहता है: [420 FLOOD_WAIT_X] - {e.value} सेकंड की प्रतीक्षा आवश्यक है!",
        "Done": "@z_downloadbot (संगीत) और @Zpotify1 (समाचार) देखें।",
        "Report": 'कृपया डेवलपर को "निजी संस्करण" कहकर और ऊपर की त्रुटि संदेश के साथ रिपोर्ट करें।',
        "Rights Check": "यार, जांचें कि क्या मेरे पास पर्याप्त अधिकार हैं 😎⚠️",
        "title": "🎧 शीर्षक",
        "artist": "🎤 कलाकार",
        "album": "💽 एल्बम",
        "release_year": "🗓 रिलीज़ वर्ष",
        "image": "छवि",
        "track_id": "ट्रैक आईडी"
    },
}

LANGUAGE_STRINGS = {
    "en": {  # English
        "title": "🎧 Title",
        "artist": "🎤 Artist",
        "album": "💽 Album",
        "release_year": "🗓 Release Year",
        "image": "IMAGE",
        "track_id": "Track ID",
        "track_not_found": "Track Not Found ⚠️",
        "playlist": "Playlist",
        "description": "Description",
        "owner": "Owner",
        "followers": "Followers",
        "total_tracks": "Total Tracks",
        "valid_playlist_question": "Are you sure it's a valid playlist? 🤨",
        "valid_song_question": "are you sure it's a valid song 🤨?"

    },
    "fa": {  # Persian (Farsi)
        "title": "🎧 عنوان",
        "artist": "🎤 هنرمند",
        "album": "💽 آلبوم",
        "release_year": "🗓 سال انتشار",
        "image": "تصویر",
        "track_id": "شناسه آهنگ",
        "track_not_found": "آهنگ پیدا نشد ⚠️",
        "playlist": "لیست پخش",
        "description": "توضیحات",
        "owner": "مالک",
        "followers": "دنبال کنندگان",
        "total_tracks": "تعداد ترک‌ها",
        "valid_playlist_question": "آیا مطمئن هستید که این یک لیست پخش معتبر است؟ 🤨",
        "valid_song_question": "آیا مطمئن هستید که آهنگ معتبری است؟ 🤨"
    },
    "es": {  # Spanish
        "title": "🎧 Título",
        "artist": "🎤 Artista",
        "album": "💽 Álbum",
        "release_year": "🗓 Año de lanzamiento",
        "image": "IMAGEN",
        "track_id": "ID de pista",
        "track_not_found": "Pista no encontrada ⚠️",
        "playlist": "Lista de reproducción",
        "description": "Descripción",
        "owner": "Propietario",
        "followers": "Seguidores",
        "total_tracks": "Total de pistas",
        "valid_playlist_question": "¿Estás seguro de que es una lista de reproducción válida? 🤨",
        "valid_song_question": "¿Estás segura de que es una canción válida 🤨?"

    },
    "ru": {  # Russian
        "title": "🎧 Название",
        "artist": "🎤 Исполнитель",
        "album": "💽 Альбом",
        "release_year": "🗓 Год выпуска",
        "image": "ИЗОБРАЖЕНИЕ",
        "track_id": "ID трека",
        "track_not_found": "Трек не найден ⚠️",
        "playlist": "Плейлист",
        "description": "Описание",
        "owner": "Владелец",
        "followers": "Подписчики",
        "total_tracks": "Всего треков",
        "valid_playlist_question": "¿Я уверен, что список воспроизведений действителен? 🤨",
        "valid_song_question": "вы уверены, что это допустимая песня 🤨?"
    },
    "ar": {  # Arabic
        "title": "🎧 العنوان",
        "artist": "🎤 الفنان",
        "album": "💽 الألبوم",
        "release_year": "🗓 سنة الإصدار",
        "image": "صورة",
        "track_id": "معرف المسار",
        "track_not_found": "لم يتم العثور على المسار ⚠️",
        "playlist": "قائمة تشغيل",
        "description": "الوصف",
        "owner": "المالك",
        "followers": "المتابعون",
        "total_tracks": "إجمالي المسارات",
        "valid_playlist_question": "هل من المؤكد أنها قائمة إعادة إنتاج صالحة؟ 🤨",
        "valid_song_question": "هل أنت متأكد من أن هذه أغنية صالحة 🤨؟"

    },
    "hi": {  # Hindi
        "title": "🎧 शीर्षक",
        "artist": "🎤 कलाकार",
        "album": "💽 एल्बम",
        "release_year": "🗓 रिलीज़ वर्ष",
        "image": "छवि",
        "track_id": "ट्रैक आईडी",
        "track_not_found": "ट्रैक नहीं मिला ⚠️",
        "playlist": "प्लेलिस्ट",
        "description": "विवरण",
        "owner": "मालिक",
        "followers": "फॉलोअर्स",
        "total_tracks": "कुल गाने",
        "valid_playlist_question": "¿क्या आप वैध पुनरुत्पादन सूची तैयार कर सकते हैं? 🤨",
        "valid_song_question": "क्या आप सुनिश्चित हैं कि यह एक वैध गीत है 🤨?"
    }
}



@Mbot.on_message(filters.incoming & filters.regex(r'https?://open.spotify.com[^\s]+') | filters.incoming & filters.regex(r'https?://spotify.link[^\s]+'))
async def spotify_dl(Mbot,message: Message):

    user_lang = get_user_language(message.from_user.id)  # Fetch user language from your function
    strings = LANGUAGE_STRINGS.get(user_lang, LANGUAGE_STRINGS["en"])  # Default to English if not found

# Check maintenance mode
    if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text(SPOTIFY_RESPONSES.get(user_lang, {}).get("maintenance","🔧 The bot is under maintenance. Please try again later."))
        return

    # Check Banned Users
    if message.from_user.id in banned_users:
        await message.reply_text(SPOTIFY_RESPONSES.get(user_lang, {}).get("banned","You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
        return
        
    if MAIN:
       await message.reply_text(SPOTIFY_RESPONSES.get(user_lang, {}).get(f"Under","Bot Is Under Maintenance ⚠️"))
       return
    link = message.matches[0].group(0)
    if "https://www.deezer.com" in link:
       return
    if "https://youtu.be" in link:
          return await message.reply(SPOTIFY_RESPONSES.get(user_lang, {}).get("301","301 Use @y2mate_api_bot Insted Of Me 🚫"))
    try:
        parsed_item = await parse_spotify_url(link)
        item_type, item_id = parsed_item[0],parsed_item[1]
    except Exception as e:
        pass
        cr =  await message.reply(SPOTIFY_RESPONSES.get(user_lang, {}).get("417", "417 Not Critical, Retrying Again  🚫"))
        await  Mbot.send_message(BUG,f" Private r: Unsupported [URI](link) Not critical {message.chat.id}  {message.from_user.id} {message.from_user.mention}")   
        try:
            link = head(link).headers['location']
            parsed_item = await parse_spotify_url(link)
            item_type, item_id = parsed_item[0],parsed_item[1]
        except Exception as e:
            pass 
            await  Mbot.send_message(BUG,f" Private r: Unsupported [URI](link) Failed twice {message.chat.id}  {message.from_user.id} {message.from_user.mention}")
            return await cr.edit(f"501: This URI Is Not Supported ⚠")
    if message.text.startswith("/thumb"):
       try:
          await Mbot.send_message(BUG,f"Thumb download requested from {message.from_user.mention}")
          parsed_item = await parse_spotify_url(link)
          item_type, item_id = parsed_item[0],parsed_item[1]
          if item_type == "track":
             item = client.track(track_id=item_id)
             alb = client.album(album_id=item['album']['id'],)
             await message.reply_document(alb['images'][0]['url'])
          elif item_type == "playlist":
               play = client.playlist(playlist_id=item_id,)
               await message.reply_document(play['images'][0]['url'])
          elif item_type == "album":
               alb = client.album(album_id=item_id,)
               await message.reply_document(alb['images'][0]['url'])
          elif item_type == "artist":
               art = client.artist(item_id)
               await message.reply_document(art['images'][0]['url'])
       except Exception as e:
           pass
           await message.reply("404: sorry, thumbnail download is not available for this track 😔")
           await Mbot.send_message(BUG,f" thumb 400 {e}")
       return 
    if message.text.startswith("/preview"):
          parsed_item = await parse_spotify_url(link)
          item_type, item_id = parsed_item[0],parsed_item[1]
          if item_type == "track":
             try:
                 await Mbot.send_message(BUG,f"Preview download requested from {message.from_user.mention}")
                 item = client.track(track_id=item_id)
                 await  message.reply_audio(f"{item.get('preview_url')}")
             except Exception as e:
                 pass
                 await message.reply(SPOTIFY_RESPONSES.get(user_lang, {}).get("404","404: sorry, audio preview is not available for this track 😔"))
                 await Mbot.send_message(BUG,e)
          return 
    u = message.from_user.id
    randomdir = f"/tmp/{str(randint(1,100000000))}"
    mkdir(randomdir)
    try:
        m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
        await message.reply_chat_action(enums.ChatAction.TYPING)
    except ChatWriteForbidden:
        pass

    try:
        parsed_item = await parse_spotify_url(link)
        item_type, item_id = parsed_item[0],parsed_item[1]
        if item_type in ["show", "episode"]:
            items = await getIds(link)
            for item in items:
                cForChat = await message.reply_chat_action(enums.ChatAction.UPLOAD_PHOTO)
                sleeeps = await sleep (0.9)
                PForCopy = await message.reply_photo(item[5],caption=f"✔️ Episode Name : `{item[3]}`\n🕔 Duration : {item[4]//60}:{item[4]%60}")
                reply = await message.reply_text(SPOTIFY_RESPONSES.get(user_lang, {}).get(f"sorry", "sorry we removed support of  episode 😔 pls send other types album/playlist/track"))
       
        elif item_type == "track":
            song = await fetch_spotify_track(client,item_id)
            #sleeeps = await sleep (0.9)
            try:
                item = client.track(track_id=item_id)
            except:
                pass
               
            try:
                if not item:
           #         await message.reply_chat_action(enums.ChatAction.UPLOAD_PHOTO)
                  # Get user's language

                            PForCopy = await message.reply_photo(
    song.get('cover'),
    caption=(
        f"{SPOTIFY_RESPONSES.get(user_lang, SPOTIFY_RESPONSES['en'])['title']} : `{song['name']}`\n"
        f"{SPOTIFY_RESPONSES.get(user_lang, SPOTIFY_RESPONSES['en'])['artist']} : `{song['artist']}`\n"
        f"{SPOTIFY_RESPONSES.get(user_lang, SPOTIFY_RESPONSES['en'])['album']} : `{song['album']}`\n"
        f"{SPOTIFY_RESPONSES.get(user_lang, SPOTIFY_RESPONSES['en'])['release_year']} : `{song['year']}`\n\n"
        f"[{SPOTIFY_RESPONSES.get(user_lang, SPOTIFY_RESPONSES['en'])['image']}]({song.get('cover')})\n"
        f"{SPOTIFY_RESPONSES.get(user_lang, SPOTIFY_RESPONSES['en'])['track_id']} : `{song['deezer_id']}`"
    )
)

           #         await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
            #        document= await message.reply_document(song.get('cover'))  
                else:
                     PForCopy = await message.reply_photo(
    item['album']['images'][0]['url'],
    caption=(
        f"{strings['title']} : `{song['name']}`\n"
        f"{strings['artist']} : `{song['artist']}`\n"
        f"{strings['album']} : `{song['album']}`\n"
        f"{strings['release_year']} : `{song['year']}`\n"
        f"❗️{strings['is_local']} : `{item['is_local']}`\n"
        f"🌐 {strings['isrc']} : `{item['external_ids']['isrc']}`\n\n"
        f"[{strings['image']}]({item['album']['images'][0]['url']})\n"
        f"{strings['track_id']} : `{song['deezer_id']}`"
    ),
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❌", callback_data="cancel")]])
)

              #       document= await message.reply_document(alb['images'][0]['url'],
                #     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❌", callback_data="cancel")]]))
              # await message.reply_audio(f"{item.get('preview_url')}")
            except:
                pass
         #       await message.reply_chat_action(enums.ChatAction.TYPING)
                PForCopy = await message.reply_text(
    f"{strings['title']} : `{song['name']}`\n"
    f"{strings['artist']} : `{song['artist']}`\n"
    f"{strings['album']} : `{song['album']}`\n"
    f"{strings['release_year']} : `{song['year']}`\n\n"
    f"[{strings['image']}]({song.get('cover')})\n"
    f"{strings['track_id']} : `{song['deezer_id']}`"
)

       #     try:
       #         await message.reply_audio(f"{item.get('preview_url')}",
       #         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="❌", callback_data="cancel")]]))
      #      except:
      #          pass
      #      await sleep(0.6)
            try:
               path = await download_songs(item,randomdir)
            except Exception as e:
                pass
## optional you can clear this or add this by using #
                await message.reply(e)
          #      await Mbot.send_message(BUG,e)
                await message.reply_text(
    f"[{song.get('name')} - {song.get('artist')}]"
    f"(https://open.spotify.com/track/{song.get('deezer_id')}) "
    f"{strings['track_not_found']}"
)

         #       await message.reply_text(f"try `/saavn {song.get('name')} - {song.get('artist')}`")
            thumbnail = await thumb_down(item['album']['images'][0]['url'],song.get('deezer_id'))
            audio = EasyID3(path)
            try:
                audio["TITLE"] = f" {song.get('name')}"
                audio["originaldate"] = song.get('year')
              #  audio["YEAR_OF_RELEASE"] = song.get('year')
                audio["WEBSITE"] = "https://t.me/z_downloadbot"
            #    audio["GEEK_SCORE"] = "9"
                audio["ARTIST"] = song.get('artist')                                                                            
                audio["ALBUM"] = song.get('album')
                audio["DATE"] = song.get('year')
                audio["DISCNUMBER"] =f" {item['disc_number']}"
                audio["TRACKNUMBER"] =f" {item['track_number']}"
                try:
                    audio["ISRC"] = item['external_ids']['isrc']
                except:
                    pass
                try:
                    songGenius = genius.search_song(song('name'), song('artist'))
                    audio["LYRICS"] = (songGenius.lyrics)
                except:
                    pass
                audio.save()
                try:
                   audio = MP3(path, ID3=ID3)
                   audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(thumbnail,'rb').read()))
                   audio.save()
                except Exception :
                    pass   
            except:
                pass
            audio.save()
            caption = f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {strings['album']} {song.get('album')} - {strings['artist']} {song.get('artist')}"

# Send the audio message with translated caption
            AForCopy = await message.reply_audio(
    path,
    performer=f"{song.get('artist')}",
    title=f"{song.get('name')} - {song.get('artist')}",
    caption=caption,
    thumb=thumbnail,
    parse_mode=enums.ParseMode.MARKDOWN,
    quote=True
)
            if LOG_GROUP:
               await copy(PForCopy,AForCopy)
        elif item_type == "playlist":
            play = client.playlist(playlist_id=item_id,)
           # if u in PREM:
            tracks = client.playlist_items(playlist_id=item_id,additional_types=['track'], offset=0, market=None)
          #  else:
         #        tracks = client.playlist_items(playlist_id=item_id,additional_types=['track'], limit=30, offset=0, market=None) 
            total_tracks = tracks.get('total')
            track_no = 1
            try:
                # Create the caption dynamically using the translated strings
                caption = f"▶️{strings['playlist']}:{play['name']}\n📝{strings['description']}:{play['description']}\n👤{strings['owner']}:{play['owner']['display_name']}\n❤️{strings['followers']}:{play['followers']['total']}\n🔢 {strings['total_tracks']}:{play['tracks']['total']}\n\n[IMAGES]({play['images'][0]['url']})\n{play['uri']}"

# Send the photo with the translated caption
                PForCopy = await message.reply_photo(
    play['images'][0]['url'],
    caption=caption
)
          #      document= await message.reply_document(play['images'][0]['url'])
          #      sup = 40
           #     if u in PREM:
         #          re = 2
         #       else:
         #            re = play['tracks']['total']
          #      if re > sup:
          #         await message.reply(f"trying to send first 40 tracks of {play['name']} total {re}")     
            except Exception as e:
                pass
                # Create the caption dynamically using the translated strings
                caption = f"▶️{strings['playlist']}:{play['name']}\n📝{strings['description']}:{play['description']}\n👤{strings['owner']}:{play['owner']['display_name']}\n❤️{strings['followers']}:{play['followers']['total']}\n🔢 {strings['total_tracks']}:{play['tracks']['total']}\n\n[IMAGES]({play['images'][0]['url']})\n{play['tracks']['uri']}"

# Send the playlist details message
                PForCopy = await message.reply(
                caption
)

# Send the confirmation message
                confirmation_text = strings['valid_playlist_question']
                await message.reply(confirmation_text)
            
            for track in tracks['items']:
                song = await fetch_spotify_track(client,track.get('track').get('id'))
                item = client.track(track_id=track['track']['id'])
             #   cForChat = await message.reply_chat_action(enums.ChatAction.TYPING)
               #sleeeps = await sleep (0.6)
            #    try:
           #        PForCopy = await message.reply_photo(song.get('cover'),caption=f"🎧 Title : `{song['name']}`\n🎤 Artist : `{song['artist']}`\n💽 Album : `{song['album']}`\n🗓 Release Year: `{song['year']}`\n❗️Is Local: `{track['is_local']}`\n🔢 Track No: `{track_no}`\n🔢 Total Track: `{total_tracks}`\n\n[IMAGE]({song.get('cover')})\ntrack id:`{song['deezer_id']}`")
            #       document= await message.reply_document(song.get('cover'))
             #   except:
              #      pass
                  #  PForCopy = await message.reply_text(f"🎧 Title : `{song['name']}`\n🎤 Artist : `{song['artist']}`\n💽 Album : `{song['album']}`\n🗓 Release Year: `{song['year']}`\n\n[IMAGE]({song.get('cover')})\ntrack id:`{song['deezer_id']}`")
                #PForCopy = await message.reply_photo(song.get('cover'),caption=f"🎧 Title : `{song['name']}`\n🎤 Artist : `{song['artist']}`\n💽 Album : `{song['album']}`\n🎼 Genre : `{song['genre']}`\n🗓 Release Year: `{song['year']}`\n🔢 Track No: `{song['playlist_num']}`\n🔢 Total Track: `{total_tracks}`\n\n[IMAGE]({song.get('cover')})\ntrack id:`{song['deezer_id']}")
                await sleep(0.6)
                try:
                   path = await download_songs(item,randomdir)
                except Exception as e:
                    pass
## optional you can clear this or add this by using #
                    await message.reply(e)
                    await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
            #        await message.reply_text(f"try `/saavn {song.get('name')} - {song.get('artist')}`")
            #        await message.reply(f"[Click Here](https://t.me/)")
                thumbnail = await thumb_down(song.get('cover'),song.get('deezer_id'))
                await sleep(0.6)
                audio = EasyID3(path)
                try:
                    audio["TITLE"] = f" {song.get('name')} "
                    audio["originaldate"] = song.get('year')
                #    audio["YEAR_OF_RELEASE"] = song.get('year')
                    audio["WEBSITE"] = "https://t.me/z_downloadbot"
              #      audio["GEEK_SCORE"] = "9"
                    audio["ARTIST"] = song.get('artist')                                                                           
                    audio["ALBUM"] = song.get('album')
                    audio["DATE"] = song.get('year')
                    audio["discnumber"] =f" {item['disc_number']}"
                    audio["tracknumber"] =f" {item['track_number']}"
                    try:
                        audio["ISRC"] = item['external_ids']['isrc']
                    except:
                        pass
                    try:
                       songGenius = genius.search_song(song('name'), song('artist'))
                       audio["LYRICS"] = (songGenius.lyrics)
                    except:
                        pass
                except:
                     pass
                audio.save()
                try:
                   audio = MP3(path, ID3=ID3)
                   audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(thumbnail,'rb').read()))
                except Exception as e:
                    pass
                audio.save()
                try:
                    AForCopy = await message.reply_audio(path,performer=song.get('artist'),title=f"{song.get('name')} - {song.get('artist')}",caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}",thumb=thumbnail,parse_mode=enums.ParseMode.MARKDOWN,quote=True)  
                except:
                  pass
                #AForCopy = await message.reply_audio(path,performer=song.get('artist'),title=f"{song.get('name')} - {song.get('artist')}",caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}",thumb=thumbnail,parse_mode=enums.ParseMode.MARKDOWN,quote=True)
                track_no += 1
                if LOG_GROUP:
                   await copy(PForCopy,AForCopy)
                #feedback = await message.reply_text(f"Done✅",   
                 #reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Feedback", callback_data="feed")]]))
               # shutil.rmtree(randomdir)
           
        elif item_type == "album":
            alb = client.album(album_id=item_id,)
            try:
                PForCopy = await message.reply_photo(alb['images'][0]['url'],
                caption=f"💽Album: {alb['name']}\n👥Artists: {alb['artists'][0]['name']}\n🎧Total tracks{alb['total_tracks']}\n🗂Category: {alb['album_type']}\n📆Published on: {alb['release_date']}\n\n[IMAGE]({alb['images'][0]['url']})\n{alb['uri']}")
           #     await message.reply_document(alb['images'][0]['url'])
            except Exception as e:
                pass
                err = print(e)
                PForCopy = await message.reply(f"💽Album: {alb['name']}\n👥Artists: {alb['artists'][0]['name']}\n🎧Total tracks{alb['total_tracks']}\n🗂Category: {alb['album_type']}\n📆Published on: {alb['release_date']}\n\n[IMAGE]({alb['images'][0]['url']})\n{alb['uri']}")
           # if u in PREM:
            tracks = client.album_tracks(album_id=item_id, offset=0, market=None)
          #  else:
          #       tracks = client.album_tracks(album_id=item_id, limit=30, offset=0, market=None)

            for track in alb['tracks']['items']:
                item = client.track(track_id=track['id'])
                song = await fetch_spotify_track(client,track.get('id'))
              #  cForChat = await message.reply_chat_action(enums.ChatAction.TYPING)
                sleeeps = await sleep (0.6)
                try:
                   path = await download_songs(item,randomdir)
                except Exception as e:
                    pass
## optional you can clear this or add this by using #
                    await message.reply(e)
                    await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
             #       await message.reply_text(f"try `/saavn {song.get('name')} - {song.get('artist')}`")
            #        await message.reply(f"[Click Here](https://t.me/)")
               # path = await download_songs(item,randomdir)
                thumbnail = await thumb_down(song.get('cover'),song.get('deezer_id'))
                await sleep(0.6)
                audio = EasyID3(path)
                try:
                    audio["TITLE"] = f" {song.get('name')} "
                    audio["originaldate"] = song.get('year')
            #        audio["YEAR_OF_RELEASE"] = song.get('year')
                    audio["WEBSITE"] = "https://t.me/z_downloadbot"
              #      audio["GEEK_SCORE"] = "9"
                    audio["ARTIST"] = song.get('artist')                                                                         
                    audio["ALBUM"] = song.get('album')
                    audio["DATE"] = song.get('year')
                    audio["discnumber"] =f" {item['disc_number']}"
                    audio["tracknumber"] =f" {item['track_number']}"
                    try:
                        audio["ISRC"] =f" {item['external_ids']['isrc']}"
                    except:
                        pass
                    try:
                        songGenius = genius.search_song(song('name'), song('artist'))
                        audio["LYRICS"] = (songGenius.lyrics)
                    except:
                       pass
                except:
                    pass
                audio.save()
                try:
                   audio = MP3(path, ID3=ID3)
                   audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(thumbnail,'rb').read()))
                except Exception as e:
                   pass
                   print(e)
                audio.save()
                if not path:
                           await message.reply_text(f"⚠️")
                else:
                    AForCopy = await message.reply_audio(path,performer=song.get('artist'),title=f"{song.get('name')} - {song.get('artist')}",caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}",thumb=thumbnail,parse_mode=enums.ParseMode.MARKDOWN,quote=True)
                if LOG_GROUP:
                   await copy(PForCopy,AForCopy)
           
        elif item_type == "artist":
             art = client.artist(item_id)
             try:
                 PForCopy = await message.reply_photo(art['images'][0]['url'],
                 caption=f"👤Artist: **{art['name']}­**\n❤️Followers:{art['followers']['total']}­\n🎶Generes:{art['genres']}­\n🗂Category:{art['type']}­\n❤️Popularity:{art['popularity']}­\n\n[IMAGE]({art['images'][0]['url']})\nArtist id:`{art['id']}`")
              #   await message.reply_document(art['images'][0]['url'])
             except Exception as e:
                 pass
                 await message.reply(f"👤Artist: **{art['name']}­**\n❤️Followers:{art['followers']['total']}­\n🎶Generes:{art['genres']}­\n🗂Category:{art['type']}­\n❤️Popularity:{art['popularity']}­\n\n[IMAGE]({art['images'][0]['url']})\nArtist id:`{art['id']}`")     
             
           #  if u in PREM:
          #      tracks = client.artist_albums(artist_id=item_id)
             #else:
             await message.reply(f"Sending Top 10 tracks of {art['name']}")
             tracks = client.artist_top_tracks(artist_id=item_id,)
             for item in tracks['tracks'][:10]:
                 song = await fetch_spotify_track(client,item.get('id'))
                 track = client.track(track_id=item['id'])
                 track_no = 1
                 await sleep(0.6)
                 try:
                     path = await download_songs(item,randomdir)
                 except Exception as e:
                     pass
## optional you can clear this or add this by using #
                     await message.reply(e)
                     await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
            #         await message.reply_text(f"try `/saavn {song.get('name')} - {song.get('artist')}`")
            #         await message.reply(f"[Click Here](https://t.me/)")
                 thumbnail = await thumb_down(song.get('cover'),song.get('deezer_id'))
                 audio = EasyID3(path)
                 try:
                     audio["TITLE"] = f" {song.get('name')}"
                     audio["originaldate"] = song.get('year')
              #       audio["YEAR_OF_RELEASE"] = song.get('year')
                     audio["WEBSITE"] = "https://t.me/z_downloadbot"
                #     audio["GEEK_SCORE"] = "9"
                     audio["ARTIST"] = art.get('name')                                                                            
                     audio["ALBUM"] = song.get('album')
                     audio["DATE"] = song.get('year')
                     audio["discnumber"] =f" {track['disc_number']}"
                     audio["tracknumber"] =f" {track['track_number']}"
                     try:
                         audio["ISRC"] =f" {track['external_ids']['isrc']}"
                     except:
                         pass
                     try:
                        songGenius = genius.search_song(song('name'), song('artist'))
                        audio["LYRICS"] = (songGenius.lyrics)
                     except:
                         pass
                 except:
                     pass
                 audio.save()
                 try:
                   audio = MP3(path, ID3=ID3)
                   audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(thumbnail,'rb').read()))
                 except Exception as e:
                   pass
                  # print(e)
                 audio.save()
                 AForCopy = await message.reply_audio(path,performer=f"{song.get('artist')}­",title=f"{song.get('name')} - {song.get('artist')}",caption=f"[{song.get('name')}](https://open.spotify.com/track/{song.get('deezer_id')}) | {song.get('album')} - {song.get('artist')}",thumb=thumbnail, parse_mode=enums.ParseMode.MARKDOWN,quote=True)
                 if LOG_GROUP:
                    await copy(PForCopy,AForCopy)
    except MissingSchema:
        pass
        await message.reply(LANGUAGE_STRINGS.get(user_lang, {}).get("valid_song_question","are you sure it's a valid song 🤨?"))
    except RPCError:
        pass
        await message.reply(SPOTIFY_RESPONSES.get(user_lang, {}).get(f"telegram says 500", "telegram says 500 error,so please try again later.❣️"))
    except ChatWriteForbidden:
        pass
        chat=message.chat.id
        try:
            await Mbot.leave_chat(chat)
            if BUG:
               k = await Mbot.send_message(BUG,f"{chat} {message.chat.username} or {message.from_user.id}")
               await  k.pin()
            sp = f"I have left from {chat} reason: I Am Not  Admin "
            await Mbot.send_message(message.from_user.id,f"{sp}")
        except:
            pass
    except UserIsBlocked:
        pass
        K = await  Mbot.send_message(BUG,f" private {message.chat.id}  {message.from_user.id} {message.from_user.mention}")
        k.pin()
    except IOError:
        pass
        K = await  Mbot.send_message(BUG,f" Private r: socket {message.chat.id}  {message.from_user.id} {message.from_user.mention}")
        k.pin()
    except (FileNotFoundError, OSError):
        pass
        await message.reply(SPOTIFY_RESPONSES.get(user_lang, {}).get('Unable To Procced','Sorry, We Are Unable To Procced It 🤕❣️'))
    except BrokenPipeError:
        pass
        K = await  Mbot.send_message(BUG,f" private r: broken {message.chat.id}  {message.from_user.id} {message.from_user.mention}")
    except Forbidden:
       T = await message.reply_text(SPOTIFY_RESPONSES.get(user_lang, {}).get(f"Rights Check","Dude check weather I have enough rights😎⚠️"))
    except UnboundLocalError:
       pass
  #     T = await message.reply_text(f"[{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) Track Not Found ⚠️")
        
    except FloodWait as e:
        pass
        await sleep(e.value)
        await message.reply_text(SPOTIFY_RESPONSES.get(user_lang, {}).get(f"Flood_Wait","Telegram says: [420 FLOOD_WAIT_X] - A wait of {e.value} seconds is required !"))
    except IOError as e:
        pass
        K = await  Mbot.send_message(BUG,f" private r: broken {message.chat.id} {message.from_user.mention}")
           
    except Exception as e:
        pass
        LOGGER.error(e)
        await m.edit(e)
        await Mbot.send_message(BUG,f" Finnal {e}")
      #  K = await message.reply_text(f"private [{song.get('name')} - {song.get('artist')}](https://open.spotify.com/track/{song.get('deezer_id')}) failed to send error: {e}")
     #   H = await message.reply_text(f"Done✅",   
     #        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Error Detected", callback_data="bug")]]))
    #    await message.reply_text(f"try: `/saavn {song.get('name')}`")
        await message.reply(SPOTIFY_RESPONSES.get(user_lang, {}).get('Unable To Procced','Sorry, We Are Unable To Procced It 🤕❣️'))
    finally:
        await sleep(2.0)
        try:
            rmtree(randomdir)
        except:
            pass
        try:
            await message.reply_text(
    strings['done_message'],
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=strings['feedback_button'], callback_data="feed")]])
)
            await message.reply_text(SPOTIFY_RESPONSES.get(user_lang, {}).get(f"Done", "Check out @z_downloadbot(music)  @Zpotify1(News)"))
            await m.delete()
        except:
            pass 
       # await message.reply_text(f"thumbnail and details is temp removed due to  there is  something going on telegram side:)")
           
@Mbot.on_callback_query(filters.regex(r"feed"))
async def feedback(Mbot,query):
      try:
          K = await query.message.edit(f"Feedback 🏴‍☠️",
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Press here", url="https://t.me/dailychannelsbot?start=z_downloadbot")]]))
          H = print("New Feedback")
          if BUG:
             await copy(K,H)
      except Exception as e:
          pass
         
@Mbot.on_callback_query(filters.regex(r"bug"))                                                                                                          
async def bug(_,query):
      try:                                                                                                                                  
          K = await query.message.edit(SPOTIFY_RESPONSES.get(user_lang, {}).get(f'Report','please report to the dev say "private version" with above  error occurred message'))
          await sleep(2.3)
          H = await query.message.edit(f"Bug Report 🪲",
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Report to dev ", url="https://t.me/itachi2129")]]))
          if BUG:
             await copy(K,H)
      except Exception as e:
          pass
          print(e)

@Mbot.on_callback_query(filters.regex(r"cancel"))                                                                                                          
async def bug(_,query):
          await sleep(0.2)
          await query.message.delete()
          await query.answer("closed❌")
