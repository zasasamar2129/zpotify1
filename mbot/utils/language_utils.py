import json
import os
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
from pyrogram import filters
from pyrogram.raw.functions import Ping
from mbot import LOG_GROUP, OWNER_ID, SUDO_USERS, Mbot, AUTH_CHATS
from os import execvp, sys
import os
import spotipy
import psutil
from asyncio import sleep
import json
from mbot.utils.util import save_maintenance_status
# File to store user language preferences
USER_LANGUAGES_FILE = "user_languages.json"

# Dictionary to map language codes to their display names
LANGUAGES = {
    "en": "English",
    "fa": "فارسی",
    "es": "Españolah",
    "ru": "Русский",
    "ar": "عربی",
    "hi": "हिन्दी"
}

# Load user language preferences
def load_user_languages():
    if os.path.exists(USER_LANGUAGES_FILE):
        with open(USER_LANGUAGES_FILE, "r") as f:
            return json.load(f)
    return {}

# Save user language preferences
def save_user_languages(user_languages):
    with open(USER_LANGUAGES_FILE, "w") as f:
        json.dump(user_languages, f)

# Get the user's language preference
def get_user_language(user_id):
    user_languages = load_user_languages()
    return user_languages.get(str(user_id), "en")  # Default to English if no preference is set

# Function to send the main start message in the selected language
async def send_main_start_message(client, message, lang_code):
    # Define the main start message based on the selected language
    start_messages = {
        "en": f"👋 Hello {message.from_user.first_name}, I'm 𝓩𝓟𝓞𝓣𝓘𝓕𝓨, a music downloader bot that supports downloading from YouTube, Spotify, SoundCloud, Deezer, and more.",
        "fa": f"👋 سلام {message.from_user.first_name}, من 𝓩𝓟𝓞𝓣𝓘𝓕𝓨 هستم، یک ربات دانلود موزیک که از YouTube, Spotify, SoundCloud, Deezer و بیشتر پشتیبانی می‌کند.",
        "es": f"👋 Hola {message.from_user.first_name}, soy 𝓩𝓟𝓞𝓣𝓘𝓕𝓨, un bot de descarga de música que admite descargas de YouTube, Spotify, SoundCloud, Deezer y más.",
        "ru": f"👋 Привет {message.from_user.first_name}, я 𝓩𝓟𝓞𝓣𝓘𝓕𝓨, бот для загрузки музыки, который поддерживает загрузку с YouTube, Spotify, SoundCloud, Deezer и других.",
        "ar": f"👋 مرحبًا {message.from_user.first_name}, أنا 𝓩𝓟𝓞𝓣𝓘𝓕𝓨, بوت لتنزيل الموسيقى يدعم التنزيل من YouTube, Spotify, SoundCloud, Deezer والمزيد.",
        "hi": f"👋 नमस्ते {message.from_user.first_name}, मैं 𝓩𝓟𝓞𝓣𝓘𝓕𝓨 हूँ, एक संगीत डाउनलोड बॉट जो YouTube, Spotify, SoundCloud, Deezer और अन्य से डाउनलोड का समर्थन करता है।"
    }

    # Define the reply markup (buttons)
    reply_markup = [
        [
            InlineKeyboardButton(
                text="🌐 Bot Channel", url="https://t.me/Zpotify1"),
            InlineKeyboardButton(
                text="⛓️‍💥 Repo",
                url="https://github.com/zasasamar2129/zpotify1"),
            InlineKeyboardButton(text="❓Help", callback_data="helphome")
        ],
        [
            InlineKeyboardButton(
                text="💖 Donate", url="https://www.buymeacoffee.com/zasasamar"),
        ],
        [
            InlineKeyboardButton(
                text="📢 Support", url="https://t.me/itachi2129"),
        ],
    ]

    if LOG_GROUP:
        invite_link = await client.create_chat_invite_link(chat_id=(int(LOG_GROUP) if str(LOG_GROUP).startswith("-100") else LOG_GROUP))
        reply_markup.append([InlineKeyboardButton("🗃️ LOG Channel", url=invite_link.invite_link)])

    # Send the main start message
    await message.reply_text(
        start_messages.get(lang_code, start_messages["en"]),  # Default to English if the language is not found
        reply_markup=InlineKeyboardMarkup(reply_markup)
    )

