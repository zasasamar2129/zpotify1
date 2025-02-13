from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.raw.functions import Ping
from mbot import LOG_GROUP, OWNER_ID, SUDO_USERS, Mbot, AUTH_CHATS
from os import execvp, sys
import os
import spotipy
import psutil
from asyncio import sleep
import json
from mbot.utils.util import save_maintenance_status
from mbot.utils.language_utils import get_user_language
import asyncio
from pyrogram.types import BotCommand

MAINTENANCE_FILE = "maintenance_status.json"
BAN_LIST_FILE = "banned_users.json"
USER_LIST_FILE = "user_list.json"


# File to store user language preferences
USER_LANGUAGES_FILE = "user_languages.json"

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

# Dictionary to map language codes to their display names
LANGUAGES = {
    "en": "English",
    "fa": "Persian",
    "es": "Spanish",
    "ru": "Russian",
    "ar": "Arabic",
    "hi": "Hindi"
}



# Load user list from file
def load_user_list():
    if os.path.exists(USER_LIST_FILE):
        with open(USER_LIST_FILE, "r") as f:
            return set(json.load(f))
    return set()

# Save user list to file
def save_user_list(user_list):
    with open(USER_LIST_FILE, "w") as f:
        json.dump(list(user_list), f)

# List to store users
user_list = load_user_list()

################################MAINTENANCE##################################
# Load maintenance status
def load_maintenance_status():
    if os.path.exists(MAINTENANCE_FILE):
        with open(MAINTENANCE_FILE, "r") as f:
            return json.load(f).get("maintenance", False)
    return False

# Save maintenance status
def save_maintenance_status(status):
    with open(MAINTENANCE_FILE, "w") as f:
        json.dump({"maintenance": status}, f)

# Global maintenance mode variable
maintenance_mode = load_maintenance_status()

