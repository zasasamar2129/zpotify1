from pyrogram import filters, Client as Mbot
from os import mkdir,environ 
from random import randint
from mbot import BUG as  LOG_GROUP , LOG_GROUP as DUMP_GROUP
from pyrogram import filters
from shutil import rmtree 
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL
from requests import get
import traceback,os
from mbot.utils.util import is_maintenance_mode
from mbot import LOG_GROUP, OWNER_ID, SUDO_USERS, Mbot, AUTH_CHATS
import json
from mbot.utils.language_utils import get_user_language

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

FIXIE_SOCKS_HOST= environ.get('FIXIE_SOCKS_HOST')
async def thumb_down(videoId):
    with open(f"/tmp/{videoId}.jpg","wb") as file:
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
 #       "proxy": f"socks5://{FIXIE_SOCKS_HOST}",
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

async def ytdl_down(path,video_url,id):
#    pool = multiprocessing.Pool(processes=8)
    print(video_url)
    qa="mp3"
    query = f"{video_url[3]} - {video_url[2]}".replace(":", "").replace("\"", "")
    file = f"{path}/{query}"
#    arts=",".join(ur['name'] for ur in item['artists'][0:2])
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
            video = ydl.extract_info(video_url,download=True)
           # info = ydl.extract_info(video)
        #    filename = ydl.prepare_filename(video)
            return f"{file}.{qa}"
        except (IOError,BrokenPipeError):
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
                    video = ydl.extract_info(video_url,download=True)
                    return f"{file}.{qa}"
            except Exception as e:
                print(e)
async def getIds(video):
    ids = []
    with YoutubeDL({'quiet':True}) as ydl:
        info_dict = ydl.extract_info(video, download=False)
        try:
            info_dict = info_dict['entries']
            ids.extend([x.get('id'),x.get('playlist_index'),x.get('creator') or x.get('uploader'),x.get('title'),x.get('duration'),x.get('thumbnail')] for x in info_dict)
        except:
            ids.append([info_dict.get('id'),info_dict.get('playlist_index'),info_dict.get('creator') or info_dict.get('uploader'),info_dict.get('title'),info_dict.get('duration'),info_dict.get('thumbnail')])
    return ids
