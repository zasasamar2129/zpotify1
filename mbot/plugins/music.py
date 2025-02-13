from random import randint 
from yt_dlp import YoutubeDL
from requests import get
import os
from asgiref.sync import sync_to_async
from pyrogram import filters,enums
from mbot import Mbot
from random import randint
import shutil
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

async def download_songs(query, download_directory='.'):
    query = f"{query} Lyrics".replace(":", "").replace("\"", "")
    ydl_opts = {
        'format': "bestaudio/best",
        'default_search': 'ytsearch',
        'noplaylist': True,
        "nocheckcertificate": True,
        "outtmpl": f"{download_directory}/%(title)s.mp3",
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,

        "nocheckcertificate": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            video = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]['id']
            info = ydl.extract_info(video)
            filename = ydl.prepare_filename(info)
            if not filename:
               print(f"Track Not Found⚠️")
            else:
                path_link = filename
                return path_link
        except Exception as e:
            pass
            print(e)
    return video 

@Mbot.on_message(
    filters.command('song') 
    & filters.text & filters.incoming
)
async def song(_, message):

      user_lang = get_user_language(message.from_user.id)  # Fetch user language from your function
       # Default to English if not found

      MUSIC_RESPONSES = {
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
        "track_id": "Track ID",
        "Shazaming": "Shazaming",
        "Reply_Song": "`Reply To Song File`",
        "Reply_Audio": "`Reply To Audio File.`",
        "Convert_Song": "`Unable To Convert To Song File. Is This A Valid File?`",
        "No_Result": "`No Results Found.`",
        "Saavn_Argument": "/saavn requires an argument.",
        "Downloading": "Downloading...",
        "Uploading": "Uploading...",
        "unable_to_proceed": "503: Sorry, We Are Unable To Proceed It 🤕❣️",
        "unlocked_message": "Congratulations You Had Unlocked Go Ahead 🤝 Keep The Bond With Us❣️",
        "unlocked": "Congratulations You Are Unlocked 🤝",
        "join_channel": "Please Join The Channel"
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
        "track_id": "شناسه آهنگ",
        "Shazaming": "در حال شناسایی آهنگ",
        "Reply_Song": "`به فایل آهنگ پاسخ دهید`",
        "Reply_Audio": "`به فایل صوتی پاسخ دهید.`",
        "Convert_Song": "`تبدیل به فایل آهنگ امکان‌پذیر نیست. آیا این یک فایل معتبر است؟`",
        "No_Result": "`نتیجه‌ای یافت نشد.`",
        "Saavn_Argument": "/saavn نیاز به یک آرگومان دارد.",
        "Downloading": "در حال دانلود...",
        "Uploading": "در حال آپلود...",
        "unable_to_proceed": "۵۰۳: متأسفیم، امکان پردازش وجود ندارد 🤕❣️",
        "unlocked_message": "تبریک! شما دسترسی پیدا کردید، ادامه دهید 🤝 ارتباط خود را با ما حفظ کنید❣️",
        "unlocked": "تبریک! شما دسترسی پیدا کردید 🤝",
        "join_channel": "لطفاً به کانال بپیوندید"
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
        "track_id": "ID de pista",
        "Shazaming": "Identificando canción",
        "Reply_Song": "`Responder al archivo de canción`",
        "Reply_Audio": "`Responder al archivo de audio.`",
        "Convert_Song": "`No se puede convertir a archivo de canción. ¿Es este un archivo válido?`",
        "No_Result": "`No se encontraron resultados.`",
        "Saavn_Argument": "/saavn requiere un argumento.",
        "Downloading": "Descargando...",
        "Uploading": "Subiendo...",
        "unable_to_proceed": "503: Lo sentimos, no podemos procesarlo 🤕❣️",
        "unlocked_message": "¡Felicidades! Has desbloqueado, adelante 🤝 Mantén el vínculo con nosotros❣️",
        "unlocked": "¡Felicidades! Estás desbloqueado 🤝",
        "join_channel": "Por favor, únete al canal"
        
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
        "track_id": "ID трека",
        "Shazaming": "Идентификация песни",
        "Reply_Song": "`Ответить на файл песни`",
        "Reply_Audio": "`Ответить на аудиофайл.`",
        "Convert_Song": "`Невозможно преобразовать в файл песни. Это действительный файл?`",
        "No_Result": "`Результаты не найдены.`",
        "Shazaming": "Identificando canción",
        "Reply_Song": "`Responder al archivo de canción`",
        "Reply_Audio": "`Responder al archivo de audio.`",
        "Convert_Song": "`No se puede convertir a archivo de canción. ¿Es este un archivo válido?`",
        "No_Result": "`No se encontraron resultados.`",
        "Saavn_Argument": "/saavn требует аргумента.",
        "Downloading": "Загрузка...",
        "Uploading": "Загрузка...",
        "unable_to_proceed": "503: Извините, мы не можем обработать запрос 🤕❣️",
        "unlocked_message": "Поздравляем! Доступ разблокирован, продолжайте 🤝 Оставайтесь с нами❣️",
        "unlocked": "Поздравляем! Вы разблокированы 🤝",
        "join_channel": "Пожалуйста, присоединяйтесь к каналу"
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
        "track_id": "معرف المسار",
        "Shazaming": "جاري التعرف على الأغنية",
        "Reply_Song": "`الرد على ملف الأغنية`",
        "Reply_Audio": "`الرد على ملف الصوت.`",
        "Convert_Song": "`تعذر التحويل إلى ملف أغنية. هل هذا ملف صالح؟`",
        "No_Result": "`لم يتم العثور على نتائج.`",
        "Saavn_Argument": "/saavn يتطلب وسيطًا.",
        "Downloading": "جارٍ التحميل...",
        "Uploading": "جارٍ التحميل...",
        "unable_to_proceed": "٥٠٣: عذرًا، لا يمكننا إتمام العملية 🤕❣️",
        "unlocked_message": "تهانينا! لقد تم فك القفل، استمر 🤝 حافظ على التواصل معنا❣️",
        "unlocked": "تهانينا! لقد تم فك القفل 🤝",
        "join_channel": "يرجى الانضمام إلى القناة"
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
        "track_id": "ट्रैक आईडी",
        "Shazaming": "गाना पहचाना जा रहा है",
        "Reply_Song": "`गाने की फ़ाइल का जवाब दें`",
        "Reply_Audio": "`ऑडियो फ़ाइल का जवाब दें।`",
        "Convert_Song": "`गाने की फ़ाइल में बदलने में असमर्थ। क्या यह एक वैध फ़ाइल है?`",
        "No_Result": "`कोई परिणाम नहीं मिला।`",
        "Saavn_Argument": "/saavn के लिए एक आर्ग्युमेंट की आवश्यकता है।",
        "Downloading": "डाउनलोड हो रहा है...",
        "Uploading": "अपलोड हो रहा है...",
        "unable_to_proceed": "503: क्षमा करें, हम इसे संसाधित नहीं कर सकते 🤕❣️",
        "unlocked_message": "बधाई हो! आपने अनलॉक कर लिया है, आगे बढ़ें 🤝 हमारे साथ जुड़े रहें❣️",
        "unlocked": "बधाई हो! आप अनलॉक हो गए हैं 🤝",
        "join_channel": "कृपया चैनल से जुड़ें"
    },
}

      if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text(MUSIC_RESPONSES.get(user_lang, {}).get("maintenance","🔧 The bot is under maintenance. Please try again later."))
        return
      
        # Check Banned Users
      if message.from_user.id in banned_users:
        await message.reply_text(MUSIC_RESPONSES.get(user_lang, {}).get("banned","You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
        return
        
      try:
          await message.reply_chat_action(enums.ChatAction.TYPING)
          k = await message.reply("⌛")
          print ('⌛')
          try:
              randomdir = f"/tmp/{str(randint(1,100000000))}"
              os.mkdir(randomdir)
          except Exception as e:
              await message.reply_text(MUSIC_RESPONSES.get(user_lang, {}).get(f"Failed to send song retry after sometime 😥 reason: {e} "))
              return await k.delete()
          query = message.text.split(None, 1)[1]
          await k.edit(MUSIC_RESPONSES.get(user_lang, {}).get("Downloading", "downloading"))
          print(MUSIC_RESPONSES.get(user_lang, {}).get("Downloading",'downloading'))
          await message.reply_chat_action(enums.ChatAction.RECORD_AUDIO)
          path = await download_songs(query,randomdir)
          await message.reply_chat_action(enums.ChatAction.UPLOAD_AUDIO)
          await k.edit(MUSIC_RESPONSES.get(user_lang, {}).get("Uploading", 'Uploading...'))
          await message.reply_audio(path)
      
      except IndexError:
          await message.reply(MUSIC_RESPONSES.get(user_lang, {}).get("Song_Argument", "song requies an argument `eg /song faded`"))
          return  await k.delete()
      except Exception as e:
          await message.reply_text(MUSIC_RESPONSES.get(user_lang, {}).get(f"Failed_Song", "Failed to send song 😥 reason: {e}"))
      finally:
          try:
              shutil.rmtree(randomdir)
              await message.reply_text(MUSIC_RESPONSES.get(user_lang, {}).get(f"Done", "Check out @z_downloadbot(music)  @Zpotify1(News)"))
              return await k.delete() 
          except:
              pass