# Command to toggle maintenance mode using inline buttons
@Mbot.on_message(filters.command("maintenance") & filters.user(SUDO_USERS))
async def maintenance_control(client, message):
    await message.delete()

    # Create inline buttons for enabling/disabling maintenance mode
    keyboard = [
        [
            InlineKeyboardButton("⚠️ Enable Maintenance", callback_data="maintenance_on"),
            InlineKeyboardButton("🟢 Disable Maintenance", callback_data="maintenance_off"),
        ],
        [
            InlineKeyboardButton("🚧 Check Maintenance Status", callback_data="maintenance_status")
        ],
        [   
            InlineKeyboardButton(text="❌", callback_data="close")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("🛠️ Please choose an option to enable/disable maintenance mode or check the current status:", reply_markup=reply_markup)

# Handle callback queries for maintenance toggle and status check
@Mbot.on_callback_query(filters.regex(r"maintenance_(on|off|status)"))
async def handle_maintenance_toggle(client, callback_query):
    action = callback_query.data.split("_")[1]  # Extract "on", "off", or "status"
    
    if action == "on":
        save_maintenance_status(True)
        await callback_query.answer("👨🏻‍🔧 Maintenance mode has been enabled.", show_alert=True)
        await callback_query.message.edit_text("👨🏻‍🔧 Maintenance mode has been enabled. Bot will not respond to user requests")
        await callback_query.message.delete()

    elif action == "off":
        save_maintenance_status(False)
        await callback_query.answer("➤ Maintenance mode has been disabled.", show_alert=True)
        await callback_query.message.edit_text("Maintenance mode has been disabled. Bot is now operational 🟢")
        await callback_query.message.delete()

    elif action == "status":
        status = "ON" if load_maintenance_status() else "OFF"
        await callback_query.answer(f"🚧 Maintenance mode is currently: **{status}**", show_alert=True)
        await callback_query.message.delete()

# Helper function to check maintenance mode
def maintenance_check(handler):
    async def wrapper(client, message):
        # Load the latest maintenance status
        global maintenance_mode
        maintenance_mode = load_maintenance_status()
        
        if maintenance_mode and message.from_user.id not in SUDO_USERS:
            await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("maintenance","🔧 The bot is under maintenance. Please try again later."))
            return
        await handler(client, message)
    return wrapper

#################################MAINTENANCE##################################


#####################################BAN######################################


# Load banned users from file
def load_banned_users():
    if os.path.exists(BAN_LIST_FILE):
        with open(BAN_LIST_FILE, "r") as f:
            return set(json.load(f))
    return set()

# Save banned users to file
def save_banned_users(banned_users):
    with open(BAN_LIST_FILE, "w") as f:
        json.dump(list(banned_users), f)
        
# List to store banned users
banned_users = load_banned_users()

# Command to ban a user
@Mbot.on_message(filters.command("ban") & filters.user(SUDO_USERS))
async def ban_user(client, message):
    await message.delete()
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 2:
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("⛔ Invalid user ID. Please provide a numeric user ID.")
            return
    else:
        await message.reply_text("ℹ️ Usage: /ban <user_id> or reply to a user's message with /ban")
        return

    # Add the user to the ban list
    banned_users.add(user_id)
    save_banned_users(banned_users)  # Pass the updated banned_users set
    await message.reply_text(f"User {user_id} has been banned successfully .")

# Command to unban a user
@Mbot.on_message(filters.command("unban") & filters.user(SUDO_USERS))
async def unban_user(client, message):
    await message.delete()
    if len(message.command) != 2:
        await message.reply_text("ℹ️ Usage: /unban <user_id>")
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text("⛔ Invalid user ID. Please provide a numeric user ID.")
        return

    # Remove the user from the ban list
    if user_id in banned_users:
        banned_users.remove(user_id)
        save_banned_users(banned_users)  # Pass the updated banned_users set
        await message.reply_text(f"User {user_id} has been unbanned successfully 🟢.")
    else:
        await message.reply_text(f"User {user_id} is not in the ban list 📋.")

# Command to view the ban list
@Mbot.on_message(filters.command("banlist") & filters.user(SUDO_USERS))
async def view_ban_list(client, message):
    await message.delete()
    if not banned_users:
        await message.reply_text("🕊️ No users are currently banned.")
    else:
        ban_list = "\n".join(str(user_id) for user_id in banned_users)
        await message.reply_text(f"Banned users:\n{ban_list}")

#####################################BAN######################################

######################################SHUTDOWN################################
@Mbot.on_message(filters.command("shutdown") & filters.chat(OWNER_ID) & filters.private)
async def shutdown(_, message):
    await message.delete()

    keyboard = [
        [
            InlineKeyboardButton("🟢 Yes", callback_data="shutdown_yes"),
            InlineKeyboardButton("🔴 No", callback_data="shutdown_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("( •᷄ᴗ•́) Are you sure you want to shut down the bot?", reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"shutdown_(yes|no)"))
async def handle_shutdown_query(_, callback_query):
    if callback_query.data == "shutdown_yes":
        await callback_query.message.delete()
        await callback_query.answer("🔌Shutting down bot...", show_alert=True)

        # Shutdown the bot by stopping the event loop
        await os._exit(0)

    

    elif callback_query.data == "shutdown_no":
        await callback_query.answer("Bot shutdown has been cancelled.", show_alert=True)
        await callback_query.message.delete()


from mbot.utils.language_utils import (
    load_user_languages,
    save_user_languages,
    LANGUAGES,
    get_user_language,
    send_main_start_message
)

GREET_RESPONSES = {
    "en": {  # English
        "banned": "You are banned from using this bot 😢",
        "cpu_usage": "**CPU Usage:** `{cpu_percent}%`",
        "pong": "**Pong!**\nResponse time: `{ms} ms`",
        "donate": "If you would like to support the development of this bot, you can donate here:",
        "greeting": "👋😊Hello {name}, I'm 𝓩𝓟𝓞𝓣𝓘𝓕𝓨.\nI'm Here to download your music.",
        "fetching_message": "Fetching stats...\n[                    ] 0%",
        "select_language": "👋 Please select your preferred language:",
        "maintenance": "🔧 The bot is under maintenance. Please try again later.",
    },

    "es": {  # Spanish
        "banned": "Estás prohibido de usar este bot 😢",
        "cpu_usage": "**Uso de CPU:** `{cpu_percent}%`",
        "pong": "**¡Pong!**\nTiempo de respuesta: `{ms} ms`",
        "donate": "Si deseas apoyar el desarrollo de este bot, puedes donar aquí:",
        "greeting": "👋😊Hola {name}, soy 𝓩𝓟𝓞𝓣𝓘𝓕𝓨.\nEstoy aquí para descargar tu música.",
        "fetching_message": "Obteniendo estadísticas...\n[                    ] 0%",
        "select_language": "👋 Por favor, selecciona tu idioma preferido:",
        "maintenance": "🔧 El bot está en mantenimiento. Por favor, inténtalo más tarde.",
    },

    "hi": {  # Hindi
        "banned": "आप इस बोट के उपयोग से प्रतिबंधित हैं 😢",
        "cpu_usage": "**CPU उपयोग:** `{cpu_percent}%`",
        "pong": "**पोंग!**\nप्रतिक्रिया समय: `{ms} ms`",
        "donate": "यदि आप इस बोट के विकास का समर्थन करना चाहते हैं, तो आप यहाँ दान कर सकते हैं:",
        "greeting": "👋😊नमस्ते **{user_name}**, मैं **𝓩𝓟𝓞𝓣𝓘𝓕𝓨** हूँ।\nमैं यहाँ आपका संगीत डाउनलोड करने के लिए हूँ।",
        "fetching_message": "आँकड़े लाए जा रहे हैं...\n[                    ] 0%",
        "select_language": "👋 कृपया अपनी पसंदीदा भाषा चुनें:",
        "maintenance": "🔧 बोट रखरखाव में है। कृपया बाद में पुनः प्रयास करें।",
    },

    "fa": {  # Persian (Farsi)
        "banned": "شما از استفاده از این ربات ممنوع شده‌اید 😢",
        "cpu_usage": "**استفاده از CPU:** `{cpu_percent}%`",
        "pong": "**پینگ!**\nزمان پاسخ: `{ms} ms`",
        "donate": "اگر مایل به حمایت از توسعه این ربات هستید، می‌توانید از اینجا کمک مالی کنید:",
        "greeting": "👋😊سلام {name}، من 𝓩𝓟𝓞𝓣𝓘𝓕𝓨 هستم.\nاینجا هستم تا موسیقی شما را دانلود کنم.",
        "fetching_message": "دریافت آمار...\n[                    ] 0%",
        "select_language": "👋 لطفاً زبان مورد نظر خود را انتخاب کنید:",
        "maintenance": "🔧 ربات در حال تعمیر و نگهداری است. لطفاً بعداً دوباره امتحان کنید.",
    },

    "fr": {  # French
        "banned": "Vous êtes banni de ce bot 😢",
        "cpu_usage": "**Utilisation du CPU :** `{cpu_percent}%`",
        "pong": "**Pong !**\nTemps de réponse : `{ms} ms`",
        "donate": "Si vous souhaitez soutenir le développement de ce bot, vous pouvez faire un don ici :",
        "greeting": "👋😊Bonjour **{user_name}**, je suis **𝓩𝓟𝓞𝓣𝓘𝓕𝓨**.\nJe suis ici pour télécharger votre musique.",
        "fetching_message": "Récupération des statistiques...\n[                    ] 0%",
        "select_language": "👋 Veuillez sélectionner votre langue préférée :",
        "maintenance": "🔧 Le bot est en maintenance. Veuillez réessayer plus tard.",
    },

    "de": {  # German
        "banned": "Du bist von der Nutzung dieses Bots ausgeschlossen 😢",
        "cpu_usage": "**CPU-Auslastung:** `{cpu_percent}%`",
        "pong": "**Pong!**\nAntwortzeit: `{ms} ms`",
        "donate": "Wenn Sie die Entwicklung dieses Bots unterstützen möchten, können Sie hier spenden:",
        "greeting": "👋😊Hallo **{user_name}**, ich bin **𝓩𝓟𝓞𝓣𝓘𝓕𝓨**.\nIch bin hier, um deine Musik herunterzuladen.",
        "fetching_message": "Statistiken abrufen...\n[                    ] 0%",
        "select_language": "👋 Bitte wählen Sie Ihre bevorzugte Sprache:",
        "maintenance": "🔧 Der Bot wird gewartet. Bitte versuchen Sie es später noch einmal.",
    },

    "ru": {  # Russian
        "banned": "Вам запрещено использовать этого бота 😢",
        "cpu_usage": "**Использование ЦП:** `{cpu_percent}%`",
        "pong": "**Понг!**\nВремя отклика: `{ms} ms`",
        "donate": "Если вы хотите поддержать разработку этого бота, вы можете сделать пожертвование здесь:",
        "greeting": "👋😊Привет, {name}, я 𝓩𝓟𝓞𝓣𝓘𝓕𝓨.\nЯ здесь, чтобы загрузить вашу музыку.",
        "fetching_message": "Получение статистики...\n[                    ] 0%",
        "select_language": "👋 Пожалуйста, выберите предпочитаемый язык:",
        "maintenance": "🔧 Бот на техническом обслуживании. Попробуйте позже.",
    },

    "ar": {  # Arabic
        "banned": "أنت محظور من استخدام هذا البوت 😢",
        "cpu_usage": "**استخدام وحدة المعالجة المركزية:** `{cpu_percent}%`",
        "pong": "**بونغ!**\nوقت الاستجابة: `{ms} ms`",
        "donate": "إذا كنت ترغب في دعم تطوير هذا البوت، يمكنك التبرع هنا:",
        "greeting": "👋😊مرحبًا {name}، أنا 𝓩𝓟𝓞𝓣𝓘𝓕𝓨.\nأنا هنا لتنزيل موسيقاك.",
        "fetching_message": "جاري جلب الإحصائيات...\n[                    ] 0%",
        "select_language": "👋 يرجى اختيار لغتك المفضلة:",
        "maintenance": "🔧 البوت قيد الصيانة. يرجى المحاولة لاحقًا.",
    },
}
INFO_TEXT = {
"en": (
        "💢 **Hello! I am 𝓩𝓟𝓞𝓣𝓘𝓕𝓨** 💢\n\n"
        "✨ **Here are the amazing things I can do for you:** ✨\n\n"
        "1️⃣ **Download Music from YouTube**\n🎵 Send a YouTube link, and I will download the song for you.\n\n"
        "2️⃣ **Download Music from Spotify**\n🎧 Send a Spotify track, playlist, album, show, or episode link, and I will download it for you.\n\n"
        "3️⃣ **Download Music from Deezer**\n🎼 Send a Deezer playlist, album, or track link, and I will download it for you.\n\n"
        "4️⃣ **Download Music from SoundCloud**\n🔊 Send a SoundCloud track link, and I will download it for you.\n\n"
        "5️⃣ **Download IG Reels**\n📸 Send an Instagram link, and I will download the reel, post, or story for you.\n\n"
        "6️⃣ **Ping Command**\n📡 Use the `/ping` command to check the bot's response time.\n\n"
        "7️⃣ **Help Command**\n🛠️ Use the `/help` command to get detailed instructions on how to use the bot.\n\n"
        "8️⃣ **Donate**\n💖 If you love the bot, you can support its development by donating.\n\n"
        "💢 **Feel free to explore and use the commands to get the best out of this bot!** 💢"
    ),
    "fa": (
        "💢 **سلام! من 𝓩𝓟𝓞𝓣𝓘𝓕𝓨 هستم** 💢\n\n"
        "✨ **در اینجا کارهای شگفت‌انگیزی که می‌توانم برای شما انجام دهم آورده شده است:** ✨\n\n"
        "1️⃣ **دانلود موزیک از یوتیوب**\n🎵 یک لینک یوتیوب ارسال کنید، و من آهنگ را برای شما دانلود خواهم کرد.\n\n"
        "2️⃣ **دانلود موزیک از اسپاتیفای**\n🎧 یک لینک آهنگ، پلی‌لیست، آلبوم، نمایش یا اپیزود اسپاتیفای ارسال کنید، و من آن را برای شما دانلود خواهم کرد.\n\n"
        "3️⃣ **دانلود موزیک از دیزر**\n🎼 یک لینک پلی‌لیست، آلبوم یا آهنگ دیزر ارسال کنید، و من آن را برای شما دانلود خواهم کرد.\n\n"
        "4️⃣ **دانلود موزیک از ساندکلاد**\n🔊 یک لینک آهنگ ساندکلاد ارسال کنید، و من آن را برای شما دانلود خواهم کرد.\n\n"
        "5️⃣ **دانلود رییل‌های اینستاگرام**\n📸 یک لینک اینستاگرام ارسال کنید، و من رییل، پست یا استوری را برای شما دانلود خواهم کرد.\n\n"
        "6️⃣ **دستور پینگ**\n📡 از دستور `/ping` برای بررسی زمان پاسخ ربات استفاده کنید.\n\n"
        "7️⃣ **دستور کمک**\n🛠️ از دستور `/help` برای دریافت دستورالعمل‌های دقیق در مورد نحوه استفاده از ربات استفاده کنید.\n\n"
        "8️⃣ **حمایت مالی**\n💖 اگر ربات را دوست دارید، می‌توانید از طریق کمک مالی از توسعه آن حمایت کنید.\n\n"
        "💢 **احساس راحتی کنید و از دستورات برای بهره‌برداری حداکثری از این ربات استفاده کنید!** 💢"
    ),
    "ru": (
        "💢 **Привет! Я 𝓩𝓟𝓞𝓣𝓘𝓕𝓨** 💢\n\n"
        "✨ **Вот удивительные вещи, которые я могу для вас сделать:** ✨\n\n"
        "1️⃣ **Скачать музыку с YouTube**\n🎵 Отправьте ссылку на YouTube, и я скачаю песню для вас.\n\n"
        "2️⃣ **Скачать музыку с Spotify**\n🎧 Отправьте ссылку на трек, плейлист, альбом, шоу или эпизод Spotify, и я скачаю его для вас.\n\n"
        "3️⃣ **Скачать музыку с Deezer**\n🎼 Отправьте ссылку на плейлист, альбом или трек Deezer, и я скачаю его для вас.\n\n"
        "4️⃣ **Скачать музыку с SoundCloud**\n🔊 Отправьте ссылку на трек SoundCloud, и я скачаю его для вас.\n\n"
        "5️⃣ **Скачать IG Reels**\n📸 Отправьте ссылку на Instagram, и я скачаю рил, пост или историю для вас.\n\n"
        "6️⃣ **Команда Ping**\n📡 Используйте команду `/ping`, чтобы проверить время отклика бота.\n\n"
        "7️⃣ **Команда Help**\n🛠️ Используйте команду `/help`, чтобы получить подробные инструкции по использованию бота.\n\n"
        "8️⃣ **Пожертвовать**\n💖 Если вам нравится бот, вы можете поддержать его развитие, сделав пожертвование.\n\n"
        "💢 **Не стесняйтесь исследовать и использовать команды, чтобы получить максимум от этого бота!** 💢"
    ),
    "es": (
        "💢 **¡Hola! Soy 𝓩𝓟𝓞𝓣𝓘𝓕𝓨** 💢\n\n"
        "✨ **Aquí están las cosas increíbles que puedo hacer por ti:** ✨\n\n"
        "1️⃣ **Descargar música de YouTube**\n🎵 Envía un enlace de YouTube, y descargaré la canción para ti.\n\n"
        "2️⃣ **Descargar música de Spotify**\n🎧 Envía un enlace de una canción, lista de reproducción, álbum, programa o episodio de Spotify, y lo descargaré para ti.\n\n"
        "3️⃣ **Descargar música de Deezer**\n🎼 Envía un enlace de una lista de reproducción, álbum o canción de Deezer, y lo descargaré para ti.\n\n"
        "4️⃣ **Descargar música de SoundCloud**\n🔊 Envía un enlace de una canción de SoundCloud, y la descargaré para ti.\n\n"
        "5️⃣ **Descargar IG Reels**\n📸 Envía un enlace de Instagram, y descargaré el reel, la publicación o la historia para ti.\n\n"
        "6️⃣ **Comando Ping**\n📡 Usa el comando `/ping` para verificar el tiempo de respuesta del bot.\n\n"
        "7️⃣ **Comando Help**\n🛠️ Usa el comando `/help` para obtener instrucciones detalladas sobre cómo usar el bot.\n\n"
        "8️⃣ **Donar**\n💖 Si te gusta el bot, puedes apoyar su desarrollo donando.\n\n"
        "💢 **¡Siéntete libre de explorar y usar los comandos para aprovechar al máximo este bot!** 💢"
    ),
    "ar": (
        "💢 **مرحبًا! أنا 𝓩𝓟𝓞𝓣𝓘𝓕𝓨** 💢\n\n"
        "✨ **إليك الأشياء المذهلة التي يمكنني القيام بها من أجلك:** ✨\n\n"
        "1️⃣ **تنزيل الموسيقى من YouTube**\n🎵 أرسل رابط YouTube، وسأقوم بتنزيل الأغنية لك.\n\n"
        "2️⃣ **تنزيل الموسيقى من Spotify**\n🎧 أرسل رابط أغنية، قائمة تشغيل، ألبوم، عرض أو حلقة من Spotify، وسأقوم بتنزيلها لك.\n\n"
        "3️⃣ **تنزيل الموسيقى من Deezer**\n🎼 أرسل رابط قائمة تشغيل، ألبوم أو أغنية من Deezer، وسأقوم بتنزيلها لك.\n\n"
        "4️⃣ **تنزيل الموسيقى من SoundCloud**\n🔊 أرسل رابط أغنية من SoundCloud، وسأقوم بتنزيلها لك.\n\n"
        "5️⃣ **تنزيل IG Reels**\n📸 أرسل رابط Instagram، وسأقوم بتنزيل الريل، المنشور أو القصة لك.\n\n"
        "6️⃣ **أمر Ping**\n📡 استخدم الأمر `/ping` للتحقق من وقت استجابة البوت.\n\n"
        "7️⃣ **أمر Help**\n🛠️ استخدم الأمر `/help` للحصول على تعليمات مفصلة حول كيفية استخدام البوت.\n\n"
        "8️⃣ **التبرع**\n💖 إذا كنت تحب البوت، يمكنك دعم تطويره من خلال التبرع.\n\n"
        "💢 **لا تتردد في استكشاف واستخدام الأوامر للحصول على أقصى استفادة من هذا البوت!** 💢"
    ),
    "hi": (
        "💢 **नमस्ते! मैं 𝓩𝓟𝓞𝓣𝓘𝓕𝓨 हूँ** 💢\n\n"
        "✨ **यहाँ वे अद्भुत चीज़ें हैं जो मैं आपके लिए कर सकता हूँ:** ✨\n\n"
        "1️⃣ **YouTube से संगीत डाउनलोड करें**\n🎵 एक YouTube लिंक भेजें, और मैं आपके लिए गाना डाउनलोड करूँगा।\n\n"
        "2️⃣ **Spotify से संगीत डाउनलोड करें**\n🎧 एक Spotify ट्रैक, प्लेलिस्ट, एल्बम, शो या एपिसोड लिंक भेजें, और मैं इसे आपके लिए डाउनलोड करूँगा।\n\n"
        "3️⃣ **Deezer से संगीत डाउनलोड करें**\n🎼 एक Deezer प्लेलिस्ट, एल्बम या ट्रैक लिंक भेजें, और मैं इसे आपके लिए डाउनलोड करूँगा।\n\n"
        "4️⃣ **SoundCloud से संगीत डाउनलोड करें**\n🔊 एक SoundCloud ट्रैक लिंक भेजें, और मैं इसे आपके लिए डाउनलोड करूँगा।\n\n"
        "5️⃣ **IG Reels डाउनलोड करें**\n📸 एक Instagram लिंक भेजें, और मैं रील, पोस्ट या स्टोरी आपके लिए डाउनलोड करूँगा।\n\n"
        "6️⃣ **Ping कमांड**\n📡 बॉट के प्रतिक्रिया समय की जांच के लिए `/ping` कमांड का उपयोग करें।\n\n"
        "7️⃣ **Help कमांड**\n🛠️ बॉट का उपयोग करने के तरीके के बारे में विस्तृत निर्देश प्राप्त करने के लिए `/help` कमांड का उपयोग करें।\n\n"
        "8️⃣ **दान करें**\n💖 यदि आप बॉट को पसंद करते हैं, तो आप दान करके इसके विकास का समर्थन कर सकते हैं।\n\n"
        "💢 **इस बॉट का अधिकतम लाभ उठाने के लिए कमांड्स का उपयोग करने के लिए स्वतंत्र महसूस करें!** 💢"
    )
}


@Mbot.on_message(filters.command("settings"))
@maintenance_check
async def settings(client, message):
    await message.delete()
    
    keyboard = [
        [InlineKeyboardButton("🌐 Change Language", callback_data="change_language")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("⚙️ Settings:\nChoose an option:", reply_markup=reply_markup)
    
# Handler for the /start command
@Mbot.on_message(filters.command("start"))
@maintenance_check
async def start(client, message):
    user_id = message.from_user.id
    user_lang = get_user_language(user_id)
    
    await message.delete()

    if user_id in banned_users:
        await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("banned", "You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
        return

    # Default commands for all users
    commands = [
        BotCommand("start", "🎬 Start the bot and initiate tasks"),
        BotCommand("help", "❓ Learn how to use the bot"),
        BotCommand("saavn", "🎶 Download music from Saavn"),
        BotCommand("song", "🎵 Type song name to fetch it"),
        BotCommand("lyrics", "📝 Reply with a song name to get lyrics"),
        BotCommand("genius", "🎤 Get lyrics from GENIUS"),
        BotCommand("search", "🔍 Find your favorite music"),
        BotCommand("info", "ℹ️ Get info about this bot"),
        BotCommand("ping", "⚡️ Check bot response time"),
        BotCommand("stats", "📊 View your current status"),
        BotCommand("settings", "⚙️ Adjust your preferences"),
        BotCommand("donate", "💖 Support this project with a donation"),
    ]

    # Add /admin command only for Owner and Sudo Users
    if user_id == OWNER_ID or user_id in SUDO_USERS:
        commands.append(BotCommand("admin", "⚜️ Admin Panel"))

    # Apply the commands for the specific user
    await client.set_my_commands(commands, scope="default", user_id=user_id)

    await message.reply_text("✅ Your menu commands have been set according to your access level.")
    # Add user to the user list
    user_list.add(message.from_user.id)
    save_user_list(user_list)  # Save the updated user list

    # Check if the user has already selected a language
    user_languages = load_user_languages()
    user_id = str(message.from_user.id)
    if user_id in user_languages:
        # If the user has already selected a language, send the main start message
        await send_main_start_message(client, message, user_languages[user_id])
    else:
        # If the user hasn't selected a language, ask for their preferred language
        keyboard = [
            [InlineKeyboardButton(LANGUAGES[lang], callback_data=f"set_lang_{lang}")] for lang in LANGUAGES
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            "👋 Please select your preferred language:",
            reply_markup=reply_markup
        )


# Handler for language selection callback
@Mbot.on_callback_query(filters.regex(r"set_lang_(.*)"))
async def handle_language_selection(client, callback_query):
    lang_code = callback_query.data.split("_")[2]  # Extract language code
    user_id = str(callback_query.from_user.id)

    # Save the user's language preference
    user_languages = load_user_languages()
    user_languages[user_id] = lang_code
    save_user_languages(user_languages)

    # Send a confirmation message
    await callback_query.answer(f"Language set to {LANGUAGES[lang_code]}", show_alert=True)

    # Send the main start message in the selected language
    await send_main_start_message(client, callback_query.message, lang_code)

############################RESTART######################################
@Mbot.on_message(filters.command("restart") & filters.chat(OWNER_ID) & filters.private)
async def restart(_, message):
    await message.delete()

    keyboard = [
        [
            InlineKeyboardButton("🟢 Yes", callback_data="restart_yes"),
            InlineKeyboardButton("🔴 No", callback_data="restart_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.delete()
    await message.reply_text("( •᷄ᴗ•́) Are you sure you want to restart the bot?", reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"restart_(yes|no)"))
async def handle_restart_query(_, callback_query):
    if callback_query.data == "restart_yes":
        await callback_query.message.delete()
        await callback_query.answer("Restarting bot...", show_alert=True)
        
        execvp(sys.executable, [sys.executable, "-m", "mbot"])
    elif callback_query.data == "restart_no":
        await callback_query.answer("Bot restart has been cancelled.", show_alert=True)
        await callback_query.message.delete()

############################RESTART######################################
@Mbot.on_message(filters.command("log") & filters.chat(SUDO_USERS))
async def send_log(_, message):
    await message.delete()
    await message.reply_document("bot.log")

@Mbot.on_message(filters.command("cpu"))
async def cpu_usage(_, message):
    await message.delete()
    cpu_percent = psutil.cpu_percent(interval=1)
    await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("cpu_usage", "**CPU Usage:** `{cpu_percent}%`"))


@Mbot.on_message(filters.command("ping"))
@maintenance_check
async def ping(client, message):
    if message.from_user.id in banned_users:
        await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("banned", "You are banned from using this bot  😢"))

        return
    start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    ms = (datetime.now() - start).microseconds / 1000
    await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("pong", "**Pong!**\nResponse time: `{ms} ms`"))

@Mbot.on_message(filters.command("donate"))
@maintenance_check
async def donate(_, message):
    if message.from_user.id in banned_users:
        await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("banned","You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Donate", url="https://www.buymeacoffee.com/zasasamar")],
        [InlineKeyboardButton(text="❌", callback_data="close")]
    ])
    await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("donate", "If you would like to support the development of this bot, you can donate here:", reply_markup=keyboard))

@Mbot.on_message(filters.command("info"))
@maintenance_check
async def info(_, message):
    if message.from_user.id in banned_users:
        await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("banned","You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
        return
        user_lang = get_user_language(message.from_user.id)  # Function to get the user's language
        responses = INFO_TEXT.get(user_lang, INFO_TEXT["en"])  # Default to English if language is not found

    info_text = (
    "💢 **Hello! I am 𝓩𝓟𝓞𝓣𝓘𝓕𝓨** 💢\n\n"
    "✨ **Here are the amazing things I can do for you:** ✨\n\n"
    
    "1️⃣ **Download Music from YouTube**\n"
    "🎵 Send a YouTube link, and I will download the song for you.\n\n"
    
    "2️⃣ **Download Music from Spotify**\n"
    "🎧 Send a Spotify track, playlist, album, show, or episode link, and I will download it for you.\n\n"
    
    "3️⃣ **Download Music from Deezer**\n"
    "🎼 Send a Deezer playlist, album, or track link, and I will download it for you.\n\n"
    
    "4️⃣ **Download Music from SoundCloud**\n"
    "🔊 Send a SoundCloud track link, and I will download it for you.\n\n"
    
    "5️⃣ **Download IG Reels**\n"
    "📸 Send an Instagram link, and I will download the reel, post, or story for you.\n\n"
    
    "6️⃣ **Ping Command**\n"
    "📡 Use the `/ping` command to check the bot's response time.\n\n"
    
    "7️⃣ **Help Command**\n"
    "🛠️ Use the `/help` command to get detailed instructions on how to use the bot.\n\n"
    
    "8️⃣ **Donate**\n"
    "💖 If you love the bot, you can support its development by donating.\n\n"
    
    "💢 **Feel free to explore and use the commands to get the best out of this bot!** 💢"
)
    await message.reply_text(INFO_TEXT.get(user_lang, {}).get(info_text))

STATS_TEXT = {

"en": {
    "server_status": "⚡️ **ZPOTIFY Server Status** ⚡️\n\n",
    "server_os": "💻 **Server OS** 💻\n",
    "os_type": "🌐 **Operating System Type:** {os_type}\n",
    "linux_type": "📜 **Linux Type:** {linux_type}\n\n",
    "cpu_status": "🖥️ **CPU Status** 🖥️\n",
    "cpu_cores": "🧮 **CPU Cores:** {cpu_cores}\n",
    "cpu_usage": "📊 **CPU Usage:** {cpu_usage}%\n",
    "cpu_free": "💾 **CPU Free:** {cpu_free}%\n",
    "response_status": "📡 **Response Status** 📡\n",
    "telegram_response_time": "⏱️ **Telegram API Response Time:** {round(telegram_response_time)} ms\n",
    "spotify_response_time": "🎵 **Spotify API Response Time:** {spotify_response_time:.2f} ms\n\n",
    "memory_status": "💾 **Memory Status** 💾\n",
    "total_ram": "💽 **Total RAM:** {total_ram:.2f} MB\n",
    "ram_usage": "🔋 **RAM Usage:** {ram_usage}%\n",
    "ram_available": "📥 **RAM Available:** {ram_available:.2f} MB\n",
    "used_ram": "📤 **Used RAM:** {used_ram:.2f} MB\n\n",
    "database_status": "📚 **Database Status** 📚\n",
    "db1_used_size": "📂 **DB 1 Used Size:** {db1_used_size} MB\n",
    "db1_free_size": "📂 **DB 1 Free Size:** {db1_free_size} MB\n",
    "db2_used_size": "📂 **DB 2 Used Size:** {db2_used_size} MB\n",
    "db2_free_size": "📂 **DB 2 Free Size:** {db2_free_size} MB\n\n",
    "users_status": "👥 **Users Status** 👥\n",
    "total_users": "👤 **Total Users:** {total_users}\n",
    "total_files": "📁 **Total Files:** {total_files}\n",
    "total_premium_users": "✨ **Total Premium Users and Premium Trial Users:** {total_premium_users}\n",
    "total_premium_trials": "🌟 **Users Who Enjoyed Premium Trials and Plans:** {total_premium_trials}\n"
},

"fa": {
    "server_status": "⚡️ **وضعیت سرور زپاتیفای** ⚡️\n\n",
    "server_os": "💻 **سیستم عامل سرور** 💻\n",
    "os_type": "🌐 **نوع سیستم عامل:** {os_type}\n",
    "linux_type": "📜 **نوع لینوکس:** {linux_type}\n\n",
    "cpu_status": "🖥️ **وضعیت سی‌پی‌یو** 🖥️\n",
    "cpu_cores": "🧮 **هسته‌های سی‌پی‌یو:** {cpu_cores}\n",
    "cpu_usage": "📊 **مصرف سی‌پی‌یو:** {cpu_usage}%\n",
    "cpu_free": "💾 **سی‌پی‌یو آزاد:** {cpu_free}%\n",
    "response_status": "📡 **وضعیت پاسخ** 📡\n",
    "telegram_response_time": "⏱️ **زمان پاسخ API تلگرام:** {round(telegram_response_time)} ms\n",
    "spotify_response_time": "🎵 **زمان پاسخ API اسپاتیفای:** {spotify_response_time:.2f} ms\n\n",
    "memory_status": "💾 **وضعیت حافظه** 💾\n",
    "total_ram": "💽 **مجموع رم:** {total_ram:.2f} MB\n",
    "ram_usage": "🔋 **مصرف رم:** {ram_usage}%\n",
    "ram_available": "📥 **رم قابل دسترس:** {ram_available:.2f} MB\n",
    "used_ram": "📤 **رم مصرف شده:** {used_ram:.2f} MB\n\n",
    "database_status": "📚 **وضعیت پایگاه‌داده** 📚\n",
    "db1_used_size": "📂 **اندازه استفاده شده DB 1:** {db1_used_size} MB\n",
    "db1_free_size": "📂 **اندازه آزاد DB 1:** {db1_free_size} MB\n",
    "db2_used_size": "📂 **اندازه استفاده شده DB 2:** {db2_used_size} MB\n",
    "db2_free_size": "📂 **اندازه آزاد DB 2:** {db2_free_size} MB\n\n",
    "users_status": "👥 **وضعیت کاربران** 👥\n",
    "total_users": "👤 **مجموع کاربران:** {total_users}\n",
    "total_files": "📁 **مجموع فایل‌ها:** {total_files}\n",
    "total_premium_users": "✨ **مجموع کاربران پرمیوم و آزمایشی پرمیوم:** {total_premium_users}\n",
    "total_premium_trials": "🌟 **کاربرانی که از آزمایش‌های پرمیوم و برنامه‌های پرمیوم بهره‌مند شدند:** {total_premium_trials}\n"
},
"ru": {
    "server_status": "⚡️ **Статус сервера ZPOTIFY** ⚡️\n\n",
    "server_os": "💻 **ОС сервера** 💻\n",
    "os_type": "🌐 **Тип операционной системы:** {os_type}\n",
    "linux_type": "📜 **Тип Linux:** {linux_type}\n\n",
    "cpu_status": "🖥️ **Статус процессора** 🖥️\n",
    "cpu_cores": "🧮 **Ядра процессора:** {cpu_cores}\n",
    "cpu_usage": "📊 **Загрузка процессора:** {cpu_usage}%\n",
    "cpu_free": "💾 **Свободный процессор:** {cpu_free}%\n",
    "response_status": "📡 **Статус ответа** 📡\n",
    "telegram_response_time": "⏱️ **Время отклика API Telegram:** {round(telegram_response_time)} ms\n",
    "spotify_response_time": "🎵 **Время отклика API Spotify:** {spotify_response_time:.2f} ms\n\n",
    "memory_status": "💾 **Статус памяти** 💾\n",
    "total_ram": "💽 **Всего RAM:** {total_ram:.2f} MB\n",
    "ram_usage": "🔋 **Использование RAM:** {ram_usage}%\n",
    "ram_available": "📥 **Доступный RAM:** {ram_available:.2f} MB\n",
    "used_ram": "📤 **Используемый RAM:** {used_ram:.2f} MB\n\n",
    "database_status": "📚 **Статус базы данных** 📚\n",
    "db1_used_size": "📂 **Использованный размер DB 1:** {db1_used_size} MB\n",
    "db1_free_size": "📂 **Свободный размер DB 1:** {db1_free_size} MB\n",
    "db2_used_size": "📂 **Использованный размер DB 2:** {db2_used_size} MB\n",
    "db2_free_size": "📂 **Свободный размер DB 2:** {db2_free_size} MB\n\n",
    "users_status": "👥 **Статус пользователей** 👥\n",
    "total_users": "👤 **Всего пользователей:** {total_users}\n",
    "total_files": "📁 **Всего файлов:** {total_files}\n",
    "total_premium_users": "✨ **Всего премиум и тестовых пользователей:** {total_premium_users}\n",
    "total_premium_trials": "🌟 **Пользователи, воспользовавшиеся премиум-испытаниями и планами:** {total_premium_trials}\n"
},
"es": {
    "server_status": "⚡️ **Estado del Servidor ZPOTIFY** ⚡️\n\n",
    "server_os": "💻 **Sistema Operativo del Servidor** 💻\n",
    "os_type": "🌐 **Tipo de Sistema Operativo:** {os_type}\n",
    "linux_type": "📜 **Tipo de Linux:** {linux_type}\n\n",
    "cpu_status": "🖥️ **Estado de la CPU** 🖥️\n",
    "cpu_cores": "🧮 **Núcleos de la CPU:** {cpu_cores}\n",
    "cpu_usage": "📊 **Uso de la CPU:** {cpu_usage}%\n",
    "cpu_free": "💾 **CPU Libre:** {cpu_free}%\n",
    "response_status": "📡 **Estado de Respuesta** 📡\n",
    "telegram_response_time": "⏱️ **Tiempo de Respuesta de la API de Telegram:** {round(telegram_response_time)} ms\n",
    "spotify_response_time": "🎵 **Tiempo de Respuesta de la API de Spotify:** {spotify_response_time:.2f} ms\n\n",
    "memory_status": "💾 **Estado de la Memoria** 💾\n",
    "total_ram": "💽 **RAM Total:** {total_ram:.2f} MB\n",
    "ram_usage": "🔋 **Uso de la RAM:** {ram_usage}%\n",
    "ram_available": "📥 **RAM Disponible:** {ram_available:.2f} MB\n",
    "used_ram": "📤 **RAM Usada:** {used_ram:.2f} MB\n\n",
    "database_status": "📚 **Estado de la Base de Datos** 📚\n",
    "db1_used_size": "📂 **Tamaño Utilizado DB 1:** {db1_used_size} MB\n",
    "db1_free_size": "📂 **Tamaño Libre DB 1:** {db1_free_size} MB\n",
    "db2_used_size": "📂 **Tamaño Utilizado DB 2:** {db2_used_size} MB\n",
    "db2_free_size": "📂 **Tamaño Libre DB 2:** {db2_free_size} MB\n\n",
    "users_status": "👥 **Estado de los Usuarios** 👥\n",
    "total_users": "👤 **Total de Usuarios:** {total_users}\n",
    "total_files": "📁 **Total de Archivos:** {total_files}\n",
    "total_premium_users": "✨ **Total de Usuarios Premium y de Prueba Premium:** {total_premium_users}\n",
    "total_premium_trials": "🌟 **Usuarios que Disfrutaron de Pruebas y Planes Premium:** {total_premium_trials}\n"
},
"ar": {
    "server_status": "⚡️ **حالة خادم زبوتيفاي** ⚡️\n\n",
    "server_os": "💻 **نظام تشغيل الخادم** 💻\n",
    "os_type": "🌐 **نوع نظام التشغيل:** {os_type}\n",
    "linux_type": "📜 **نوع لينكس:** {linux_type}\n\n",
    "cpu_status": "🖥️ **حالة وحدة المعالجة المركزية** 🖥️\n",
    "cpu_cores": "🧮 **أنوية وحدة المعالجة المركزية:** {cpu_cores}\n",
    "cpu_usage": "📊 **استخدام وحدة المعالجة المركزية:** {cpu_usage}%\n",
    "cpu_free": "💾 **وحدة المعالجة المركزية الحرة:** {cpu_free}%\n",
    "response_status": "📡 **حالة الاستجابة** 📡\n",
    "telegram_response_time": "⏱️ **وقت استجابة API تلغرام:** {round(telegram_response_time)} ms\n",
    "spotify_response_time": "🎵 **وقت استجابة API سبوتيفاي:** {spotify_response_time:.2f} ms\n\n",
    "memory_status": "💾 **حالة الذاكرة** 💾\n",
    "total_ram": "💽 **مجموع ذاكرة الوصول العشوائي:** {total_ram:.2f} MB\n",
    "ram_usage": "🔋 **استخدام ذاكرة الوصول العشوائي:** {ram_usage}%\n",
    "ram_available": "📥 **ذاكرة الوصول العشوائي المتاحة:** {ram_available:.2f} MB\n",
    "used_ram": "📤 **ذاكرة الوصول العشوائي المستخدمة:** {used_ram:.2f} MB\n\n",
    "database_status": "📚 **حالة قاعدة البيانات** 📚\n",
    "db1_used_size": "📂 **حجم قاعدة البيانات المستخدمة 1:** {db1_used_size} MB\n",
    "db1_free_size": "📂 **حجم قاعدة البيانات الحرة 1:** {db1_free_size} MB\n",
    "db2_used_size": "📂 **حجم قاعدة البيانات المستخدمة 2:** {db2_used_size} MB\n",
    "db2_free_size": "📂 **حجم قاعدة البيانات الحرة 2:** {db2_free_size} MB\n\n",
    "users_status": "👥 **حالة المستخدمين** 👥\n",
    "total_users": "👤 **إجمالي المستخدمين:** {total_users}\n",
    "total_files": "📁 **إجمالي الملفات:** {total_files}\n",
    "total_premium_users": "✨ **إجمالي المستخدمين المميزين والمستخدمين التجريبيين:** {total_premium_users}\n",
    "total_premium_trials": "🌟 **المستخدمين الذين استفادوا من التجارب المميزة والخطط:** {total_premium_trials}\n"
},
"hi": {
    "server_status": "⚡️ **ज़्पॉटीफ़ाई सर्वर स्थिति** ⚡️\n\n",
    "server_os": "💻 **सर्वर ऑपरेटिंग सिस्टम** 💻\n",
    "os_type": "🌐 **ऑपरेटिंग सिस्टम प्रकार:** {os_type}\n",
    "linux_type": "📜 **लिनक्स प्रकार:** {linux_type}\n\n",
    "cpu_status": "🖥️ **सीपीयू स्थिति** 🖥️\n",
    "cpu_cores": "🧮 **सीपीयू कोर:** {cpu_cores}\n",
    "cpu_usage": "📊 **सीपीयू उपयोग:** {cpu_usage}%\n",
    "cpu_free": "💾 **मुक्त सीपीयू:** {cpu_free}%\n",
    "response_status": "📡 **प्रतिक्रिया स्थिति** 📡\n",
    "telegram_response_time": "⏱️ **टेलीग्राम एपीआई प्रतिक्रिया समय:** {round(telegram_response_time)} ms\n",
    "spotify_response_time": "🎵 **स्पॉटीफ़ाई एपीआई प्रतिक्रिया समय:** {spotify_response_time:.2f} ms\n\n",
    "memory_status": "💾 **मेमोरी स्थिति** 💾\n",
    "total_ram": "💽 **कुल रैम:** {total_ram:.2f} MB\n",
    "ram_usage": "🔋 **रैम उपयोग:** {ram_usage}%\n",
    "ram_available": "📥 **उपलब्ध रैम:** {ram_available:.2f} MB\n",
    "used_ram": "📤 **उपयोग की गई रैम:** {used_ram:.2f} MB\n\n",
    "database_status": "📚 **डेटाबेस स्थिति** 📚\n",
    "db1_used_size": "📂 **DB 1 उपयोग आकार:** {db1_used_size} MB\n",
    "db1_free_size": "📂 **DB 1 मुक्त आकार:** {db1_free_size} MB\n",
    "db2_used_size": "📂 **DB 2 उपयोग आकार:** {db2_used_size} MB\n",
    "db2_free_size": "📂 **DB 2 मुक्त आकार:** {db2_free_size} MB\n\n",
    "users_status": "👥 **उपयोगकर्ता स्थिति** 👥\n",
    "total_users": "👤 **कुल उपयोगकर्ता:** {total_users}\n",
    "total_files": "📁 **कुल फ़ाइलें:** {total_files}\n",
    "total_premium_users": "✨ **कुल प्रीमियम उपयोगकर्ता और प्रीमियम ट्रायल उपयोगकर्ता:** {total_premium_users}\n",
    "total_premium_trials": "🌟 **उपयोगकर्ता जिन्होंने प्रीमियम ट्रायल्स और योजनाओं का आनंद लिया:** {total_premium_trials}\n"
}
}

@Mbot.on_message(filters.command("stats"))
@maintenance_check
async def stats(client, message):

    user_lang = get_user_language(message.from_user.id)  # Fetch the user's preferred language
    responses = STATS_TEXT.get(user_lang, STATS_TEXT["en"])  # Default to English if not found

    if message.from_user.id in banned_users:
        await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("banned","You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) "))
        return
    # Initial reply with a placeholder message
    fetching_message = await message.reply_text(GREET_RESPONSES.get(user_lang, {}).get("fetching_message", "Fetching stats...\n[                    ] 0%"))
    
    # Simulate progress by updating the message incrementally
    for progress in range(0, 101, 10):
        bar = "█" * (progress // 10) + " " * (10 - (progress // 10))
        await fetching_message.edit_text(GREET_RESPONSES.get(user_lang, {}).get(f"Fetching stats...\n[{bar}] {progress}%"))
        await sleep(0.5)  # Adjust sleep time to control animation speed
    
    # Gather system information
    os_type = sys.platform
    linux_type = " ".join(os.uname()) if hasattr(os, 'uname') else "N/A"
    cpu_cores = psutil.cpu_count(logical=True)
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_free = 100 - cpu_usage
    core_usages = psutil.cpu_percent(interval=1, percpu=True)
    memory = psutil.virtual_memory()
    total_ram = memory.total / (1024 ** 2)
    ram_usage = memory.percent
    ram_available = memory.available / (1024 ** 2)
    used_ram = memory.used / (1024 ** 2)
    # Simulate database status (replace with actual database queries if available)
    db1_used_size = 116.23
    db1_free_size = 395.77
    db2_used_size = 10.47
    db2_free_size = 501.53
    # Simulate user and file counts (replace with actual queries if available)
    total_users = 61864
    total_files = 42590
    total_premium_users = 0
    total_premium_trials = 31916
    # Measure response times
    start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    telegram_response_time = (datetime.now() - start).microseconds / 1000
    start = datetime.now()
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.search("test")  # Dummy search to measure response time
    spotify_response_time = (datetime.now() - start).microseconds / 1000
    stats_text = (
    "⚡️ **𝓩𝓟𝓞𝓣𝓘𝓕𝓨 Server Status** ⚡️\n\n"
    
    "💻 **Server OS** 💻\n"
    f"🌐 **Operating System Type:** {os_type}\n"
    f"📜 **Linux Type:** {linux_type}\n\n"
    
    "🖥️ **CPU Status** 🖥️\n"
    f"🧮 **CPU Cores:** {cpu_cores}\n"
    f"📊 **CPU Usage:** {cpu_usage}%\n"
    f"💾 **CPU Free:** {cpu_free}%\n"
    + "\n".join([f"⚙️ **Core {i + 1}:** {usage}%" for i, usage in enumerate(core_usages)]) + "\n\n"
    
    "📡 **Response Status** 📡\n"
    f"⏱️ **Telegram API Response Time:** {round(telegram_response_time)} ms\n"
    f"🎵 **Spotify API Response Time:** {spotify_response_time:.2f} ms\n\n"
    
    "💾 **Memory Status** 💾\n"
    f"💽 **Total RAM:** {total_ram:.2f} MB\n"
    f"🔋 **RAM Usage:** {ram_usage}%\n"
    f"📥 **RAM Available:** {ram_available:.2f} MB\n"
    f"📤 **Used RAM:** {used_ram:.2f} MB\n\n"
    
    "📚 **Database Status** 📚\n"
    f"📂 **DB 1 Used Size:** {db1_used_size} MB\n"
    f"📂 **DB 1 Free Size:** {db1_free_size} MB\n"
    f"📂 **DB 2 Used Size:** {db2_used_size} MB\n"
    f"📂 **DB 2 Free Size:** {db2_free_size} MB\n\n"
    
    "👥 **Users Status** 👥\n"
    f"👤 **Total Users:** {total_users}\n"
    f"📁 **Total Files:** {total_files}\n"
    f"✨ **Total Premium Users and Premium Trial Users:** {total_premium_users}\n"
    f"🌟 **Users Who Enjoyed Premium Trials and Plans:** {total_premium_trials}\n"
)
    await fetching_message.delete()
    await message.reply_text(STATS_TEXT.get(user_lang, {}).get(stats_text))

    

HELP_TEXT = {
    "en": {
        "YouTube": (
            "1️⃣ **🌟 Download Music from YouTube**\n"
            "   ➤ Send me a YouTube link, and I’ll fetch the song for you."
        ),
        "Spotify": (
            "2️⃣ **🌟 Download Music from Spotify**\n"
            "   ➤ Share a Spotify track, playlist, album, show, or episode link, "
            "and I'll download it for you."
        ),
        "Deezer": (
            "3️⃣ **🌟 Download Music from Deezer**\n"
            "   ➤ Provide a Deezer playlist, album, or track link, and I'll handle the rest."
        ),
        "Soundcloud": (
            "4️⃣ **🌟 Download Music from Soundcloud**\n"
            "   ➤ Send a Soundcloud track link, and I’ll get the song for you."
        ),
        "Instagram": (
            "5️⃣ **🌟 Download Instagram Reels**\n"
            "   ➤ Share an Instagram link, and I’ll download the reel, post, or story for you."
        ),
        "JioSaavn": (
            "6️⃣ **🌟 Download Music from JioSaavn**\n"
            "   ➤ Send a JioSaavn link to download the song."
        ),
        "Group": (
            "7️⃣ **🌟 Group Functionality**\n"
            "   ➤ Group functionality will be added later."
        ),
    },
    "fa": {
        "YouTube": (
            "1️⃣ **🌟 دانلود موزیک از یوتیوب**\n"
            "   ➤ یک لینک یوتیوب برای من بفرستید، و من آهنگ را برای شما دانلود خواهم کرد."
        ),
        "Spotify": (
            "2️⃣ **🌟 دانلود موزیک از اسپاتیفای**\n"
            "   ➤ یک لینک آهنگ، پلی‌لیست، آلبوم، نمایش یا اپیزود از اسپاتیفای به اشتراک بگذارید، "
            "و من آن را برای شما دانلود خواهم کرد."
        ),
        "Deezer": (
            "3️⃣ **🌟 دانلود موزیک از دیزر**\n"
            "   ➤ یک لینک پلی‌لیست، آلبوم یا آهنگ از دیزر ارائه دهید، و من بقیه کارها را انجام خواهم داد."
        ),
        "Soundcloud": (
            "4️⃣ **🌟 دانلود موزیک از ساندکلاد**\n"
            "   ➤ یک لینک آهنگ از ساندکلاد بفرستید، و من آهنگ را برای شما دریافت خواهم کرد."
        ),
        "Instagram": (
            "5️⃣ **🌟 دانلود رییل‌های اینستاگرام**\n"
            "   ➤ یک لینک اینستاگرام به اشتراک بگذارید، و من رییل، پست یا استوری را برای شما دانلود خواهم کرد."
        ),
        "JioSaavn": (
            "6️⃣ **🌟 دانلود موزیک از جیوساون**\n"
            "   ➤ یک لینک جیوساون برای دانلود آهنگ بفرستید."
        ),
        "Group": (
            "7️⃣ **🌟 عملکرد گروهی**\n"
            "   ➤ عملکرد گروهی در آینده اضافه خواهد شد."
        ),
    },
    "ru": {
        "YouTube": (
            "1️⃣ **🌟 Скачать музыку с YouTube**\n"
            "   ➤ Отправьте мне ссылку на YouTube, и я найду песню для вас."
        ),
        "Spotify": (
            "2️⃣ **🌟 Скачать музыку с Spotify**\n"
            "   ➤ Поделитесь ссылкой на трек, плейлист, альбом, шоу или эпизод Spotify, "
            "и я скачаю его для вас."
        ),
        "Deezer": (
            "3️⃣ **🌟 Скачать музыку с Deezer**\n"
            "   ➤ Предоставьте ссылку на плейлист, альбом или трек Deezer, и я сделаю всё остальное."
        ),
        "Soundcloud": (
            "4️⃣ **🌟 Скачать музыку с Soundcloud**\n"
            "   ➤ Отправьте ссылку на трек Soundcloud, и я получу песню для вас."
        ),
        "Instagram": (
            "5️⃣ **🌟 Скачать рилсы из Instagram**\n"
            "   ➤ Поделитесь ссылкой на Instagram, и я скачаю рилс, пост или историю для вас."
        ),
        "JioSaavn": (
            "6️⃣ **🌟 Скачать музыку с JioSaavn**\n"
            "   ➤ Отправьте ссылку на JioSaavn, чтобы скачать песню."
        ),
        "Group": (
            "7️⃣ **🌟 Функциональность группы**\n"
            "   ➤ Функциональность группы будет добавлена позже."
        ),
    },
    "es": {
        "YouTube": (
            "1️⃣ **🌟 Descargar música de YouTube**\n"
            "   ➤ Envíame un enlace de YouTube, y buscaré la canción para ti."
        ),
        "Spotify": (
            "2️⃣ **🌟 Descargar música de Spotify**\n"
            "   ➤ Comparte un enlace de una canción, lista de reproducción, álbum, programa o episodio de Spotify, "
            "y lo descargaré para ti."
        ),
        "Deezer": (
            "3️⃣ **🌟 Descargar música de Deezer**\n"
            "   ➤ Proporciona un enlace de una lista de reproducción, álbum o canción de Deezer, y yo me encargaré del resto."
        ),
        "Soundcloud": (
            "4️⃣ **🌟 Descargar música de Soundcloud**\n"
            "   ➤ Envía un enlace de una canción de Soundcloud, y obtendré la canción para ti."
        ),
        "Instagram": (
            "5️⃣ **🌟 Descargar Reels de Instagram**\n"
            "   ➤ Comparte un enlace de Instagram, y descargaré el reel, publicación o historia para ti."
        ),
        "JioSaavn": (
            "6️⃣ **🌟 Descargar música de JioSaavn**\n"
            "   ➤ Envía un enlace de JioSaavn para descargar la canción."
        ),
        "Group": (
            "7️⃣ **🌟 Funcionalidad de grupo**\n"
            "   ➤ La funcionalidad de grupo se agregará más tarde."
        ),
    },
    "ar": {
        "YouTube": (
            "1️⃣ **🌟 تنزيل الموسيقى من YouTube**\n"
            "   ➤ أرسل لي رابط YouTube، وسأحضر الأغنية لك."
        ),
        "Spotify": (
            "2️⃣ **🌟 تنزيل الموسيقى من Spotify**\n"
            "   ➤ شارك رابط أغنية، قائمة تشغيل، ألبوم، عرض أو حلقة من Spotify، "
            "وسأقوم بتنزيلها لك."
        ),
        "Deezer": (
            "3️⃣ **🌟 تنزيل الموسيقى من Deezer**\n"
            "   ➤ قدم رابط قائمة تشغيل، ألبوم أو أغنية من Deezer، وسأقوم بالباقي."
        ),
        "Soundcloud": (
            "4️⃣ **🌟 تنزيل الموسيقى من Soundcloud**\n"
            "   ➤ أرسل رابط أغنية من Soundcloud، وسأحضر الأغنية لك."
        ),
        "Instagram": (
            "5️⃣ **🌟 تنزيل رييلز Instagram**\n"
            "   ➤ شارك رابط Instagram، وسأقوم بتنزيل الريل، المنشور أو القصة لك."
        ),
        "JioSaavn": (
            "6️⃣ **🌟 تنزيل الموسيقى من JioSaavn**\n"
            "   ➤ أرسل رابط JioSaavn لتنزيل الأغنية."
        ),
        "Group": (
            "7️⃣ **🌟 وظائف المجموعة**\n"
            "   ➤ سيتم إضافة وظائف المجموعة لاحقًا."
        ),
    },
    "hi": {
        "YouTube": (
            "1️⃣ **🌟 YouTube से संगीत डाउनलोड करें**\n"
            "   ➤ मुझे एक YouTube लिंक भेजें, और मैं आपके लिए गाना लेकर आऊंगा।"
        ),
        "Spotify": (
            "2️⃣ **🌟 Spotify से संगीत डाउनलोड करें**\n"
            "   ➤ एक Spotify ट्रैक, प्लेलिस्ट, एल्बम, शो या एपिसोड लिंक साझा करें, "
            "और मैं इसे आपके लिए डाउनलोड कर दूंगा।"
        ),
        "Deezer": (
            "3️⃣ **🌟 Deezer से संगीत डाउनलोड करें**\n"
            "   ➤ एक Deezer प्लेलिस्ट, एल्बम या ट्रैक लिंक प्रदान करें, और मैं बाकी का काम करूंगा।"
        ),
        "Soundcloud": (
            "4️⃣ **🌟 Soundcloud से संगीत डाउनलोड करें**\n"
            "   ➤ एक Soundcloud ट्रैक लिंक भेजें, और मैं आपके लिए गाना लेकर आऊंगा।"
        ),
        "Instagram": (
            "5️⃣ **🌟 Instagram रील्स डाउनलोड करें**\n"
            "   ➤ एक Instagram लिंक साझा करें, और मैं रील, पोस्ट या स्टोरी आपके लिए डाउनलोड कर दूंगा।"
        ),
        "JioSaavn": (
            "6️⃣ **🌟 JioSaavn से संगीत डाउनलोड करें**\n"
            "   ➤ गाना डाउनलोड करने के लिए एक JioSaavn लिंक भेजें।"
        ),
        "Group": (
            "7️⃣ **🌟 ग्रुप कार्यक्षमता**\n"
            "   ➤ ग्रुप कार्यक्षमता बाद में जोड़ी जाएगी।"
        ),
    },
}

# Help message
HELP = {
    "YouTube": (
        "1️⃣ **🌟 Download Music from YouTube**\n"
        "   ➤ Send me a YouTube link, and I’ll fetch the song for you."
    ),
    "Spotify": (
        "2️⃣ **🌟 Download Music from Spotify**\n"
        "   ➤ Share a Spotify track, playlist, album, show, or episode link, "
        "and I'll download it for you."
    ),
    "Deezer": (
        "3️⃣ **🌟 Download Music from Deezer**\n"
        "   ➤ Provide a Deezer playlist, album, or track link, and I'll handle the rest."
    ),
    "Soundcloud": (
        "4️⃣ **🌟 Download Music from Soundcloud**\n"
        "   ➤ Send a Soundcloud track link, and I’ll get the song for you."
    ),
    "Instagram": (
        "5️⃣ **🌟 Download Instagram Reels**\n"
        "   ➤ Share an Instagram link, and I’ll download the reel, post, or story for you."
    ),
    "JioSaavn": (
        "6️⃣ **🌟 Download Music from JioSaavn**\n"
        "   ➤ Send a JioSaavn link to download the song."
    ),
    "Group": (
        "7️⃣ **🌟 Group Functionality**\n"
        "   ➤ Group functionality will be added later."
    ),
}

@Mbot.on_message(filters.command("help"))
@maintenance_check
async def help(_, message):
    user_lang = get_user_language(message.from_user.id)  # Fetch the user's preferred language
    responses = HELP_TEXT.get(user_lang, HELP_TEXT["en"])  # Default to English if not found

    if message.from_user.id in banned_users:
        await message.reply_text(
            GREET_RESPONSES.get(user_lang, {}).get("banned", "You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) ")
        )
        return
    await message.delete()
    
    greeting_text = GREET_RESPONSES.get(user_lang, {}).get("greeting", "👋😊Hello {name}, I'm 𝓩𝓟𝓞𝓣𝓘𝓕𝓨.\nI'm Here to download your music.")
    greeting_text = greeting_text.format(name=message.from_user.first_name)  # Format the message correctly

    button = [
        [InlineKeyboardButton(text=i, callback_data=f"help_{i}")] for i in HELP
    ]
    button.append([InlineKeyboardButton(text="❌", callback_data="close")])

    await message.reply_text(greeting_text, reply_markup=InlineKeyboardMarkup(button))

@Mbot.on_callback_query(filters.regex(r"backdome"))
async def backdo(_, query):
    user_lang = get_user_language(query.from_user.id)  # Fetch the user's language

    button = [
        [InlineKeyboardButton(text=i, callback_data=f"help_{i}")] for i in HELP
    ]
    button.append([InlineKeyboardButton("❌ Close", callback_data="close")])

    greeting_text = GREET_RESPONSES.get(user_lang, {}).get(
        "greeting", "👋😊Hello {name}, I'm 𝓩𝓟𝓞𝓣𝓘𝓕𝓨.\nI'm Here to download your music."
    ).format(name=query.from_user.first_name)  # Format user name

    await query.message.edit(greeting_text, reply_markup=InlineKeyboardMarkup(button))
 
    
@Mbot.on_callback_query(filters.regex(r"help_(.*?)"))
async def helpbtn(_, query):
    user_lang = get_user_language(query.from_user.id)  # Get user language
    i = query.data.replace("help_", "")
    
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="helphome")]
    ])

    # Fetch translation based on user language, fallback to English if missing
    help_text = HELP_TEXT.get(user_lang, HELP_TEXT["en"]).get(i, "No help available for this topic.")

    await query.message.edit(text=help_text, reply_markup=button)