@Mbot.on_message(filters.regex(r'https?://.*youtube[^\s]+') & filters.incoming|filters.regex(r'(https?:\/\/(?:www\.)?youtu\.?be(?:\.com)?\/.*)') & filters.incoming)
async def _(Mbot,message):

    user_lang = get_user_language(message.from_user.id)
    YT_RESPONSES = {
    
  "en": {
    "start_download": "🎧 Downloading your request... Please wait!",
    "download_complete": "✅ Download complete! Enjoy your music.",
    "error": "❌ Sorry, an error occurred. Please try again or report this issue.",
    "banned": "🚫 You are banned from using this bot.",
    "maintenance": "🔧 The bot is under maintenance. Please try again later.",
    "unable_to_find": "400: Sorry, Unable To Find It. Try another or report it to @itachi2129 or support chat @spotify_supportbot 🤖",
    "support_message": "Check out @z_downloadbot (music) @zpotify1 (Channel) \n Please Support Us By /donate To Maintain This Project",
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
    "valid_song_question": "Are you sure it's a valid song? 🤨",
    "photo_caption": "🎧 Title: {title}\n🎤 Artist: {artist}\n💽 Track No: {track_no}\n💽 Total Tracks: {total_tracks}",
    "audio_caption": "[{title}](https://youtu.be/{video_id}) - {artist} Thank you for using - @z_downloadbot"

  },
  "fa": {
    "start_download": "🎧 درخواست شما در حال دانلود... لطفا منتظر بمانید!",
    "download_complete": "✅ دانلود کامل شد! از موسیقی خود لذت ببرید.",
    "error": "❌ متاسفانه خطایی رخ داد. لطفا دوباره امتحان کنید یا مشکل را گزارش دهید.",
    "banned": "🚫 شما از استفاده از این ربات محروم شده‌اید.",
    "maintenance": "🔧 ربات در حال تعمیر و نگهداری است. لطفا بعدا تلاش کنید.",
    "unable_to_find": "400: متأسفم، نمی توانم آن را پیدا کنم. دیگری را امتحان کنید یا آن را به @itachi2129 گزارش دهید یا از چت @spotify_supportbot 🤖 پشتیبانی کنید",
    "support_message": "بررسی کنید @z_downloadbot (موسیقی) @zpotify1 (کانال) \n لطفاً با /donate از این پروژه حمایت کنید تا به کار خود ادامه دهد",
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
    "photo_caption": "🎧 عنوان: {title}\n🎤 هنرمند: {artist}\n💽 شماره ترک: {track_no}\n💽 تعداد کل ترک‌ها: {total_tracks}",
    "audio_caption": "[{title}](https://youtu.be/{video_id}) - {artist} با تشکر از استفاده شما - @z_downloadbot"

  },
  "es": {
    "start_download": "🎧 Descargando tu solicitud... ¡Por favor espera!",
    "download_complete": "✅ ¡Descarga completa! Disfruta de tu música.",
    "error": "❌ Lo siento, ocurrió un error. Inténtalo de nuevo o informa del problema.",
    "banned": "🚫 Estás prohibido de usar este bot.",
    "maintenance": "🔧 El bot está en mantenimiento. Inténtalo más tarde.",
    "unable_to_find": "400: Lo siento, no se pudo encontrar. Inténtalo con otro o informa en @itachi2129 o en el chat de soporte @spotify_supportbot 🤖",
    "support_message": "Consulta @z_downloadbot (música) @zpotify1 (canal) \n Apóyanos con /donate para mantener este proyecto",
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
    "valid_song_question": "¿Estás segura de que es una canción válida? 🤨",
    "photo_caption": "🎧 Título: {title}\n🎤 Artista: {artist}\n💽 Número de pista: {track_no}\n💽 Total de pistas: {total_tracks}",
    "audio_caption": "[{title}](https://youtu.be/{video_id}) - {artist} Gracias por usar - @z_downloadbot"

  },
  "ru": {
    "start_download": "🎧 Загружается ваш запрос... Пожалуйста, подождите!",
    "download_complete": "✅ Загрузка завершена! Наслаждайтесь вашей музыкой.",
    "error": "❌ Извините, произошла ошибка. Попробуйте еще раз или сообщите о проблеме.",
    "banned": "🚫 Вам запрещено использовать этого бота.",
    "maintenance": "🔧 Бот на техническом обслуживании. Попробуйте позже.",
    "unable_to_find": "400: Извините, не удалось найти. Попробуйте другой или сообщите в @itachi2129 или чат поддержки @spotify_supportbot 🤖",
    "support_message": "Посмотрите @z_downloadbot (музыка) @zpotify1 (канал) \n Пожалуйста, поддержите нас через /donate, чтобы поддерживать этот проект",
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
    "valid_playlist_question": "Вы уверены, что это действительный плейлист? 🤨",
    "valid_song_question": "Вы уверены, что это действительная песня? 🤨",
    "photo_caption": "🎧 Название: {title}\n🎤 Исполнитель: {artist}\n💽 Номер трека: {track_no}\n💽 Всего треков: {total_tracks}",
    "audio_caption": "[{title}](https://youtu.be/{video_id}) - {artist} Спасибо за использование - @z_downloadbot"

  },
  "ar": {
    "start_download": "🎧 يتم تنزيل طلبك... يرجى الانتظار!",
    "download_complete": "✅ تم اكتمال التنزيل! استمتع بموسيقاك.",
    "error": "❌ عذرًا، حدث خطأ. يرجى المحاولة مرة أخرى أو الإبلاغ عن المشكلة.",
    "banned": "🚫 أنت محظور من استخدام هذا البوت.",
    "maintenance": "🔧 البوت تحت الصيانة. يرجى المحاولة لاحقًا.",
    "unable_to_find": "400: عذرًا، لم أتمكن من العثور عليه. حاول تجربة آخر أو أبلغ عنه إلى @itachi2129 أو دعم الدردشة @spotify_supportbot 🤖",
    "support_message": "تحقق من @z_downloadbot (الموسيقى) @zpotify1 (القناة) \n يرجى دعمنا عن طريق /donate للحفاظ على هذا المشروع",
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
    "valid_song_question": "هل أنت متأكد من أن هذه أغنية صالحة؟ 🤨",
    "photo_caption": "🎧 العنوان: {title}\n🎤 الفنان: {artist}\n💽 رقم المسار: {track_no}\n💽 إجمالي المسارات: {total_tracks}",
    "audio_caption": "[{title}](https://youtu.be/{video_id}) - {artist} شكرًا لاستخدامك - @z_downloadbot"

  },
  "hi": {
    "start_download": "🎧 आपका अनुरोध डाउनलोड हो रहा है... कृपया प्रतीक्षा करें!",
    "download_complete": "✅ डाउनलोड पूरा हुआ! अपने संगीत का आनंद लें।",
    "error": "❌ क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें या इस समस्या की रिपोर्ट करें।",
    "banned": "🚫 आपको इस बॉट के उपयोग से प्रतिबंधित किया गया है।",
    "maintenance": "🔧 बॉट का रखरखाव किया जा रहा है। कृपया बाद में प्रयास करें।",
    "unable_to_find": "400: क्षमा करें, इसे खोज नहीं सका। किसी अन्य को आज़माएं या इसे @itachi2129 या समर्थन चैट @spotify_supportbot 🤖 को रिपोर्ट करें।",
    "support_message": "@z_downloadbot (संगीत) @zpotify1 (चैनल) देखें \n कृपया इस प्रोजेक्ट को बनाए रखने के लिए /donate के माध्यम से हमारा समर्थन करें",
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
    "valid_playlist_question": "क्या आप सुनिश्चित हैं कि यह एक वैध प्लेलिस्ट है? 🤨",
    "valid_song_question": "क्या आप सुनिश्चित हैं कि यह एक वैध गीत है? 🤨",
    "photo_caption": "🎧 शीर्षक: {title}\n🎤 कलाकार: {artist}\n💽 ट्रैक नंबर: {track_no}\n💽 कुल ट्रैक: {total_tracks}",
    "audio_caption": "[{title}](https://youtu.be/{video_id}) - {artist} उपयोग करने के लिए धन्यवाद - @z_downloadbot"

  }
}

    if is_maintenance_mode() and message.from_user.id not in SUDO_USERS:
        await message.reply_text(YT_RESPONSES.get(user_lang, {}).get("maintenance","🔧 The bot is under maintenance. Please try again later."))
        return
   
   # Check Banned Users
    if message.from_user.id in banned_users:
        await message.reply_text(YT_RESPONSES.get(user_lang, {}).get("banned","You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
        return

    try:
        m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
    except:
        pass
    link = message.matches[0].group(0)
    if "channel" in link or "/c/" in link:
        return await m.edit_text("**Channel** Download Not Available. ")
    if "shorts" in link:
        try:
            randomdir = "/tmp/"+str(randint(1,100000000))
            mkdir(randomdir)
            fileLink = await  ytdl_video(randomdir,link, message.from_user.id)
            AForCopy=await message.reply_video(fileLink)
            if os.path.exists(randomdir):
               rmtree(randomdir)
            await m.delete()
            if DUMP_GROUP:
                await AForCopy.copy(DUMP_GROUP)
        except Exception as e:
            await m.delete()
            if LOG_GROUP:
               await Mbot.send_message(LOG_GROUP,f"YouTube Shorts {e} {link}")
               await message.reply_text(YT_RESPONSES.get(user_lang, {}).get("unable_to_find",  # The correct key from the dictionary
               "400: Sorry, Unable To Find It. Try another or report it to @itachi2129 or support chat @spotify_supportbot 🤖"
    )
)
               print(traceback.format_exc())
               await Mbot.send_message(LOG_GROUP, traceback.format_exc())
               
        return await message.reply_text(
    YT_RESPONSES.get(user_lang, {}).get(
        "support_message",
        "Check out @z_downloadbot (music) @zpotify1 (Channel) \n Please Support Us By /donate To Maintain This Project"
    )
)
    try:
        ids = await getIds(message.matches[0].group(0))
        videoInPlaylist = len(ids)
        randomdir = "/tmp/"+str(randint(1,100000000))
        mkdir(randomdir)
        for id in ids:
  #          await message.reply(id)
  #          await message.reply(id[2])
            PForCopy = await message.reply_photo(
    f"https://i.ytimg.com/vi/{id[0]}/hqdefault.jpg",
    caption=YT_RESPONSES.get(user_lang, {}).get("photo_caption", "").format(
    title=id[3], artist=id[2], track_no=id[1], total_tracks=videoInPlaylist
)
            )

            fileLink = await ytdl_down(randomdir, id, message.from_user.id)
            print("down completely")
            thumbnail = await thumb_down(id[0])

            AForCopy = await message.reply_audio(
    fileLink,
    caption=YT_RESPONSES.get(user_lang, {}).get("audio_caption", "").format(
    title=id[3], video_id=id[0], artist=id[2]
)
,
    title=id[3].replace("_", " "),
    performer=id[2],
    thumb=thumbnail,
    duration=id[4]
)

            if DUMP_GROUP:
                await PForCopy.copy(DUMP_GROUP)
                await AForCopy.copy(DUMP_GROUP)
        await m.delete()
        if os.path.exists(randomdir):
           rmtree(randomdir)
        
    except Exception as e:
        print(e)
        if LOG_GROUP:
               await Mbot.send_message(LOG_GROUP,f"Youtube {e} {link}")
               await message.reply_text(
    YT_RESPONSES.get(user_lang, {}).get(
        "unable_to_find",
        "400: Sorry, Unable To Find It. Try another or report it to @itachi2129 or support chat @spotify_supportbot 🤖"
    )
)
               await Mbot.send_message(LOG_GROUP, traceback.format_exc())
