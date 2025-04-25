import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / "downloads"

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Platform-specific download paths
YOUTUBE_DOWNLOAD_PATH = str(DOWNLOADS_DIR / "youtube")
INSTAGRAM_DOWNLOAD_PATH = str(DOWNLOADS_DIR / "instagram")
REDDIT_DOWNLOAD_PATH = str(DOWNLOADS_DIR / "reddit")
PINTEREST_DOWNLOAD_PATH = str(DOWNLOADS_DIR / "pinterest")
SPOTIFY_DOWNLOAD_PATH = str(DOWNLOADS_DIR / "spotify")

# Instagram Credentials (Optional)
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Reddit API Credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Spotify API Credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Download Settings
MAX_DOWNLOADS = int(os.getenv("MAX_DOWNLOADS", "10"))
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", "300"))
CLEANUP_AFTER_SEND = os.getenv("CLEANUP_AFTER_SEND", "true").lower() == "true"

# Supported Formats
SUPPORTED_VIDEO_FORMATS = ['mp4', 'webm']
SUPPORTED_AUDIO_FORMATS = ['mp3', 'm4a', 'wav']
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit for Telegram

# Storage Settings
HISTORY_FILE = str(BASE_DIR / "download_history.json")

# Health API Settings
HEALTH_API_HOST = os.getenv("HOST", "0.0.0.0")
HEALTH_API_PORT = int(os.getenv("PORT", "8080"))

# Validate required environment variables
required_vars = [
    ("BOT_TOKEN", "Telegram Bot Token"),
    ("REDDIT_CLIENT_ID", "Reddit Client ID"),
    ("REDDIT_CLIENT_SECRET", "Reddit Client Secret"),
    ("SPOTIFY_CLIENT_ID", "Spotify Client ID"),
    ("SPOTIFY_CLIENT_SECRET", "Spotify Client Secret"),
]

missing_vars = []
for var, name in required_vars:
    if not os.getenv(var):
        missing_vars.append(name)

if missing_vars:
    raise ValueError(
        "Missing required environment variables:\n" +
        "\n".join(f"- {var}" for var in missing_vars) +
        "\nPlease check your .env file"
    )