@Mbot.on_callback_query(filters.regex(r"helphome"))
async def help_home(_, query):
    user_lang = get_user_language(query.from_user.id)  # Fetch the user's preferred language

    button = [
        [InlineKeyboardButton(text=i, callback_data=f"help_{i}")] for i in HELP
    ]
    button.append([InlineKeyboardButton("❌ Close", callback_data="close")])

    greeting_text = GREET_RESPONSES.get(user_lang, {}).get(
        "greeting", "👋😊Hello {name}, I'm 𝓩𝓟𝓞𝓣𝓘𝓕𝓨.\nI'm Here to download your music."
    ).format(name=query.from_user.first_name)  # Format the string with the user's name

    await query.message.edit(greeting_text, reply_markup=InlineKeyboardMarkup(button))


@Mbot.on_callback_query(filters.regex(r"close"))
async def close(_, query):
    await query.message.delete()


################################################ Admin Panel ################################################
@Mbot.on_message(filters.command("admin") & filters.user(SUDO_USERS))
async def admin_panel(client, message):
    await message.delete()

    keyboard = [
        [
            InlineKeyboardButton("🛑 Ban Management", callback_data="ban_management"),
            InlineKeyboardButton("🛠️ Maintenance", callback_data="maintenance_management"),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats_management"),
            InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_management"),
        ],
        [
            InlineKeyboardButton("🌍 Environment Variables", callback_data="env_management"),
            InlineKeyboardButton("🌐 Language Management", callback_data="language_management"),
        ],
        [
            InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_bot"),
            InlineKeyboardButton("🔌 Shutdown Bot", callback_data="shutdown_bot"),
        ],
        [
            InlineKeyboardButton("📜 View Logs", callback_data="view_logs"),
            InlineKeyboardButton("💻 CPU Usage", callback_data="cpu_usage"),
        ],
        [
            InlineKeyboardButton("👥 List Users", callback_data="list_users_management"),
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("🖥️ 𝒜𝒹𝓂𝒾𝓃 𝒫𝒶𝓃𝑒𝓁\n", reply_markup=reply_markup)


@Mbot.on_callback_query(filters.regex(r"language_management"))
async def language_management_panel(client, callback_query):
    await callback_query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🌍 Set Global Language", callback_data="set_global_language"),
            InlineKeyboardButton("👤 Set User Language", callback_data="set_user_language"),
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="admin")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("🌐 Language Management:\nChoose an action:", reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"set_global_language"))
async def set_global_language(client, callback_query):
    await callback_query.answer()
    
    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang], callback_data=f"set_global_lang_{lang}")] for lang in LANGUAGES
    ]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="language_management")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("🌍 Set Global Language:\nChoose a language:", reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"set_global_lang_(.*)"))