##############################################DICTIONARY#####################################################

    YT_RESPONSES = {
    "en": {
        "start_download": "🎧 Downloading your request... Please wait!",
        "download_complete": "✅ Download complete! Enjoy your music.",
        "error": "❌ Sorry, an error occurred. Please try again or report this issue.",
        "banned": "🚫 You are banned from using this bot.",
        "maintenance": "🔧 The bot is under maintenance. Please try again later.",
        "unable_to_find": "400: Sorry, Unable To Find It. Try another or report it to @itachi2129 or support chat @spotify_supportbot 🤖",
        "support_message": "Check out @z_downloadbot (music) @zpotify1 (Channel) \n Please Support Us By /donate To Maintain This Project",
    },
    "fa": {
        "start_download": "🎧 درخواست شما در حال دانلود... لطفا منتظر بمانید!",
        "download_complete": "✅ دانلود کامل شد! از موسیقی خود لذت ببرید.",
        "error": "❌ متاسفانه خطایی رخ داد. لطفا دوباره امتحان کنید یا مشکل را گزارش دهید.",
        "banned": "🚫 شما از استفاده از این ربات محروم شده‌اید.",
        "maintenance": "🔧 ربات در حال تعمیر و نگهداری است. لطفا بعدا تلاش کنید.",
        "unable_to_find": "400: متأسفم، نمی توانم آن را پیدا کنم. دیگری را امتحان کنید یا آن را به @itachi2129 گزارش دهید یا از چت @spotify_supportbot 🤖 پشتیبانی کنید",
        "support_message": "بررسی کنید @z_downloadbot (موسیقی) @zpotify1 (کانال) \n لطفاً با /donate از این پروژه حمایت کنید تا به کار خود ادامه دهد",
    },
    "es": {
        "start_download": "🎧 Descargando tu solicitud... ¡Por favor espera!",
        "download_complete": "✅ ¡Descarga completa! Disfruta de tu música.",
        "error": "❌ Lo siento, ocurrió un error. Inténtalo de nuevo o informa del problema.",
        "banned": "🚫 Estás prohibido de usar este bot.",
        "maintenance": "🔧 El bot está en mantenimiento. Inténtalo más tarde.",
        "unable_to_find": "400: Lo siento, no se pudo encontrar. Inténtalo con otro o informa en @itachi2129 o en el chat de soporte @spotify_supportbot 🤖",
        "support_message": "Consulta @z_downloadbot (música) @zpotify1 (canal) \n Apóyanos con /donate para mantener este proyecto",
    },
    "ru": {
        "start_download": "🎧 Загружается ваш запрос... Пожалуйста, подождите!",
        "download_complete": "✅ Загрузка завершена! Наслаждайтесь вашей музыкой.",
        "error": "❌ Извините, произошла ошибка. Попробуйте еще раз или сообщите о проблеме.",
        "banned": "🚫 Вам запрещено использовать этого бота.",
        "maintenance": "🔧 Бот на техническом обслуживании. Попробуйте позже.",
        "unable_to_find": "400: Извините, не удалось найти. Попробуйте другой или сообщите в @itachi2129 или чат поддержки @spotify_supportbot 🤖",
        "support_message": "Посмотрите @z_downloadbot (музыка) @zpotify1 (канал) \n Пожалуйста, поддержите нас через /donate, чтобы поддерживать этот проект",
    },
    "ar": {
        "start_download": "🎧 يتم تنزيل طلبك... يرجى الانتظار!",
        "download_complete": "✅ تم اكتمال التنزيل! استمتع بموسيقاك.",
        "error": "❌ عذرًا، حدث خطأ. يرجى المحاولة مرة أخرى أو الإبلاغ عن المشكلة.",
        "banned": "🚫 أنت محظور من استخدام هذا البوت.",
        "maintenance": "🔧 البوت تحت الصيانة. يرجى المحاولة لاحقًا.",
        "unable_to_find": "400: عذرًا، لم أتمكن من العثور عليه. حاول تجربة آخر أو أبلغ عنه إلى @itachi2129 أو دعم الدردشة @spotify_supportbot 🤖",
        "support_message": "تحقق من @z_downloadbot (الموسيقى) @zpotify1 (القناة) \n يرجى دعمنا عن طريق /donate للحفاظ على هذا المشروع",
    },
    "hi": {
        "start_download": "🎧 आपका अनुरोध डाउनलोड हो रहा है... कृपया प्रतीक्षा करें!",
        "download_complete": "✅ डाउनलोड पूरा हुआ! अपने संगीत का आनंद लें।",
        "error": "❌ क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें या इस समस्या की रिपोर्ट करें।",
        "banned": "🚫 आपको इस बॉट के उपयोग से प्रतिबंधित किया गया है।",
        "maintenance": "🔧 बॉट का रखरखाव किया जा रहा है। कृपया बाद में प्रयास करें।",
        "unable_to_find": "400: क्षमा करें, इसे खोज नहीं सका। किसी अन्य को आज़माएं या इसे @itachi2129 या समर्थन चैट @spotify_supportbot 🤖 को रिपोर्ट करें।",
        "support_message": "@z_downloadbot (संगीत) @zpotify1 (चैनल) देखें \n कृपया इस प्रोजेक्ट को बनाए रखने के लिए /donate के माध्यम से हमारा समर्थन करें",
    },
}

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
        'Unable To Procced':'Sorry, We Are Unable To Procced It 🤕❣️',
        "Flood_Wait": "Telegram says: [420 FLOOD_WAIT_X] - A wait of {e.value} seconds is required !",
        "Done": "Check out @z_downloadbot(music)  @Zpotify1(News)",
        'Report':'please report to the dev say "private version" with above  error occurred message',
        "Rights Check":"Dude check weather I have enough rights😎⚠️",
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
        "done_message": "Done✅",
        "feedback_button": "Feedback",
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