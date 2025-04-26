<div align="center">
  <a href="https://github.com/zasasamar2129/zpotify1">
    <kbd>
      <img width="250" src="https://files.catbox.moe/ppbwe6.jpg" alt="ZPOTIFY Logo">
    </kbd>
  </a>

## **𝒵𝒫𝒪𝒯𝐼𝐹𝒴** 🎶
</div>

---

# Spotify Downloader Bot

[![Demo Bot](https://img.shields.io/badge/Try%20it%20out-%40z_downloadbot-blue?style=for-the-badge&logo=telegram)](https://t.me/z_downloadbot)

## 🌟 About
ZPOTIFY is a powerful and open-source Spotify downloader bot designed for Telegram. It offers an easy and efficient way to download your favorite tracks from Spotify with additional features planned for continuous improvement. While inspired by [@NeedMusicRobot](https://github.com/rozari0/NeedMusicRobot), ZPOTIFY is a completely independent project with unique features.

---

## 🚀 Deployment

### Local/VPS Deployment
1. **Install Dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y && sudo apt install git ffmpeg python3 python3-pip -y
   ```
2. **Clone Repository & Install Requirements:**
   ```bash
   git clone https://github.com/zasasamar2129/zpotify1.git
   cd zpotify1
   pip3 install -r requirements.txt
   ```
3. **Install Requirements 2:**
   ```bash
   cd mbot/pirate
   pip3 install -r requirements.txt
   ```
4. **Run the Bot:**
   ```bash
   cd ../../
   python3 -m mbot
   ```

### Docker Deployment
1. **Build and Run the Docker Image:**
   ```bash
   docker build . -t musicbot
   docker run musicbot
   ```

---

## 🔧 Configuration
Add these variables in [config.env](https://github.com/zasasamar2129/zpotify1/blob/Latest/config.env):

### Required Environment Variables
```env
API_ID = ""                # Get this from https://my.telegram.org
API_HASH = ""              # Get this from https://my.telegram.org
BOT_TOKEN = ""             # Your bot token
OWNER_ID = ""              # Your Telegram ID
SPOTIPY_CLIENT_ID = ""     # Get this from developers.spotify.com
SPOTIPY_CLIENT_SECRET = "" # Get this from developers.spotify.com
```

### Optional Environment Variables
```env
SUDO_USERS = ""                # Space-separated user IDs with admin permissions
AUTH_CHATS = ""                # Space-separated chat IDs allowed to use the bot
LOG_GROUP = ""                 # ID of a log group (optional)
BUG = ""                       # Error log group ID (optional)
GENIUS_API = ""                # Genius API key (optional)
XDG_CACHE_HOME = "~/.tmp"      # Temporary file storage path (optional)
FIXIE_SOCKS_HOST = ""          # Proxy URL (optional)
F_SUB = False                  # Enable forced subscription (default: False)
F_SUB_CHANNEL_ID = ""          # Channel ID for forced subscription (optional)
F_SUB_CHANNEL_INVITE_LINK = "" # Channel invite link for forced subscription (optional)
```

---

## 💡 Features
- 🎵 **High-Quality Downloads**
- 🚀 **Fast and Reliable**
- 🔄 **Playlist Support**
- 🛠️ **Customizable via Environment Variables**
- 📜 **Error Logging**
- 🔒 **Secure Configuration**
- 💎 **Admin Panel**
---

## 🍕 Support
If you find this project useful, please consider buying me a pizza! 🍕

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Pizza-BrightGreen?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/zasasamar)

---

## 📢 Feedback
We value your input! Share your feedback and rate the bot:

[![Feedback](https://img.shields.io/badge/Feedback-Rate%20Our%20Bot-yellow?style=for-the-badge&logo=telegram)](https://t.me/dailychannelsbot?start=z_downloadbot)

---

## 📞 Contact
Need help or have suggestions? Reach out:
- [Instagram](https://instagram.com/zaco.game)
- [Telegram](https://t.me/Itachi2129)

---

## 🌐 Community
Join our community for updates and support:

[![Join Telegram Channel](https://img.shields.io/badge/Join%20Telegram%20Channel-1DA1F2?style=for-the-badge&logo=telegram)](https://t.me/dailychannelsbot?start=z_downloadbot)

---

## 📜 License
This project is licensed under the [Apache License 2.0](LICENSE).