async def handle_global_language_selection(client, callback_query):
    lang_code = callback_query.data.split("_")[3]  # Extract language code
    
    # Save the global language preference (you can store this in a global variable or a file)
    global_language = lang_code
    await callback_query.answer(f"Global language set to {LANGUAGES[lang_code]}", show_alert=True)
    await callback_query.message.edit_text(f"🌍 Global language has been set to {LANGUAGES[lang_code]}.")

@Mbot.on_callback_query(filters.regex(r"set_user_language"))
async def set_user_language(client, callback_query):
    await callback_query.answer()
    
    await callback_query.message.edit_text("👤 Set User Language:\nPlease enter the user ID and the language code (e.g., '123456789 en').")

@Mbot.on_message(filters.text & filters.user(SUDO_USERS))
async def handle_user_language_setting(client, message):
    if message.text.startswith("/"):
        return  # Ignore commands
    
    try:
        user_id, lang_code = message.text.split()
        user_id = int(user_id)
        lang_code = lang_code.lower()
        
        if lang_code not in LANGUAGES:
            await message.reply_text("⛔ Invalid language code. Please use one of the following: " + ", ".join(LANGUAGES.keys()))
            return
        
        # Save the user's language preference
        user_languages = load_user_languages()
        user_languages[str(user_id)] = lang_code
        save_user_languages(user_languages)
        
        await message.reply_text(f"👤 Language for user {user_id} has been set to {LANGUAGES[lang_code]}.")
    except ValueError:
        await message.reply_text("⛔ Invalid format. Please use 'user_id lang_code' (e.g., '123456789 en').")

