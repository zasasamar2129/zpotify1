import os
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL

class SpotifyDownloader:
    def __init__(self, 
                 client_id: str,
                 client_secret: str,
                 download_path: str = "downloads/spotify"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Spotify client
        self.spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )
        
        # Default options for yt-dlp
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True
        }

    def _parse_url(self, url: str) -> Dict:
        """Parse Spotify URL to determine content type and ID"""
        if "track" in url:
            return {"type": "track", "id": url.split("track/")[1].split("?")[0]}
        elif "playlist" in url:
            return {"type": "playlist", "id": url.split("playlist/")[1].split("?")[0]}
        elif "album" in url:
            return {"type": "album", "id": url.split("album/")[1].split("?")[0]}
        else:
            raise ValueError("Unsupported Spotify URL")

    async def _search_youtube(self, query: str) -> Optional[str]:
        """Search for a song on YouTube and return the best match URL"""
        try:
            with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                # Search YouTube
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ydl.extract_info(f"ytsearch:{query}", download=False)
                )
                
                if result and 'entries' in result and result['entries']:
                    # Get the first result
                    video = result['entries'][0]
                    return f"https://www.youtube.com/watch?v={video['id']}"
                return None
        except Exception:
            return None

    async def _download_audio(self, youtube_url: str, title: str) -> Dict:
        """Download audio from YouTube URL"""
        try:
            # Update output template with sanitized title
            self.ydl_opts['outtmpl'] = str(self.download_path / f'{title}.%(ext)s')
            
            with YoutubeDL(self.ydl_opts) as ydl:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    ydl.download, [youtube_url]
                )
                
            return {
                'success': True,
                'title': title,
                'path': str(self.download_path / f'{title}.mp3'),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def download_track(self, url: str) -> Dict:
        """Download a Spotify track"""
        try:
            parsed = self._parse_url(url)
            if parsed["type"] != "track":
                raise ValueError("URL must be a Spotify track")

            # Get track information
            track = await asyncio.get_event_loop().run_in_executor(
                None,
                self.spotify.track, parsed["id"]
            )
            
            # Create search query
            artists = ", ".join([artist["name"] for artist in track["artists"]])
            query = f"{track['name']} {artists}"
            
            # Search on YouTube
            youtube_url = await self._search_youtube(query)
            if not youtube_url:
                raise Exception("Could not find track on YouTube")

            # Download the track
            result = await self._download_audio(youtube_url, track["name"])
            result.update({
                'track_info': {
                    'name': track["name"],
                    'artists': artists,
                    'album': track["album"]["name"],
                    'duration': track["duration_ms"] / 1000,  # Convert to seconds
                    'spotify_url': track["external_urls"]["spotify"]
                }
            })
            
            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def download_playlist(self, url: str, limit: Optional[int] = None) -> List[Dict]:
        """Download tracks from a Spotify playlist"""
        try:
            parsed = self._parse_url(url)
            if parsed["type"] != "playlist":
                raise ValueError("URL must be a Spotify playlist")

            # Get playlist information
            results = []
            offset = 0
            limit = limit or 100  # Default to 100 tracks if no limit specified
            
            while True:
                # Get batch of tracks
                playlist_tracks = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.spotify.playlist_tracks(
                        parsed["id"],
                        offset=offset,
                        limit=min(100, limit - offset)  # Spotify API limit is 100
                    )
                )
                
                if not playlist_tracks["items"]:
                    break

                # Process each track
                for item in playlist_tracks["items"]:
                    if not item["track"]:
                        continue
                        
                    track = item["track"]
                    track_url = track["external_urls"]["spotify"]
                    result = await self.download_track(track_url)
                    results.append(result)
                    
                    # Add delay to avoid rate limits
                    await asyncio.sleep(1)

                offset += len(playlist_tracks["items"])
                if offset >= limit:
                    break

            return results

        except Exception as e:
            return [{
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }]

    async def download_album(self, url: str) -> List[Dict]:
        """Download all tracks from a Spotify album"""
        try:
            parsed = self._parse_url(url)
            if parsed["type"] != "album":
                raise ValueError("URL must be a Spotify album")

            # Get album tracks
            album = await asyncio.get_event_loop().run_in_executor(
                None,
                self.spotify.album, parsed["id"]
            )

            results = []
            for track in album["tracks"]["items"]:
                track_url = track["external_urls"]["spotify"]
                result = await self.download_track(track_url)
                results.append(result)
                
                # Add delay to avoid rate limits
                await asyncio.sleep(1)

            return results

        except Exception as e:
            return [{
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }]