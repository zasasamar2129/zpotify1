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
from mbot.utils.focus_manager import set_focus, clear_focus, is_focused
MAINTENANCE_FILE = "maintenance_status.json"
BAN_LIST_FILE = "banned_users.json"
USER_LIST_FILE = "user_list.json"

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
            await message.reply_text("🚧 The bot is under maintenance. Please try again later.")
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


@Mbot.on_message(filters.command("settings"))
@maintenance_check
async def settings(client, message):
    await message.delete()
    await message.reply_text("🔜 We will add this feature. Stay tuned @Zpotify1(News)")

@Mbot.on_message(filters.command("start"))
@maintenance_check
async def start(client, message):
    await message.delete()
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) .")
        return

        # Add user to the user list
    user_list.add(message.from_user.id)
    save_user_list(user_list)  # Save the updated user list

    await message.delete()
    reply_markup = [
        [
            InlineKeyboardButton(
                text=" 🌐 Bot Channel", url="https://t.me/Zpotify1"),
            InlineKeyboardButton(
                text="⛓️‍💥 Repo",
                url="https://github.com/zasasamar2129/zpotify1"),
            InlineKeyboardButton(text="❓Help", callback_data="helphome")
        ],
        [
            InlineKeyboardButton(text="💖 Donate",
            url="https://www.buymeacoffee.com/zasasamar"),
        ]
    ]
    
    if LOG_GROUP:
        invite_link = await client.create_chat_invite_link(chat_id=(int(LOG_GROUP) if str(LOG_GROUP).startswith("-100") else LOG_GROUP))
        reply_markup.append([InlineKeyboardButton("🗃️ LOG Channel", url=invite_link.invite_link)])
    
    reply_markup.append([InlineKeyboardButton(text="❌", callback_data="close")])
    
    return await message.reply_text(f"👋 Hello {message.from_user.first_name}, I'm  𝓩𝓟𝓞𝓣𝓘𝓕𝓨. a music downloader bot that supports Download from Youtube,Spotify,Soundcloud,Deezer and more.",
                    reply_markup=InlineKeyboardMarkup(reply_markup))

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

@Mbot.on_message(filters.command("cpu") & filters.chat(SUDO_USERS))
async def cpu_usage(_, message):
    await message.delete()
    cpu_percent = psutil.cpu_percent(interval=1)
    await message.reply_text(f"**CPU Usage:** `{cpu_percent}%`")

@Mbot.on_message(filters.command("ping"))
@maintenance_check
async def ping(client, message):
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) .")
        return
    start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    ms = (datetime.now() - start).microseconds / 1000
    await message.reply_text(f"**Pong!**\nResponse time: `{ms} ms`")

@Mbot.on_message(filters.command("donate"))
@maintenance_check
async def donate(_, message):
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) .")
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Donate", url="https://www.buymeacoffee.com/zasasamar")],
        [InlineKeyboardButton(text="❌", callback_data="close")]
    ])
    await message.reply_text("If you would like to support the development of this bot, you can donate here:", reply_markup=keyboard)

@Mbot.on_message(filters.command("info"))
@maintenance_check
async def info(_, message):
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) .")
        return
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
    await message.reply_text(info_text)

