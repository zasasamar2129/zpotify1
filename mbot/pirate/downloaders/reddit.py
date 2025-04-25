import os
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import praw
import requests
import aiohttp
import aiofiles

class RedditDownloader:
    def __init__(self, 
                 client_id: str,
                 client_secret: str,
                 user_agent: str,
                 download_path: str = "downloads/reddit"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def _parse_url(self, url: str) -> Dict:
        """Parse Reddit URL to determine content type"""
        if "/comments/" in url:
            return {"type": "post", "id": url.split("/comments/")[1].split("/")[0]}
        elif "/r/" in url:
            return {"type": "subreddit", "name": url.split("/r/")[1].split("/")[0]}
        else:
            raise ValueError("Unsupported Reddit URL")

    async def _download_file(self, url: str, filename: str) -> bool:
        """Download a file asynchronously"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        filepath = self.download_path / filename
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(await response.read())
                        return True
            return False
        except Exception:
            return False

    async def download_media_from_url(self, url: str, filename: str) -> Dict:
        """Download media from a direct URL"""
        try:
            success = await self._download_file(url, filename)
            if success:
                return {
                    'success': True,
                    'url': url,
                    'path': str(self.download_path / filename),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("Failed to download media")
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def download_post(self, url: str) -> Dict:
        """Download media from a Reddit post"""
        try:
            parsed = self._parse_url(url)
            if parsed["type"] != "post":
                raise ValueError("URL must be a Reddit post")

            # Get post information
            submission = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.reddit.submission(id=parsed["id"])
            )

            results = {
                'success': True,
                'title': submission.title,
                'author': str(submission.author),
                'media': [],
                'text': submission.selftext if submission.selftext else None,
                'timestamp': datetime.now().isoformat()
            }

            # Handle different types of media
            if hasattr(submission, 'is_video') and submission.is_video:
                # Download Reddit-hosted video
                if hasattr(submission, 'media') and submission.media:
                    video_url = submission.media['reddit_video']['fallback_url']
                    filename = f"{submission.id}_video.mp4"
                    result = await self.download_media_from_url(video_url, filename)
                    if result['success']:
                        results['media'].append({
                            'type': 'video',
                            'path': result['path']
                        })

            elif hasattr(submission, 'url'):
                # Handle image posts
                if any(submission.url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    filename = f"{submission.id}_image{Path(submission.url).suffix}"
                    result = await self.download_media_from_url(submission.url, filename)
                    if result['success']:
                        results['media'].append({
                            'type': 'image',
                            'path': result['path']
                        })

                # Handle gallery posts
                elif hasattr(submission, 'is_gallery') and submission.is_gallery:
                    for i, item in enumerate(submission.gallery_data['items']):
                        media_id = item['media_id']
                        if media_id in submission.media_metadata:
                            image_url = submission.media_metadata[media_id]['p'][0]['u']
                            filename = f"{submission.id}_gallery_{i}{Path(image_url).suffix}"
                            result = await self.download_media_from_url(image_url, filename)
                            if result['success']:
                                results['media'].append({
                                    'type': 'image',
                                    'path': result['path']
                                })

            return results

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def download_subreddit(self, url: str, limit: int = 10, 
                               sort: str = 'hot') -> List[Dict]:
        """Download media from top posts in a subreddit"""
        try:
            parsed = self._parse_url(url)
            if parsed["type"] != "subreddit":
                raise ValueError("URL must be a subreddit")

            subreddit = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.reddit.subreddit(parsed["name"])
            )

            results = []
            posts = []

            # Get posts based on sort method
            if sort == 'hot':
                posts = subreddit.hot(limit=limit)
            elif sort == 'new':
                posts = subreddit.new(limit=limit)
            elif sort == 'top':
                posts = subreddit.top(limit=limit)

            for submission in posts:
                post_url = f"https://reddit.com{submission.permalink}"
                result = await self.download_post(post_url)
                results.append(result)

            return results

        except Exception as e:
            return [{
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }]