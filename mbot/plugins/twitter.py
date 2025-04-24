from pyrogram import filters,Client as Mbot
from mbot import BUG as  LOG_GROUP, LOG_GROUP as DUMP_GROUP
import os,re,asyncio,bs4
import requests,wget,traceback
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


TWITTER_RESPONSES = {
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
        "track_id": "Track ID",
        "INVALID_LINK": "Oops Invalid link or Media Is Not Available:)"
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
        "track_id": "شناسه آهنگ",
        "INVALID_LINK": "اوه پیوند نامعتبر یا رسانه موجود نیست:)"
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
        "track_id": "ID de pista",
        "INVALID_LINK": "¡Ups! Enlace no válido o el medio no está disponible:)"
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
        "track_id": "ID трека",
        "INVALID_LINK": "Упс, неверная ссылка или медиафайл недоступен:)"
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
        "track_id": "معرف المسار",
        "INVALID_LINK": "عفواً، الرابط غير صالح أو الوسائط غير متوفرة:)"
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
        "track_id": "ट्रैक आईडी",
        "INVALID_LINK": "ओह, अमान्य लिंक या मीडिया उपलब्ध नहीं है:)"
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
        "valid_song_question": "are you sure it's a valid song 🤨?",
        "start_download": "🎧 Downloading your request... Please wait!",
        "download_complete": "✅ Download complete! Enjoy your music.",
        "error": "❌ Sorry, an error occurred. Please try again or report this issue.",
        "banned": "🚫 You are banned from using this bot.",
        "maintenance": "🔧 The bot is under maintenance. Please try again later.",
        "invalid_link": "⚠️ Are you sure this is a valid Twitter link?",
        "track_not_found": "⚠️ Track not found. Please try another link.",
        "thumbnail_error": "⚠️ Thumbnail download is not available for this track.",
        "preview_error": "⚠️ Audio preview is not available for this track.",
        "Under": "Bot Is Under Maintenance ⚠️",
        "Done": "Check out @z_downloadbot(music)  @Zpotify1(Channel) Please support us by /donate to maintain this project.",
        "INVALID_LINK": "Oops Invalid link or Media Is Not Available:)"

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
        "valid_song_question": "آیا مطمئن هستید که آهنگ معتبری است؟ 🤨",
        "start_download": "🎧 درخواست شما در حال دانلود... لطفا منتظر بمانید!",
        "download_complete": "✅ دانلود کامل شد! از موسیقی خود لذت ببرید.",
        "error": "❌ متاسفانه خطایی رخ داد. لطفا دوباره امتحان کنید یا مشکل را گزارش دهید.",
        "banned": "🚫 شما از استفاده از این ربات محروم شده‌اید.",
        "maintenance": "🔧 ربات در حال تعمیر و نگهداری است. لطفا بعدا تلاش کنید.",
        "invalid_link": "⚠️ آیا مطمئن هستید که این لینک معتبر است؟",
        "track_not_found": "⚠️ آهنگ پیدا نشد. لطفا لینک دیگری را امتحان کنید.",
        "thumbnail_error": "⚠️ دانلود تصویر برای این آهنگ امکان‌پذیر نیست.",
        "preview_error": "⚠️ پیش‌نمایش صوتی برای این آهنگ موجود نیست.",
        "Done": "Done✅",
        "INVALID_LINK": "اوه پیوند نامعتبر یا رسانه موجود نیست:) "
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
        "valid_song_question": "¿Estás segura de que es una canción válida 🤨?",
        "start_download": "🎧 Descargando tu solicitud... ¡Por favor espera!",
        "download_complete": "✅ ¡Descarga completa! Disfruta de tu música.",
        "error": "❌ Lo sentimos, ocurrió un error. Por favor, inténtalo de nuevo o informa este problema.",
        "banned": "🚫 Estás prohibido de usar este bot.",
        "maintenance": "🔧 El bot está en mantenimiento. Por favor, inténtalo de nuevo más tarde.",
        "invalid_link": "⚠️ ¿Estás seguro de que este es un enlace válido de Twitter?",
        "track_not_found": "⚠️ Canción no encontrada. Por favor, prueba con otro enlace.",
        "thumbnail_error": "⚠️ La descarga de la miniatura no está disponible para esta canción.",
        "preview_error": "⚠️ La vista previa de audio no está disponible para esta canción.",
        "Under": "El bot está en mantenimiento ⚠️",
        "Done": "Mira @z_downloadbot (música) y @Zpotify1 (canal). Por favor, apóyanos con /donate para mantener este proyecto.",
        "INVALID_LINK": "¡Ups! Enlace inválido o el medio no está disponible :)"

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
        "valid_song_question": "вы уверены, что это допустимая песня 🤨?",
        "start_download": "🎧 Ваш запрос загружается... Пожалуйста, подождите!",
        "download_complete": "✅ Загрузка завершена! Наслаждайтесь своей музыкой.",
        "error": "❌ Извините, произошла ошибка. Пожалуйста, попробуйте снова или сообщите об этой проблеме.",
        "banned": "🚫 Вам запрещено использовать этого бота.",
        "maintenance": "🔧 Бот находится на техническом обслуживании. Пожалуйста, попробуйте позже.",
        "invalid_link": "⚠️ Вы уверены, что это действительная ссылка на Twitter?",
        "track_not_found": "⚠️ Трек не найден. Пожалуйста, попробуйте другую ссылку.",
        "thumbnail_error": "⚠️ Загрузка миниатюры для этого трека недоступна.",
        "preview_error": "⚠️ Аудиопревью для этого трека недоступно.",
        "Under": "Бот на техническом обслуживании ⚠️",
        "Done": "Проверьте @z_downloadbot (музыка) и @Zpotify1 (канал). Пожалуйста, поддержите нас через /donate, чтобы поддерживать этот проект.",
        "INVALID_LINK": "Упс! Неверная ссылка или медиа недоступно :)"
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
        "valid_song_question": "هل أنت متأكد من أن هذه أغنية صالحة 🤨؟",
        "start_download": "🎧 جارٍ تنزيل طلبك... الرجاء الانتظار!",
        "download_complete": "✅ اكتمل التنزيل! استمتع بموسيقاك.",
        "error": "❌ عذرًا، حدث خطأ. يرجى المحاولة مرة أخرى أو الإبلاغ عن هذه المشكلة.",
        "banned": "🚫 أنت محظور من استخدام هذا البوت.",
        "maintenance": "🔧 البوت قيد الصيانة. يرجى المحاولة مرة أخرى لاحقًا.",
        "invalid_link": "⚠️ هل أنت متأكد أن هذا رابط تويتر صالح؟",
        "track_not_found": "⚠️ لم يتم العثور على المقطع. يرجى تجربة رابط آخر.",
        "thumbnail_error": "⚠️ تنزيل الصورة المصغرة غير متاح لهذا المقطع.",
        "preview_error": "⚠️ معاينة الصوت غير متاحة لهذا المقطع.",
        "Under": "البوت قيد الصيانة ⚠️",
        "Done": "تحقق من @z_downloadbot (موسيقى) و @Zpotify1 (قناة). يرجى دعمنا عبر /donate للحفاظ على هذا المشروع.",
        "INVALID_LINK": "عذرًا! الرابط غير صالح أو الوسائط غير متوفرة :)"
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
        "valid_song_question": "क्या आप सुनिश्चित हैं कि यह एक वैध गीत है 🤨?",
        "start_download": "🎧 आपका अनुरोध डाउनलोड किया जा रहा है... कृपया प्रतीक्षा करें!",
        "download_complete": "✅ डाउनलोड पूरा हो गया! अपने संगीत का आनंद लें।",
        "error": "❌ क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें या इस समस्या की रिपोर्ट करें।",
        "banned": "🚫 आपको इस बॉट का उपयोग करने से प्रतिबंधित किया गया है।",
        "maintenance": "🔧 बॉट रखरखाव के अधीन है। कृपया बाद में पुनः प्रयास करें।",
        "invalid_link": "⚠️ क्या आप सुनिश्चित हैं कि यह एक वैध ट्विटर लिंक है?",
        "track_not_found": "⚠️ ट्रैक नहीं मिला। कृपया कोई अन्य लिंक आज़माएं।",
        "thumbnail_error": "⚠️ इस ट्रैक के लिए थंबनेल डाउनलोड उपलब्ध नहीं है।",
        "preview_error": "⚠️ इस ट्रैक के लिए ऑडियो पूर्वावलोकन उपलब्ध नहीं है।",
        "Under": "बॉट रखरखाव के अधीन है ⚠️",
        "Done": "@z_downloadbot (संगीत) और @Zpotify1 (चैनल) देखें। कृपया इस प्रोजेक्ट को बनाए रखने के लिए /donate के माध्यम से हमारा समर्थन करें।",
        "INVALID_LINK": "उफ़! अमान्य लिंक या मीडिया उपलब्ध नहीं है :)"
    }
}

