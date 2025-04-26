import logging
import asyncio
import signal
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import psutil
import json
from pathlib import Path
from aiohttp import web

from telegram import Update, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

import config
from utils import URLValidator, DownloadTracker, FileManager, ProgressTracker
from downloaders import (
    YouTubeDownloader, InstagramDownloader, RedditDownloader,
    PinterestDownloader, SpotifyDownloader
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot state
startup_time = datetime.now()

# Initialize downloaders
#youtube_dl = YouTubeDownloader(download_path=config.YOUTUBE_DOWNLOAD_PATH)
instagram_dl = InstagramDownloader(download_path=config.INSTAGRAM_DOWNLOAD_PATH)
reddit_dl = RedditDownloader(
    client_id=config.REDDIT_CLIENT_ID,
    client_secret=config.REDDIT_CLIENT_SECRET,
    user_agent=config.REDDIT_USER_AGENT,
    download_path=config.REDDIT_DOWNLOAD_PATH
)
pinterest_dl = PinterestDownloader(download_path=config.PINTEREST_DOWNLOAD_PATH)
#spotify_dl = SpotifyDownloader(
    #client_id=config.SPOTIFY_CLIENT_ID,
    #client_secret=config.SPOTIFY_CLIENT_SECRET,
    #download_path=config.SPOTIFY_DOWNLOAD_PATH
#)

# Initialize download tracker
download_tracker = DownloadTracker(config.HISTORY_FILE)



async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show download history when the command /history is issued."""
    history = await download_tracker.get_history(limit=10)
    
    if not history:
        await update.message.reply_text("No download history available.")
        return

    message = "📥 Recent Downloads:\n\n"
    for item in reversed(history):
        status = "✅" if item.get('success') else "❌"
        message += (
            f"{status} {item.get('title', 'Unknown')}\n"
            f"Platform: {item.get('platform', 'Unknown')}\n"
            f"Date: {datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M')}\n\n"
        )
    
    await update.message.reply_text(message)

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings options when the command /settings is issued."""
    keyboard = [
        [
            InlineKeyboardButton("Video Quality", callback_data="settings_video_quality"),
            InlineKeyboardButton("Audio Quality", callback_data="settings_audio_quality")
        ],
        [
            InlineKeyboardButton("Download Path", callback_data="settings_download_path"),
            InlineKeyboardButton("Auto-Delete", callback_data="settings_auto_delete")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚙️ Settings:", reply_markup=reply_markup)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URLs sent to the bot."""
    url = update.message.text
    status_message = await update.message.reply_text("🔄 Processing your request...")
    
    try:
        # Validate URL
        if not URLValidator.is_valid_url(url):
            await status_message.edit_text("❌ Invalid URL. Please send a valid URL.")
            return

        # Determine platform
        platform = URLValidator.get_platform(url)
        if not platform:
            await status_message.edit_text(
                "❌ Unsupported platform. Please send a URL from a supported platform."
            )
            return

        # Update status
        await status_message.edit_text("⏳ Starting download...")

        # Handle download based on platform
        result = None
        if platform == 'youtube':
            result = await youtube_dl.download(url)
        elif platform == 'instagram':
            result = await instagram_dl.download_post(url)
        elif platform == 'reddit':
            result = await reddit_dl.download_post(url)
        elif platform == 'pinterest':
            result = await pinterest_dl.download_pin(url)
        #elif platform == 'spotify':
            #result = await spotify_dl.download_track(url)

        if not result or not result.get('success'):
            error_msg = result.get('error', 'Unknown error') if result else 'Download failed'
            await status_message.edit_text(f"❌ {error_msg}")
            return

        # Track download
        await download_tracker.add_download({
            'url': url,
            'platform': platform,
            'success': True,
            'title': result.get('title', 'Unknown'),
            'file_size': sum(FileManager.get_file_size(Path(p)) for p in result.get('paths', []))
            if result.get('paths')
            else FileManager.get_file_size(Path(result['path']))
            if result.get('path')
            else 0
        })

        try:
            if 'paths' in result:  # Multiple files (e.g., Pinterest)
                await status_message.edit_text("📤 Sending files...")
                file_paths = [Path(p) for p in result['paths']]
                total_files = len(file_paths)
                
                for idx, file_path in enumerate(file_paths, 1):
                    try:
                        # Ensure filename has consistent format
                        title = FileManager.sanitize_filename(result.get('title', 'Unknown'))
                        file_name = f"{title}_part_{idx}{file_path.suffix}"
                        new_path = file_path.parent / file_name

                        # Rename if necessary
                        if file_path != new_path and file_path.exists():
                            file_path.rename(new_path)

                        # Open file in binary mode for sending
                        with open(new_path, 'rb') as file:
                            caption = f"📄 {result.get('title', 'File')} ({idx}/{total_files})"
                            if new_path.suffix.lower() in ['.mp4', '.webm']:
                                await update.message.reply_video(
                                    video=file,
                                    caption=caption
                                )
                            elif new_path.suffix.lower() in ['.mp3', '.m4a', '.wav']:
                                await update.message.reply_audio(
                                    audio=file,
                                    caption=caption
                                )
                            else:
                                await update.message.reply_document(
                                    document=file,
                                    caption=caption
                                )

                        # Cleanup if enabled
                        if config.CLEANUP_AFTER_SEND:
                            new_path.unlink()

                    except Exception as e:
                        logger.error(f"Error sending file {idx}: {str(e)}", exc_info=True)
                        await status_message.edit_text(f"❌ Error sending file {idx}: {str(e)}")
                        return

                await status_message.edit_text(f"✅ Successfully sent {total_files} files!")

            else:  # Single file
                file_path = Path(result['path'])
                await status_message.edit_text("📤 Sending file...")
                
                # Ensure filename has consistent format
                title = FileManager.sanitize_filename(result.get('title', 'Unknown'))
                new_path = file_path.parent / f"{title}{file_path.suffix}"
                
                # Rename if necessary
                if file_path != new_path and file_path.exists():
                    file_path.rename(new_path)
                
                # Open file in binary mode for sending
                with open(new_path, 'rb') as file:
                    if new_path.suffix.lower() in ['.mp4', '.webm']:
                        await update.message.reply_video(
                            video=file,
                            caption=f"📹 {result.get('title', 'Video')}"
                        )
                    elif new_path.suffix.lower() in ['.mp3', '.m4a', '.wav']:
                        await update.message.reply_audio(
                            audio=file,
                            caption=f"🎵 {result.get('title', 'Audio')}"
                        )
                    else:
                        await update.message.reply_document(
                            document=file,
                            caption=f"📄 {result.get('title', 'File')}"
                        )

                # Cleanup if enabled
                if config.CLEANUP_AFTER_SEND:
                    new_path.unlink()

                await status_message.delete()

        except FileNotFoundError as e:
            await status_message.edit_text("❌ File not found after download")
            logger.error(f"File not found: {str(e)}")
        except Exception as e:
            await status_message.edit_text(f"❌ Error sending file: {str(e)}")
            logger.error(f"Error sending file: {str(e)}", exc_info=True)

    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}", exc_info=True)
        await status_message.edit_text(f"❌ Error: {str(e)}")
        
        # Track failed download
        await download_tracker.add_download({
            'url': url,
            'platform': platform if platform else 'unknown',
            'success': False,
            'error': str(e)
        })

async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return bot health status as JSON"""
    try:
        # Get system metrics
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Calculate uptime
        uptime = datetime.now() - startup_time
        
        # Get download stats
        stats = await download_tracker.get_stats()
        
        health_data = {
            "status": "healthy",
            "uptime": {
                "seconds": int(uptime.total_seconds()),
                "formatted": str(timedelta(seconds=int(uptime.total_seconds())))
            },
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory": {
                    "used_mb": memory_info.rss / 1024 / 1024,
                    "percent": process.memory_percent()
                },
                "disk": {
                    "total_gb": psutil.disk_usage('/').total / (1024 ** 3),
                    "used_gb": psutil.disk_usage('/').used / (1024 ** 3),
                    "percent": psutil.disk_usage('/').percent
                }
            },
            "downloaders": {
                "youtube": bool(youtube_dl),
                "instagram": bool(instagram_dl),
                "reddit": bool(reddit_dl),
                "pinterest": bool(pinterest_dl),
                "spotify": bool(spotify_dl)
            },
            "statistics": {
                "total_downloads": stats['total_downloads'],
                "successful_downloads": stats['successful_downloads'],
                "failed_downloads": stats['failed_downloads'],
                "success_rate": round(stats['success_rate'], 2),
                "total_data_downloaded": FileManager.format_size(stats['total_size_bytes']),
                "downloads_by_platform": stats['downloads_by_platform']
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Send JSON response
        await update.message.reply_text(
            json.dumps(health_data, indent=2),
            parse_mode=None  # Disable markdown/HTML parsing
        )
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        await update.message.reply_text(
            json.dumps(error_response, indent=2),
            parse_mode=None
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('settings_'):
        setting = query.data.replace('settings_', '')
        # Implement settings logic here
        await query.message.edit_text(f"Setting '{setting}' will be implemented soon!")

async def get_health_data() -> Dict:
    """Get bot health data"""
    try:
        # Get system metrics
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Calculate uptime
        uptime = datetime.now() - startup_time
        
        # Get download stats
        stats = await download_tracker.get_stats()
        
        return {
            "status": "healthy",
            "uptime": {
                "seconds": int(uptime.total_seconds()),
                "formatted": str(timedelta(seconds=int(uptime.total_seconds())))
            },
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory": {
                    "used_mb": memory_info.rss / 1024 / 1024,
                    "percent": process.memory_percent()
                },
                "disk": {
                    "total_gb": psutil.disk_usage('/').total / (1024 ** 3),
                    "used_gb": psutil.disk_usage('/').used / (1024 ** 3),
                    "percent": psutil.disk_usage('/').percent
                }
            },
            "downloaders": {
                "youtube": bool(youtube_dl),
                "instagram": bool(instagram_dl),
                "reddit": bool(reddit_dl),
                "pinterest": bool(pinterest_dl),
                "spotify": bool(spotify_dl)
            },
            "statistics": {
                "total_downloads": stats['total_downloads'],
                "successful_downloads": stats['successful_downloads'],
                "failed_downloads": stats['failed_downloads'],
                "success_rate": round(stats['success_rate'], 2),
                "total_data_downloaded": FileManager.format_size(stats['total_size_bytes']),
                "downloads_by_platform": stats['downloads_by_platform']
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def health_endpoint(request):
    """Handle HTTP GET requests to /health endpoint"""
    data = await get_health_data()
    return web.json_response(data)

def main():
    """Start the bot and web server"""
    # Create the Application
    application = Application.builder().token(config.BOT_TOKEN).build()

    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Set up web app
    web_app = web.Application()
    web_app.router.add_get('/monitor-health', health_endpoint)
    
    async def start_services():
        # Start web server
        runner = web.AppRunner(web_app)
        await runner.setup()
        site = web.TCPSite(runner, config.HEALTH_API_HOST, config.HEALTH_API_PORT)
        await site.start()
        logger.info(f"Health API started on http://{config.HEALTH_API_HOST}:{config.HEALTH_API_PORT}/health")

    # Initialize the event loop explicitly
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Start web server
        runner = web.AppRunner(web_app)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, config.HEALTH_API_HOST, config.HEALTH_API_PORT)
        loop.run_until_complete(site.start())
        logger.info(f"Health API started on http://{config.HEALTH_API_HOST}:{config.HEALTH_API_PORT}/health")

        # Start the bot
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
    except Exception as e:
        logger.error(f"Error running application: {e}")
        raise

if __name__ == '__main__':
    main()
