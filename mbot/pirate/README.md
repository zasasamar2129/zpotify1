# Xtract-Pirate-Bot 🏴‍☠️

<div align="center">
  <img src="assets/banner.png" alt="Xtract-Pirate-Bot Banner" width="100%">
</div>

A versatile Telegram bot that can download media content from various social media platforms. Supports YouTube, Instagram, Reddit, Pinterest, and Spotify. Arrr! Let's plunder some content! 🦜

<!-- <div align="center">
  <img src="assets/demo.gif" alt="Bot Demo" width="70%">
</div> -->

## Features

- **Multi-Platform Support** 🌐
  <!-- <img src="assets/platforms.png" alt="Supported Platforms" align="right" width="40%"> -->
  
 
  
  

  -   <img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/filled/youtube.svg" alt="Supported Platforms" width="3%"> YouTube videos and shorts
  -  <img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/filled/instagram.svg" alt="Supported Platforms" width="3%"> Instagram posts, reels, and stories
  -   <img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/filled/reddit.svg" alt="Supported Platforms" width="3%"> Reddit posts and comments
  - <img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/filled/pinterest.svg" alt="Supported Platforms" width="3%"> Pinterest pins and boards 
  - <img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/filled/spotify.svg" alt="Supported Platforms" width="3%"> Spotify songs and playlists

- **Advanced Features** ⚡
  - Multiple quality options for video downloads
  - Batch downloads from playlists/collections
  - Progress updates during downloads
  - Download history tracking
  - Usage statistics
  - Organized folder structure
  - Automatic file cleanup

<!-- ## Demo

<div align="center">
  <img src="assets/usage.png" alt="Usage Example" width="80%">
</div> -->

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Rahul-Sahani04/Xtract-Pirate-Bot.git
cd Xtract-Pirate-Bot
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   <!-- <img src="assets/env-setup.png" alt="Environment Setup" align="right" width="40%"> -->
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your API credentials:
     - Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
     - Instagram credentials (optional, for private content)
     - Reddit API credentials (from [Reddit Apps](https://www.reddit.com/prefs/apps))
     - Spotify API credentials (from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard))

4. Configure download settings in `.env` (optional):
   ```bash
   # Download Settings
   MAX_DOWNLOADS=10       # Maximum items in batch/playlist
   DOWNLOAD_TIMEOUT=300   # Timeout in seconds
   CLEANUP_AFTER_SEND=true # Delete files after sending
   ```

5. Run the bot:
```bash
python bot.py
```

## Usage

<div align="center">
  <img src="assets/commands.png" alt="Bot Commands" width="80%">
</div>

1. Start the bot in Telegram: `/start`
2. Send any supported URL to download content
3. Select quality options if prompted
4. Wait for your download

### Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/stats` - Show download statistics
- `/history` - View download history
- `/settings` - Configure download preferences

## Supported URL Formats

### YouTube
<img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/colored/youtube.svg" alt="YouTube Support" align="right" width="30%">

- Regular videos: `https://www.youtube.com/watch?v=VIDEO_ID`
- Shorts: `https://www.youtube.com/shorts/VIDEO_ID`
- Playlists: `https://www.youtube.com/playlist?list=PLAYLIST_ID`

### Instagram
<img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/colored/instagram.svg" alt="Instagram Support" align="right" width="30%">

- Posts (regular): `https://www.instagram.com/p/POST_ID/`
- Pins (short URL): `https://pin.it/SHORTCODE`
- Boards: `https://www.pinterest.com/USERNAME/BOARD_NAME/`

### Reddit
<img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/colored/reddit.svg" alt="Reddit Support" align="right" width="30%">
- Posts: `https://www.reddit.com/r/SUBREDDIT/comments/POST_ID/`
- Subreddits: `https://www.reddit.com/r/SUBREDDIT/`

### Pinterest
<img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/colored/pinterest.svg" alt="Pinterest Support" align="right" width="30%">

- Pins (regular): `https://www.pinterest.com/pin/PIN_ID/`
- Pins (short URL): `https://pin.it/SHORTCODE`
- Boards: `https://www.pinterest.com/USERNAME/BOARD_NAME/`

### Spotify
<img src="https://raw.githubusercontent.com/CLorant/readme-social-icons/main/large/colored/spotify.svg" alt="Spotify Support" align="right" width="30%">

- Tracks: `https://open.spotify.com/track/TRACK_ID`
- Playlists: `https://open.spotify.com/playlist/PLAYLIST_ID`
- Albums: `https://open.spotify.com/album/ALBUM_ID`

## API Requirements

<!-- <div align="center">
  <img src="assets/api-setup.png" alt="API Setup" width="80%">
</div> -->

1. **Telegram Bot API**
   - Create a bot through [@BotFather](https://t.me/BotFather)
   - Get the bot token and add it to `.env` as `BOT_TOKEN`
   - No rate limits for bot API tokens

2. **Instagram** (Optional, for private content)
   - Personal account credentials
   - Add to `.env` as `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`
   - No official API used, uses web scraping
   - Be cautious with rate limits

3. **Reddit API**
   - Create an app at [Reddit Apps](https://www.reddit.com/prefs/apps)
   - Get client ID and client secret
   - Add to `.env` as `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
   - Rate limits: 60 requests/minute

4. **Pinterest**
   - No official API required
   - Uses web scraping
   - Be mindful of rate limits

5. **Spotify API**
   - Create an app in [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Get client ID and client secret
   - Add to `.env` as `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
   - Rate limits: Varies by endpoint

## Configuration

<div align="center">
  <img src="assets/config.png" alt="Configuration" width="80%">
</div>

All configuration is managed through environment variables in the `.env` file:

```bash
# Telegram Bot Token
BOT_TOKEN=your_bot_token_here

# Instagram Credentials (Optional)
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent

# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# Download Settings
MAX_DOWNLOADS=10
DOWNLOAD_TIMEOUT=300
CLEANUP_AFTER_SEND=true
```

## Contributing

<!-- <div align="center">
  <img src="assets/contribute.png" alt="Contributing" width="60%">
</div> -->

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Author

<div align="center">
  <img src="assets/PirateCatLogo.jpeg" alt="Author" width="200px" style="border-radius: 50%;">
</div>

👨‍💻 **Rahul Sahani**
- GitHub: [@Rahul-Sahani04](https://github.com/Rahul-Sahani04)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational purposes only. Be sure to comply with each platform's terms of service and API usage guidelines. The developers are not responsible for any misuse of this bot.

<!-- <div align="center">
  <img src="assets/footer.png" alt="Footer" width="100%">
</div> -->