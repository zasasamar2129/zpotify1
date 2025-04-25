import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import validators
import aiofiles
from urllib.parse import urlparse

class DownloadTracker:
    """Track download history and statistics"""
    def __init__(self, history_file: str = "download_history.json"):
        self.history_file = Path(history_file)
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Create history file if it doesn't exist"""
        if not self.history_file.exists():
            self.history_file.write_text('{"downloads": []}')

    async def add_download(self, data: Dict) -> None:
        """Add a download record to history"""
        try:
            async with aiofiles.open(self.history_file, 'r') as f:
                history = json.loads(await f.read())
            
            history['downloads'].append({
                **data,
                'timestamp': datetime.now().isoformat()
            })

            async with aiofiles.open(self.history_file, 'w') as f:
                await f.write(json.dumps(history, indent=2))
        except Exception as e:
            print(f"Error tracking download: {str(e)}")

    async def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get download history"""
        try:
            async with aiofiles.open(self.history_file, 'r') as f:
                history = json.loads(await f.read())
            
            downloads = history['downloads']
            if limit:
                downloads = downloads[-limit:]
            return downloads
        except Exception:
            return []

    async def get_stats(self) -> Dict:
        """Get download statistics"""
        try:
            async with aiofiles.open(self.history_file, 'r') as f:
                history = json.loads(await f.read())
            
            downloads = history['downloads']
            total_downloads = len(downloads)
            successful = sum(1 for d in downloads if d.get('success', False))
            failed = total_downloads - successful

            # Group by platform
            platforms = {}
            for download in downloads:
                platform = download.get('platform', 'unknown')
                platforms[platform] = platforms.get(platform, 0) + 1

            # Calculate total size
            total_size = sum(
                download.get('file_size', 0) 
                for download in downloads 
                if download.get('success', False)
            )

            return {
                'total_downloads': total_downloads,
                'successful_downloads': successful,
                'failed_downloads': failed,
                'success_rate': (successful / total_downloads * 100) if total_downloads > 0 else 0,
                'downloads_by_platform': platforms,
                'total_size_bytes': total_size
            }
        except Exception:
            return {
                'total_downloads': 0,
                'successful_downloads': 0,
                'failed_downloads': 0,
                'success_rate': 0,
                'downloads_by_platform': {},
                'total_size_bytes': 0
            }

class URLValidator:
    """Validate URLs for different platforms"""
    
    PATTERNS = {
        'youtube': [
            r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://youtu\.be/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+'
        ],
        'instagram': [
            r'^https?://(?:www\.)?instagram\.com/p/[\w-]+',
            r'^https?://(?:www\.)?instagram\.com/reel/[\w-]+',
            r'^https?://(?:www\.)?instagram\.com/stories/[\w-]+',
        ],
        'reddit': [
            r'^https?://(?:www\.)?reddit\.com/r/[\w-]+/comments/[\w-]+',
            r'^https?://(?:www\.)?reddit\.com/r/[\w-]+/?$'
        ],
        'pinterest': [
            r'^https?://(?:www\.)?pinterest\.com/pin/[\w-]+',
            r'^https?://(?:www\.)?pinterest\.com/[\w-]+/[\w-]+/?$',
            r'^https?://pin\.it/[\w-]+$'  # Short URL format
        ],
        'spotify': [
            r'^https?://(?:open\.)?spotify\.com/track/[\w-]+',
            r'^https?://(?:open\.)?spotify\.com/playlist/[\w-]+',
            r'^https?://(?:open\.)?spotify\.com/album/[\w-]+'
        ]
    }

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        return bool(validators.url(url))

    @staticmethod
    def get_platform(url: str) -> Optional[str]:
        """Determine platform from URL"""
        if not URLValidator.is_valid_url(url):
            return None
            
        domain = urlparse(url).netloc.lower()
        
        platform_domains = {
            'youtube.com': 'youtube',
            'youtu.be': 'youtube',
            'instagram.com': 'instagram',
            'reddit.com': 'reddit',
            'pinterest.com': 'pinterest',
            'spotify.com': 'spotify',
        }
        
        return next(
            (platform for domain_part, platform in platform_domains.items() 
             if domain_part in domain),
            None
        )

class FileManager:
    """Handle file operations and organization"""
    
    @staticmethod
    def get_file_size(filepath: Path) -> int:
        """Get file size in bytes"""
        try:
            return filepath.stat().st_size
        except Exception:
            return 0

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by:
        1. Removing invalid characters
        2. Converting spaces to underscores
        3. Ensuring consistent case
        4. Trimming extra whitespace and underscores
        """
        # Convert to lowercase for consistency
        filename = filename.lower()
        
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Replace spaces and multiple underscores with single underscore
        filename = '_'.join(filter(None, filename.split()))
        
        # Remove any leading/trailing underscores and spaces
        filename = filename.strip('_').strip()
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed"
        
        return filename

    @staticmethod
    def ensure_unique_path(filepath: Path) -> Path:
        """Ensure filepath is unique by adding number if needed"""
        if not filepath.exists():
            return filepath
            
        directory = filepath.parent
        name = filepath.stem
        extension = filepath.suffix
        counter = 1
        
        while True:
            new_path = directory / f"{name}_{counter}{extension}"
            if not new_path.exists():
                return new_path
            counter += 1

class ProgressTracker:
    """Track download progress"""
    
    def __init__(self, total: int):
        self.total = total
        self.current = 0
        self.start_time = datetime.now()

    def update(self, chunk_size: int) -> Dict:
        """Update progress and return status"""
        self.current += chunk_size
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        if elapsed > 0:
            speed = self.current / elapsed
        else:
            speed = 0
            
        return {
            'total_size': self.total,
            'downloaded': self.current,
            'percent': (self.current / self.total * 100) if self.total > 0 else 0,
            'speed': speed,
            'elapsed': elapsed
        }