@Mbot.on_message(filters.regex(r'https?://.*twitter[^\s]+') & filters.incoming | filters.regex(r'https?://(?:www\.)?x\.com/\S+') & filters.incoming,group=-5)
async def twitter_handler(Mbot, message):
    
   user_lang = get_user_language(message.from_user.id)  # Fetch user language from your function
   strings = LANGUAGE_STRINGS.get(user_lang, LANGUAGE_STRINGS["en"])  # Default to English if not found

   if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text(TWITTER_RESPONSES.get(user_lang, {}).get("maintenance","🔧 The bot is under maintenance. Please try again later."))
        return
   
   # Check Banned Users
   if message.from_user.id in banned_users:
        await message.reply_text(TWITTER_RESPONSES.get(user_lang, {}).get("banned","You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
        return

   try:            
      link=message.matches[0].group(0)
      if "x.com" in link:
         link=link.replace("x.com","fxtwitter.com")
      elif "twitter.com" in link:
         link = link.replace("twitter.com","fxtwitter.com")
      m=await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
      try:
            dump_file = await message.reply_video(link, caption=strings["start_download"])
      except Exception as e:
          print(e)
          try:
             snd_message=await message.reply(link)
             await asyncio.sleep(1)
             dump_file = await message.reply_video(link,caption="Thank you for using - @z_downloadbot")
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
                 dump_file = await message.reply_video(content_value, caption=strings["start_download"])
              except Exception as e:
                  print(e)
                  try:
                     snd_msg=await message.reply(content_value)
                     await asyncio.sleep(1)
                     await message.reply_video(content_value, caption=strings["start_download"])
                     await snd_msg.delete()
                  except Exception as e:
                      print(e)
                      await message.reply(strings["INVALID_LINK"])
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
       await message.reply(strings["Done"])
                  
    
