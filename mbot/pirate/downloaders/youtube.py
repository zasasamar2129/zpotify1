import os
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from yt_dlp import YoutubeDL
from pathlib import Path

class YouTubeDownloader:
    def __init__(self, download_path: str = "downloads/youtube"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        
        # Default options for yt-dlp
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'windowsfilenames': True,  # Ensure consistent filename handling
            'postprocessors': [{
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }],
            # Custom filename sanitization function
            'filenamecallback': lambda filename: filename.replace(' ', '_')
        }

    async def get_video_info(self, url: str) -> Dict:
        """Fetch video metadata without downloading."""
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, ydl.extract_info, url, True
                )
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'formats': self._parse_formats(info.get('formats', [])),
                    'thumbnail': info.get('thumbnail'),
                    'is_playlist': info.get('_type') == 'playlist'
                }
        except Exception as e:
            raise Exception(f"Error fetching video info: {str(e)}")

    def _parse_formats(self, formats: List[Dict]) -> Dict[str, str]:
        """Parse available video formats into a more readable format."""
        parsed = {}
        for f in formats:
            if f.get('ext') in ['mp4', 'webm']:
                quality = f.get('format_note', 'unknown')
                if quality not in parsed:
                    parsed[quality] = f.get('format_id')
        return parsed

    async def download(self, url: str, quality: str = 'best') -> Dict:
        """
        Download a video in specified quality.
        
        Args:
            url: YouTube video URL
            quality: Video quality ('best', '1080p', '720p', etc.)
            
        Returns:
            Dict containing download details
        """
        try:
            info = await self.get_video_info(url)
            
            # Modify format based on quality selection
            if quality != 'best' and quality in info['formats']:
                self.ydl_opts['format'] = info['formats'][quality]

            # Download the video
            with YoutubeDL(self.ydl_opts) as ydl:
                await asyncio.get_event_loop().run_in_executor(
                    None, ydl.download, [url]
                )
            
            return {
                'success': True,
                'title': info['title'],
                'path': str(self.download_path / f"{info['title']}.mp4"),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def download_playlist(self, url: str, max_videos: Optional[int] = None) -> List[Dict]:
        """Download all videos from a playlist."""
        try:
            # Modify options for playlist download
            playlist_opts = self.ydl_opts.copy()
            playlist_opts.update({
                'noplaylist': False,
                'playlist_items': f"1:{max_videos}" if max_videos else None
            })

            results = []
            with YoutubeDL(playlist_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, ydl.extract_info, url, False
                )
                
                if info.get('_type') != 'playlist':
                    raise ValueError("URL is not a playlist")

                # Download each video in the playlist
                for entry in info['entries']:
                    if not entry:
                        continue
                    video_url = entry.get('webpage_url')
                    result = await self.download(video_url)
                    results.append(result)

            return results

        except Exception as e:
            return [{
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }]