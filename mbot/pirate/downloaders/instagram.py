import os
import sys
import asyncio
import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path
import instaloader
from instaloader import Post, Profile, Story, StoryItem

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils import FileManager

# Configure logging
logger = logging.getLogger(__name__)

class InstagramDownloader:
    def __init__(self, download_path: str = "downloads/instagram"):
        # Set up base download path
        self.download_path = Path(download_path).resolve()
        self.download_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created download directory at: {self.download_path}")

        # Initialize instaloader instance with optimized settings
        self.loader = instaloader.Instaloader(
            download_pictures=True,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            filename_pattern='{profile}_{mediaid}',
            dirname_pattern='',  # Don't create additional directories
            post_metadata_txt_pattern='',
            storyitem_metadata_txt_pattern='',
            max_connection_attempts=3
        )

    async def login(self, username: str, password: str) -> bool:
        """Login to Instagram (required for private content and stories)"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.loader.login, username, password
            )
            return True
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")

    def _parse_url(self, url: str) -> Dict:
        """Parse Instagram URL to determine content type and shortcode"""
        # Remove query parameters
        url = url.split('?')[0].rstrip('/')

        if "/p/" in url:
            code = url.split("/p/")[1].split("/")[0]
            return {"type": "post", "code": code}
        elif "/reel/" in url:
            code = url.split("/reel/")[1].split("/")[0]
            return {"type": "reel", "code": code}
        elif "/stories/" in url:
            parts = url.split("/stories/")[1].split("/")
            return {"type": "story", "username": parts[0]}
        else:
            raise ValueError("Unsupported Instagram URL")

    async def _ensure_login(self):
        """Ensure we're logged in if credentials are available"""
        if not self.loader.context.is_logged_in and hasattr(self.loader.context, 'username'):
            try:
                await self.login(self.loader.context.username, self.loader.context.password)
            except:
                pass  # Silent fail if login fails, we'll try without login

    async def download_post(self, url: str) -> Dict:
        """Download an Instagram post (image or video)"""
        original_cwd = os.getcwd()
        try:
            # Try to login if credentials are available
            await self._ensure_login()

            parsed = self._parse_url(url)
            if parsed["type"] not in ["post", "reel"]:
                raise ValueError("URL must be a post or reel")

            shortcode = parsed["code"]
            try:
                post = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: Post.from_shortcode(self.loader.context, shortcode)
                )
            except Exception as e:
                logger.error(f"Error fetching post {shortcode}: {str(e)}")
                raise ValueError(f"Could not fetch post. It might be private or deleted: {str(e)}")

            # Get current working directory
            logger.info(f"Original working directory: {original_cwd}")

            # Create user directory
            user_dir = self.download_path / FileManager.sanitize_filename(post.owner_username)
            user_dir.mkdir(parents=True, exist_ok=True)

            # Change to user directory for download
            os.chdir(str(user_dir))
            logger.info(f"Changed working directory to: {os.getcwd()}")

            # Download the post with retries
            max_retries = 3
            retry_count = 0
            downloaded = False
            expected_filename = f"{post.owner_username}_{post.mediaid}"

            logger.info(f"Attempting to download post {shortcode}")
            logger.info(f"Expected filename pattern: {expected_filename}")

            while retry_count < max_retries and not downloaded:
                try:
                    logger.info(f"Download attempt {retry_count + 1}/{max_retries}")
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        # Download the post
                        lambda: self.loader.download_post(post, target=user_dir)
                    )
                    # Wait a moment for file to be written
                    await asyncio.sleep(1)

                    # Check for the file with any extension in current directory
                    potential_files = list(user_dir.glob(f"{expected_filename}.*"))
                    if potential_files:
                        downloaded = True
                        logger.info(f"Download successful on attempt {retry_count + 1}")
                        logger.info(f"Found files: {[f.name for f in potential_files]}")
                    else:
                        raise FileNotFoundError(f"File {expected_filename}.* not found after download")

                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Download attempt {retry_count} failed: {str(e)}")
                    if retry_count < max_retries:
                        await asyncio.sleep(2)  # Wait before retry
                    else:
                        logger.error(f"All download attempts failed for {shortcode}")
                        raise

            # Get the downloaded file (should be only one)
            downloaded_file = potential_files[0]
            full_path = user_dir / downloaded_file.name

            return {
                'success': True,
                'type': 'video' if post.is_video else 'image',
                'caption': post.caption if post.caption else '',
                'title': downloaded_file.stem,
                'timestamp': datetime.now().isoformat(),
                'path': str(full_path)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
            logger.info(f"Restored working directory to: {original_cwd}")

    async def download_story(self, url: str) -> List[Dict]:
        """Download Instagram stories from a user"""
        original_cwd = os.getcwd()
        try:
            parsed = self._parse_url(url)
            if parsed["type"] != "story":
                raise ValueError("URL must be a story")

            username = parsed["username"]
            profile = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: Profile.from_username(self.loader.context, username)
            )

            # Get user's stories
            stories = await asyncio.get_event_loop().run_in_executor(
                None,
                self.loader.get_stories, [profile.userid]
            )

            # Create a directory for this user's stories
            story_dir = self.download_path / FileManager.sanitize_filename(username) / 'stories'
            story_dir.mkdir(parents=True, exist_ok=True)

            # Change to story directory
            os.chdir(str(story_dir))
            logger.info(f"Changed working directory to: {os.getcwd()}")

            results = []
            for story in stories:
                for item in story.get_items():
                    try:
                        # Download each story item
                        await asyncio.get_event_loop().run_in_executor(
                            None,
                            self.loader.download_storyitem,
                            item
                        )
                        await asyncio.sleep(1)  # Wait for file to be written

                        # Find the downloaded file
                        files = list(Path('.').glob('*'))
                        if files:
                            # Get the latest downloaded file
                            downloaded_file = max(files, key=lambda f: f.stat().st_mtime)
                            full_path = story_dir / downloaded_file.name
                            results.append({
                                'success': True,
                                'type': 'video' if item.is_video else 'image',
                                'title': downloaded_file.stem,
                                'timestamp': datetime.now().isoformat(),
                                'path': str(full_path)
                            })
                    except Exception as e:
                        logger.error(f"Error downloading story item: {str(e)}")

            return results

        except Exception as e:
            return [{
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }]
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
            logger.info(f"Restored working directory to: {original_cwd}")

    async def download_highlights(self, username: str) -> List[Dict]:
        """Download user's story highlights"""
        original_cwd = os.getcwd()
        try:
            profile = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: Profile.from_username(self.loader.context, username)
            )

            results = []
            highlights = await asyncio.get_event_loop().run_in_executor(
                None,
                self.loader.get_highlights,
                profile
            )

            # Create base highlights directory
            highlights_base = self.download_path / FileManager.sanitize_filename(username) / 'highlights'
            highlights_base.mkdir(parents=True, exist_ok=True)

            for highlight in highlights:
                # Create a subdirectory for each highlight
                highlight_dir = highlights_base / FileManager.sanitize_filename(highlight.title)
                highlight_dir.mkdir(parents=True, exist_ok=True)

                # Change to highlight directory
                os.chdir(str(highlight_dir))
                logger.info(f"Changed working directory to: {os.getcwd()}")

                for item in highlight.get_items():
                    try:
                        # Download the highlight item
                        await asyncio.get_event_loop().run_in_executor(
                            None,
                            self.loader.download_storyitem,
                            item
                        )
                        await asyncio.sleep(1)  # Wait for file to be written

                        # Find the downloaded file
                        files = list(Path('.').glob('*'))
                        if files:
                            # Get the latest downloaded file
                            downloaded_file = max(files, key=lambda f: f.stat().st_mtime)
                            full_path = highlight_dir / downloaded_file.name
                            results.append({
                                'success': True,
                                'type': 'video' if item.is_video else 'image',
                                'title': downloaded_file.stem,
                                'highlight_title': highlight.title,
                                'timestamp': datetime.now().isoformat(),
                                'path': str(full_path)
                            })
                    except Exception as e:
                        logger.error(f"Error downloading highlight item: {str(e)}")

            return results

        except Exception as e:
            return [{
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }]
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
            logger.info(f"Restored working directory to: {original_cwd}")