@Mbot.on_callback_query(filters.regex(r"ban_management"))
async def ban_management_panel(client, callback_query):
    await callback_query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
            InlineKeyboardButton("🟢 Unban User", callback_data="unban_user"),
        ],
        [
            InlineKeyboardButton("📋 View Ban List", callback_data="view_ban_list"),
            InlineKeyboardButton("🔙 Back", callback_data="admin")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("🛑 Ban Management:\nChoose an action:", reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"maintenance_management"))
async def maintenance_management_panel(client, callback_query):
    await callback_query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("⚠️ Enable Maintenance", callback_data="maintenance_on"),
            InlineKeyboardButton("🟢 Disable Maintenance", callback_data="maintenance_off"),
        ],
        [
            InlineKeyboardButton("🚧 Check Maintenance Status", callback_data="maintenance_status"),
            InlineKeyboardButton("🔙 Back", callback_data="admin")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("🛠️ Maintenance Management:\nChoose an action:", reply_markup=reply_markup)


@Mbot.on_callback_query(filters.regex(r"stats_management"))
async def stats_management_panel(client, callback_query):
    await callback_query.answer()
    await stats(client, callback_query.message)  # Call the existing stats function

@Mbot.on_callback_query(filters.regex(r"close"))
async def close(_, query):
    await query.message.delete()

@Mbot.on_callback_query(filters.regex(r"ban_user"))
async def ban_user_callback(client, callback_query):
    await callback_query.answer("ℹ️ Usage: /ban <user id>")
    
    @Mbot.on_message(filters.user(SUDO_USERS))
    async def handle_ban_user(client, message):
        await ban_user(client, message)  # Call the existing ban_user function

@Mbot.on_callback_query(filters.regex(r"unban_user"))
async def unban_user_callback(client, callback_query):
    await callback_query.answer("ℹ️ Usage: /unban <user id>")
    
    @Mbot.on_message(filters.user(SUDO_USERS))
    async def handle_unban_user(client, message):
        await unban_user(client, message)  # Call the existing unban_user function

@Mbot.on_callback_query(filters.regex(r"view_ban_list"))
async def view_ban_list_callback(client, callback_query):
    await view_ban_list(client, callback_query.message)  # Call the existing view_ban_list function


@Mbot.on_message(filters.command("admin") & filters.user(SUDO_USERS))
async def admin_panel(client, message):
    await message.delete()

    keyboard = [
        [
            InlineKeyboardButton("🛑 Ban Management", callback_data="ban_management"),
            InlineKeyboardButton("🛠️ Maintenance", callback_data="maintenance_management"),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats_management"),
            InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_management"),
        ],
        [
            InlineKeyboardButton("🌍 Environment Variables", callback_data="env_management"),
            InlineKeyboardButton("🌐 Language Management", callback_data="language_management"),
        ],
        [
            InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_bot"),
            InlineKeyboardButton("🔌 Shutdown Bot", callback_data="shutdown_bot"),
        ],
        [
            InlineKeyboardButton("📜 View Logs", callback_data="view_logs"),
            InlineKeyboardButton("💻 CPU Usage", callback_data="cpu_usage"),
        ],
        [
            InlineKeyboardButton("👥 List Users", callback_data="list_users_management"),
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("🖥️ 𝒜𝒹𝓂𝒾𝓃 𝒫𝒶𝓃𝑒𝓁\n", reply_markup=reply_markup)


# Add the new callback functions for the commands
@Mbot.on_callback_query(filters.regex(r"restart_bot"))
async def restart_bot_callback(client, callback_query):
    await callback_query.answer("Are you sure you want to restart the bot?")
    
    keyboard = [
        [
            InlineKeyboardButton("🟢 Yes", callback_data="restart_yes"),
            InlineKeyboardButton("🔴 No", callback_data="restart_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("🔄 Restarting the bot...", reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"shutdown_bot"))
async def shutdown_bot_callback(client, callback_query):
    await callback_query.answer("Are you sure you want to shut down the bot?")
    
    keyboard = [
        [
            InlineKeyboardButton("🟢 Yes", callback_data="shutdown_yes"),
            InlineKeyboardButton("🔴 No", callback_data="shutdown_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("🔌 Shutting down the bot...", reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"view_logs"))
async def view_logs_callback(client, callback_query):
    await callback_query.answer()
    await send_log(client, callback_query.message)  # Call the existing send_log function

@Mbot.on_callback_query(filters.regex(r"cpu_usage"))
async def cpu_usage_callback(client, callback_query):
    await callback_query.answer()
    await cpu_usage(client, callback_query.message)  # Call the existing cpu_usage function


# Handle the restart confirmation
@Mbot.on_callback_query(filters.regex(r"restart_(yes|no)"))
async def handle_restart_query(_, callback_query):
    if callback_query.data == "restart_yes":
        await callback_query.message.delete()
        await callback_query.answer("Restarting bot...", show_alert=True)
        
        execvp(sys.executable, [sys.executable, "-m", "mbot"])
    elif callback_query.data == "restart_no":
        await callback_query.answer("Bot restart has been cancelled.", show_alert=True)
        await callback_query.message.delete()

# Handle the shutdown confirmation
@Mbot.on_callback_query(filters.regex(r"shutdown_(yes|no)"))
async def handle_shutdown_query(_, callback_query):
    if callback_query.data == "shutdown_yes":
        await callback_query.message.delete()
        await callback_query.answer("🔌 Shutting down bot...", show_alert=True)

        # Shutdown the bot by stopping the event loop
        await os._exit(0)
    elif callback_query.data == "shutdown_no":
        await callback_query.answer("Bot shutdown has been cancelled.", show_alert=True)
        await callback_query.message.delete()



#################################################################################################
# File path for the config.env file
CONFIG_ENV_FILE = "config.env"

# Function to load environment variables from config.env
def load_env_vars():
    env_vars = {}
    if os.path.exists(CONFIG_ENV_FILE):
        with open(CONFIG_ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore comments and empty lines
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

# Function to save environment variables to config.env
def save_env_vars(env_vars):
    with open(CONFIG_ENV_FILE, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

# Command to set environment variables
@Mbot.on_message(filters.command("setenv") & filters.user(SUDO_USERS))
async def set_env(client, message):
    await message.delete()

    if len(message.command) < 3:
        await message.reply_text("❌ Usage: /setenv (key) (value)")
        return

    key = message.command[1]
    value = " ".join(message.command[2:])

    # Load existing environment variables
    env_vars = load_env_vars()

    # Update the environment variable
    env_vars[key] = value
    save_env_vars(env_vars)

    await message.reply_text(f"✅ Environment variable `{key}` set to `{value}`.")

# Callback handler for environment variable management
@Mbot.on_callback_query(filters.regex(r"env_management"))
async def env_management_panel(client, callback_query):
    await callback_query.answer()

    keyboard = [
        [InlineKeyboardButton("📝 Edit Environment Variables", callback_data="edit_env_vars")],
        [InlineKeyboardButton("📋 View Environment Variables", callback_data="view_env_vars")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("🌍 Environment Variable Management:\nChoose an action:", reply_markup=reply_markup)

# Callback handler to view environment variables
@Mbot.on_callback_query(filters.regex(r"view_env_vars"))
async def view_env_vars(client, callback_query):
    await callback_query.answer()

    env_vars = load_env_vars()
    if not env_vars:
        await callback_query.message.edit_text("No environment variables found.")
        return

    # Create a clean and appealing format for the environment variables
    env_vars_text = "🌍 **Environment Variables** 🌍\n\n"
    for key, value in env_vars.items():
        env_vars_text += f"🔑 **{key}**:\n"
        env_vars_text += f"   📌 `{value}`\n\n"

    await callback_query.message.edit_text(env_vars_text)

# Callback handler to edit environment variables
@Mbot.on_callback_query(filters.regex(r"edit_env_vars"))
async def edit_env_vars(client, callback_query):
    await callback_query.answer()

    keyboard = [
        [InlineKeyboardButton("➕ Add New Variable", callback_data="add_env_var")],
        [InlineKeyboardButton("✏️ Edit Existing Variable", callback_data="edit_existing_var")],
        [InlineKeyboardButton("🔙 Back", callback_data="env_management")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("📝 Edit Environment Variables:\nChoose an action:", reply_markup=reply_markup)

# Callback handler to add a new environment variable
@Mbot.on_callback_query(filters.regex(r"add_env_var"))
async def add_env_var(client, callback_query):
    await callback_query.answer("ℹ️ Use /setenv <key> <value> to add a new environment variable.")
    await callback_query.message.delete()

# Callback handler to edit an existing environment variable
@Mbot.on_callback_query(filters.regex(r"edit_existing_var"))
async def edit_existing_var(client, callback_query):
    await callback_query.answer("ℹ️ Use /setenv <key> <value> to edit an existing environment variable.")
    await callback_query.message.delete()

# Update the admin panel to include environment variable management
@Mbot.on_callback_query(filters.regex(r"admin"))
async def admin_panel_callback(client, callback_query):
    await callback_query.answer()

    keyboard = [
        [
            InlineKeyboardButton("🛑 Ban Management", callback_data="ban_management"),
            InlineKeyboardButton("🛠️ Maintenance", callback_data="maintenance_management"),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats_management"),
            InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_management"),
        ],
        [
            InlineKeyboardButton("🌍 Environment Variables", callback_data="env_management"),
            InlineKeyboardButton("🌐 Language Management", callback_data="language_management"),
        ],
        [
            InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_bot"),
            InlineKeyboardButton("🔌 Shutdown Bot", callback_data="shutdown_bot"),
        ],
        [
            InlineKeyboardButton("📜 View Logs", callback_data="view_logs"),
            InlineKeyboardButton("💻 CPU Usage", callback_data="cpu_usage"),
        ],
        [
            InlineKeyboardButton("👥 List Users", callback_data="list_users_management"),
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("🖥️ 𝒜𝒹𝓂𝒾𝓃 𝒫𝒶𝓃𝑒𝓁\n", reply_markup=reply_markup)



#File paths for persisting user data
USER_LIST_FILE = "user_list.json"

# Load and save user list functions
def load_user_list():
    if os.path.exists(USER_LIST_FILE):
        with open(USER_LIST_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_user_list(user_list):
    with open(USER_LIST_FILE, "w") as f:
        json.dump(list(user_list), f)

# Initialize user list
user_list = load_user_list()

# Broadcast command
@Mbot.on_message(filters.command("broadcast") & filters.user(SUDO_USERS))
async def broadcast_message(client, message):
    await message.delete()

    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /broadcast <message>")
        return

    broadcast_text = message.text.split(None, 1)[1]
    failed = 0

    await message.reply_text(f"Broadcast initiated. Sending message to {len(user_list)} users...")

    for user_id in user_list:
        try:
            await client.send_message(chat_id=user_id, text=broadcast_text)
            await sleep(0.1)  # Slow down to prevent API flood
        except Exception:
            failed += 1

    await message.reply_text(
        f"✅ Broadcast complete. Delivered to {len(user_list) - failed} users. Failed: {failed} users."
    )


    
    # Add callback handler for broadcast
@Mbot.on_callback_query(filters.regex(r"broadcast_management"))
async def broadcast_management_panel(client, callback_query):
    await callback_query.answer()

    keyboard = [
        [InlineKeyboardButton("📢 Send Broadcast", callback_data="send_broadcast")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("📢 Broadcast Management:\nChoose an action:", reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"send_broadcast"))
async def prompt_broadcast(client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text("ℹ️ Use /broadcast <message> to send a broadcast message.")
    await callback_query.message.delete()


@Mbot.on_message(filters.command("list_users") & filters.user(SUDO_USERS))
async def list_users(client, message):
    await message.delete()
    
    # Create inline buttons for HTML or plain message
    keyboard = [
        [
            InlineKeyboardButton("💬 Send as Message", callback_data="send_as_message"),
            InlineKeyboardButton("｡🇯‌🇸‌ Send as Json", callback_data="send_as_json"),
        ],
        [   InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("🗄️ Choose how to send the user list:", reply_markup=reply_markup)

import json

@Mbot.on_callback_query(filters.regex(r"send_as_(message|html|json|log)"))
async def send_user_list(client, callback_query):
    await callback_query.answer()
    
    format_type = callback_query.data.split("_")[-1]  # Get 'message', 'html', 'json', or 'log'
    
    # Load user list
    user_list = load_user_list()
    
    if not user_list:
        await callback_query.message.edit_text("No users found.")
        return
    
    user_details = []
    for user_id in user_list:
        try:
            user = await client.get_users(user_id)
            user_details.append({
                "id": user.id,
                "name": user.first_name,
                "username": user.username if user.username else "N/A"
            })
        except Exception as e:
            user_details.append({
                "id": user_id,
                "name": "N/A",
                "username": "N/A",
                "error": str(e)
            })
    
    if format_type == "message":
        user_list_text = "\n".join([
    f"➤ <b>🆔:</b> <code>{u['id']}</code>\n"
    f"    🏷️ <b>Name:</b> <i>{u['name']}</i>\n"
    f"    🌐 <b>Username:</b> @{u['username'] if u['username'] != 'N/A' else 'N/A'}\n"
    f"   ───────────────────────────"  # Separator line
    for u in user_details
])

        await callback_query.message.reply_text(
        f"<b>🗄️ User List:</b>\n\n{user_list_text}",
        
)
    elif format_type == "html":
        user_list_html = "\n".join([
    f"➤ <b>🆔:</b> <code>{u['id']}</code>\n"
    f"    📛 <b>Name:</b> <i>{u['name']}</i>\n"
    f"    🌐 <b>Username:</b> @{u['username'] if u['username'] != 'N/A' else 'N/A'}\n"
    f"   ───────────────────────────"  # Separator line
    for u in user_details
])
        await callback_query.message.reply_text(
            f"<b>User List:</b><br>{user_list_html}",
            parse_mode="HTML"
        )
    elif format_type in {"json", "log"}:
        # Create the file content
        file_content = json.dumps(user_details, indent=4) if format_type == "json" else "\n".join(
            [f"ID: {u['id']}, Name: {u['name']}, Username: @{u['username']}" for u in user_details]
        )
        
        # Determine file name and type
        file_name = "user_list.json" if format_type == "json" else "user_list.log"
        file_path = f"/tmp/{file_name}"
        
        # Write to file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(file_content)
        
        # Send the file
        await client.send_document(
            chat_id=callback_query.message.chat.id,
            document=file_path,
            caption=f"🗄️Here is the user list as a {format_type.upper()} file."
        )



@Mbot.on_callback_query(filters.regex(r"list_users_management"))
async def list_users_management_panel(client, callback_query):
    await callback_query.answer()
    await list_users(client, callback_query.message)  # Call the existing list_users function


@Mbot.on_callback_query(filters.regex(r"change_language"))
async def change_language(client, callback_query):
    await callback_query.answer()
    
    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang], callback_data=f"set_user_lang_{lang}")] for lang in LANGUAGES
    ]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="settings")])  # Go back to settings

    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text(
        "🌐 Change Language:\nChoose your preferred language:", reply_markup=reply_markup
    ) 

@Mbot.on_callback_query(filters.regex(r"settings"))
async def settings_menu(client, callback_query):
    user_lang = get_user_language(callback_query.from_user.id)  # Fetch the user's language
    
    # Define the settings menu buttons
    keyboard = [
        [InlineKeyboardButton("🌐 Change Language", callback_data="change_language")],
        [InlineKeyboardButton("❌ Close", callback_data="close")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Retrieve and format the settings text
    settings_text = GREET_RESPONSES.get(user_lang, {}).get(
        "settings", "⚙️ **Settings Menu**\nChoose an option below:"
    )

    await callback_query.message.edit_text(settings_text, reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"set_user_lang_(.*)"))
async def handle_user_language_change(client, callback_query):
    lang_code = callback_query.data.split("_")[3]  # Extract language code
    user_id = str(callback_query.from_user.id)
    
    # Save the user's language preference
    user_languages = load_user_languages()
    user_languages[user_id] = lang_code
    save_user_languages(user_languages)
    
    # Initial confirmation message
    countdown_text = f"🌐 Your language has been set to {LANGUAGES[lang_code]}. This message will disappear in"
    confirmation_message = await callback_query.message.edit_text(f"{countdown_text} 3 seconds...")

    # Countdown loop
    for i in range(2, 0, -1):  # Start from 2 to avoid the first edit being identical
        await asyncio.sleep(1)  # Wait for 1 second
        await confirmation_message.edit_text(f"{countdown_text} {i} seconds...")

    # Wait another second and delete the message
    await asyncio.sleep(1)
    await confirmation_message.delete()

    