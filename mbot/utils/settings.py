# Path: /mnt/data/spotify.py

import json
import
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

SETTINGS_FILE = "user_settings.json"

# Load user settings
def load_user_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

# Save user settings
def save_user_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# Load settings on startup
user_settings = load_user_settings()

@Mbot.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    user_id = str(message.from_user.id)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP3", callback_data="set_mp3"),
         InlineKeyboardButton("M4A", callback_data="set_m4a"),
         InlineKeyboardButton("FLAC", callback_data="set_flac")]
    ])
    current_setting = user_settings.get(user_id, "Not Set")
    await message.reply_text(
        f"Your current audio format is: **{current_setting}**\nChoose your preferred format:",
        reply_markup=keyboard
    )

@Mbot.on_callback_query(filters.regex(r"set_(mp3|m4a|flac)"))
async def set_audio_format(client, query):
    user_id = str(query.from_user.id)
    format_choice = query.data.split("_")[1].upper()
    
    user_settings[user_id] = format_choice
    save_user_settings(user_settings)
    
    await query.message.edit_text(f"Audio format set to: **{format_choice}**")
    await query.answer("Settings updated!")

# Modify the music sending logic
async def send_music(client, user_id, track_path, track_info):
    preferred_format = user_settings.get(str(user_id), "MP3")  # Default to MP3
    converted_path = convert_audio(track_path, preferred_format)  # Implement conversion logic
    
    await client.send_audio(
        chat_id=user_id,
        audio=converted_path,
        title=track_info["title"],
        performer=track_info["artist"],
        caption=f"{track_info['title']} - {track_info['artist']}"
    )

def convert_audio(input_path, output_format):
    # Add actual conversion logic using libraries like ffmpeg
    output_path = input_path.replace(".flac", f".{output_format.lower()}")
    # Simulating conversion; replace with actual implementation
    return output_path