@Mbot.on_message(filters.command("stats"))
@maintenance_check
async def stats(client, message):
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) .")
        return
    # Initial reply with a placeholder message
    fetching_message = await message.reply_text("Fetching stats...\n[                    ] 0%")
    
    # Simulate progress by updating the message incrementally
    for progress in range(0, 101, 10):
        bar = "█" * (progress // 10) + " " * (10 - (progress // 10))
        await fetching_message.edit_text(f"Fetching stats...\n[{bar}] {progress}%")
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
    await message.reply_text(stats_text)

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
    if message.from_user.id in banned_users:
        await message.reply_text("You are banned from using this bot  ദ്ദി ༎ຶ‿༎ຶ ) .")
        return
    await message.delete()
    button = [
        [InlineKeyboardButton(text=i, callback_data=f"help_{i}")] for i in HELP
    ]
    button.append([InlineKeyboardButton(text="❌", callback_data="close")])
    await message.reply_text(f"👋😊Hello **{message.from_user.first_name}**, I'm **𝓩𝓟𝓞𝓣𝓘𝓕𝓨**.\nI'm Here to download your music.",
                        reply_markup=InlineKeyboardMarkup(button))
                        
@Mbot.on_callback_query(filters.regex(r"backdome"))
async def backdo(_, query):
    button = [
        [InlineKeyboardButton(text=i, callback_data=f"help_{i}")] for i in HELP
    ]
    button.append([InlineKeyboardButton(text="❌", callback_data="close")])
    await query.message.edit(f"👋😊Hello **{query.message.from_user.first_name}**, I'm **𝓩𝓟𝓞𝓣𝓘𝓕𝓨**.\nI'm Here to download your music.",
                        reply_markup=InlineKeyboardMarkup(button))     
    
@Mbot.on_callback_query(filters.regex(r"help_(.*?)"))
async def helpbtn(_, query):
    i = query.data.replace("help_", "")
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="helphome")]
    ])
    text = f"Help for **{i}**\n\n{HELP[i]}"
    await query.message.edit(text=text, reply_markup=button)

@Mbot.on_callback_query(filters.regex(r"helphome"))
async def help_home(_, query):
    button = [
        [InlineKeyboardButton(text=i, callback_data=f"help_{i}")] for i in HELP
    ]
    button.append([InlineKeyboardButton(text="❌", callback_data="close")])
    await query.message.edit(f"👋😊Hello **{query.from_user.first_name}**, I'm **𝓩𝓟𝓞𝓣𝓘𝓕𝓨**.\nI'm Here to download your music.",
                        reply_markup=InlineKeyboardMarkup(button))

@Mbot.on_callback_query(filters.regex(r"close"))
async def close(_, query):
    await query.message.delete()


################################################ Admin Panel ################################################
@Mbot.on_message(filters.command("admin") & filters.user(SUDO_USERS))
async def admin_panel(client, message):
    await message.delete()
    
    keyboard = [
        [
            InlineKeyboardButton("🔨 Ban Management", callback_data="ban_management"),
            InlineKeyboardButton("🛠️ Maintenance", callback_data="maintenance_management"),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats_management"),
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("👮‍♂️ Admin Panel:\nChoose a category:", reply_markup=reply_markup)

@Mbot.on_callback_query(filters.regex(r"ban_management"))
async def ban_management_panel(client, callback_query):
    await callback_query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
            InlineKeyboardButton("🔓 Unban User", callback_data="unban_user"),
        ],
        [
            InlineKeyboardButton("📋 View Ban List", callback_data="view_ban_list"),
            InlineKeyboardButton("🔙 Back", callback_data="admin")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("🔨 Ban Management:\nChoose an action:", reply_markup=reply_markup)

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
    await callback_query.answer("Please reply to a user's message or send their user ID to ban.")
    
    @Mbot.on_message(filters.user(SUDO_USERS))
    async def handle_ban_user(client, message):
        await ban_user(client, message)  # Call the existing ban_user function

@Mbot.on_callback_query(filters.regex(r"unban_user"))
async def unban_user_callback(client, callback_query):
    await callback_query.answer("Please send the user ID to unban.")
    
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
            InlineKeyboardButton("🔨 Ban Management", callback_data="ban_management"),
            InlineKeyboardButton("🛠️ Maintenance", callback_data="maintenance_management"),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats_management"),
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
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("👮‍♂️ Admin Panel:\nChoose a category:", reply_markup=reply_markup)

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
@Mbot.on_callback_query(filters.regex(r"admin"))
async def go_back_to_admin_panel(client, callback_query):
    await callback_query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🔨 Ban Management", callback_data="ban_management"),
            InlineKeyboardButton("🛠️ Maintenance", callback_data="maintenance_management"),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats_management"),
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
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_text("👮‍♂️ Admin Panel:\nChoose a category:", reply_markup=reply_markup)
