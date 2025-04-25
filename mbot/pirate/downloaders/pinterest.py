import os
import asyncio
import aiohttp
import aiofiles
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse, unquote

# Configure logging
logger = logging.getLogger(__name__)

class PinterestDownloader:
    def __init__(self, download_path: str = "downloads/pinterest"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

    def _extract_images_from_json(self, pin_data: Dict) -> List[Dict]:
        """Extract unique image URLs from Pinterest JSON data"""
        images = []
        seen_urls = set()
        
        def add_unique_image(url: str, width: int = None, height: int = None):
            """Add image if URL is unique"""
            if url and url not in seen_urls:
                seen_urls.add(url)
                images.append({
                    'url': url,
                    'width': width,
                    'height': height
                })

        # Check for high-quality images first
        if 'images' in pin_data:
            size_preference = ['orig', 'x1200', 'x1000', 'x800', 'x600']
            for size in size_preference:
                if size in pin_data['images']:
                    data = pin_data['images'][size]
                    if isinstance(data, dict) and 'url' in data:
                        add_unique_image(
                            data['url'],
                            data.get('width'),
                            data.get('height')
                        )

        # Check 'story_pin_data' for additional unique images
        story_pin = pin_data.get('story_pin_data', {})
        if story_pin and 'pages' in story_pin:
            for page in story_pin['pages']:
                for block in page.get('blocks', []):
                    if 'image' in block:
                        image_data = block['image']
                        if isinstance(image_data, dict) and 'images' in image_data:
                            # Sort by size if available
                            images_list = list(image_data['images'].values())
                            images_list.sort(
                                key=lambda x: (x.get('width', 0) * x.get('height', 0)),
                                reverse=True
                            )
                            for img in images_list:
                                if 'url' in img:
                                    add_unique_image(
                                        img['url'],
                                        img.get('width'),
                                        img.get('height')
                                    )
        
        logger.info(f"Extracted {len(images)} images from JSON")

        return images

    def _extract_images_from_html(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract unique and high-quality images from Pinterest HTML"""
        images = []
        seen_urls = set()

        def normalize_url(url: str) -> str:
            """Normalize the URL to ensure deduplication works correctly"""
            parsed = urlparse(url)
            # Keep original URL but strip any query parameters
            return url.split('?')[0]

        def add_unique_image(url: str, width: int = None, height: int = None):
            """Add image if URL is unique and high quality"""
            if not url:
                return

            # Normalize the URL
            normalized_url = normalize_url(url)

            # Skip if already seen
            if normalized_url in seen_urls:
                return

            # Skip low-quality and thumbnail images
            if any(x in url.lower() for x in ['/237x/', '/75x/']):
                return

            # Extract size from URL if not provided
            if not width or not height:
                size_match = re.search(r'/(\d+)x/', url)
                if size_match:
                    width = height = int(size_match.group(1))

            seen_urls.add(normalized_url)
            images.append({
                'url': normalized_url,
                'width': width,
                'height': height
            })

        # Extract images from carousel with srcset handling
        carousel_divs = soup.find_all('div', {'data-test-id': re.compile(r'carousel-img-\d+')})
        logger.info(f"Found {len(carousel_divs)} carousel divs")
        
        for carousel in carousel_divs:
            img_tag = carousel.find('img')
            if img_tag:
                # Try to get the best quality image from srcset or src
                src = img_tag.get('src', '')
                srcset = img_tag.get('srcset', '').split(',')
                
                best_url = src
                # Check srcset for highest quality
                for srcset_item in srcset:
                    parts = srcset_item.strip().split()
                    if len(parts) >= 1 and '736x' in parts[0]:
                        best_url = parts[0]
                        break
                
                # If no 736x found in srcset, try to upgrade src
                if '736x' not in best_url:
                    best_url = re.sub(r'/\d+x/', '/736x/', best_url)
                
                logger.info(f"Processing carousel image: {best_url}")
                add_unique_image(best_url)

        # Extract images from <img> tags with quality indicators
        quality_indicators = ['/originals/', '/736x/', '/564x/', '/550x/', '/474x/']
        for img in soup.find_all('img', {'src': True}):
            src = img.get('src', '')
            if any(x in src.lower() for x in quality_indicators):
                add_unique_image(src)

        # Sort images by quality (based on dimensions if available)
        images.sort(
            key=lambda x: (x.get('width', 0) or 0) * (x.get('height', 0) or 0),
            reverse=True
        )
        
        logger.info(f"Extracted {len(images)} images from HTML")

        return images
    
    async def _resolve_short_url(self, url: str) -> str:
        """Resolve pin.it short URL to full Pinterest URL"""
        try:
            logger.info(f"Resolving short URL: {url}")
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status == 200:
                        final_url = str(response.url)
                        logger.info(f"Resolved to: {final_url}")
                        return final_url
            return url
        except Exception as e:
            logger.error(f"Error resolving short URL: {str(e)}")
            return url

    def _normalize_pinterest_url(self, url: str) -> str:
        """Convert any Pinterest URL to standard format"""
        # Remove query parameters and trailing slashes
        url = url.split('?')[0].rstrip('/')
        
        # Parse URL
        parsed = urlparse(url)
        
        # Handle various Pinterest domains
        if any(domain in parsed.netloc for domain in ['pin.it', 'pinterest.com', 'www.pinterest.com']) or \
           parsed.netloc.endswith('pinterest.com'):
            # Extract the path
            path = parsed.path.strip('/')
            
            # For pin URLs, standardize to pinterest.com format
            if 'pin' in path:
                pin_id = re.search(r'pin[/]?([0-9]+)', path)
                if pin_id:
                    return f"https://www.pinterest.com/pin/{pin_id.group(1)}"
            
            return f"https://www.pinterest.com/{path}"
        
        return url

    async def _parse_url(self, url: str) -> Dict:
        """Parse Pinterest URL to determine content type"""
        # Handle short URLs
        if "pin.it" in url:
            url = await self._resolve_short_url(url)
        
        # Normalize URL
        url = self._normalize_pinterest_url(url)
        logger.info(f"Normalized URL: {url}")
        
        if "/pin/" in url:
            pin_id = url.split("/pin/")[1].split("/")[0]
            logger.info(f"Detected pin ID: {pin_id}")
            return {"type": "pin", "id": pin_id}
        elif "/board/" in url:
            parts = url.split("/board/")[1].split("/")
            return {"type": "board", "username": parts[0], "board_name": parts[1]}
        else:
            raise ValueError("Unsupported Pinterest URL")

    async def _get_pin_data(self, pin_id: str) -> Dict:
        """Extract pin data and all associated images"""
        urls_to_try = [
            f"https://www.pinterest.com/pin/{pin_id}/",
            f"https://pinterest.com/pin/{pin_id}/"
        ]
        
        for url in urls_to_try:
            try:
                logger.info(f"Fetching pin data from: {url}")
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            continue
                        
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        pin_data = {
                            'title': '',
                            'description': '',
                            'images': []
                        }

                        # Get basic metadata
                        meta_title = soup.find('meta', property='og:title')
                        meta_desc = soup.find('meta', property='og:description')
                        pin_data['title'] = meta_title.get('content', '') if meta_title else ''
                        pin_data['description'] = meta_desc.get('content', '') if meta_desc else ''

                        # Try to find images from Pinterest's JSON data
                        for script in soup.find_all('script', type='application/json'):
                            try:
                                data = json.loads(script.string)
                                if 'props' in data and 'initialReduxState' in data['props']:
                                    pins = data['props']['initialReduxState'].get('pins', {})
                                    if pin_id in pins:
                                        json_images = self._extract_images_from_json(pins[pin_id])
                                        if json_images:
                                            pin_data['images'].extend(json_images)
                            except json.JSONDecodeError:
                                continue

                        # If no images found in JSON, try HTML extraction
                        if not pin_data['images']:
                            html_images = self._extract_images_from_html(soup)
                            pin_data['images'].extend(html_images)

                        if pin_data['images']:
                            return pin_data

            except Exception as e:
                logger.error(f"Error fetching from {url}: {str(e)}")
                continue

        raise Exception("Pin data not found")

    async def _download_file(self, url: str, filename: str) -> bool:
        """Download a file asynchronously"""
        try:
            logger.info(f"Downloading file: {filename}")
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        filepath = self.download_path / filename
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(await response.read())
                        logger.info(f"File downloaded successfully: {filepath}")
                        return True
                    else:
                        logger.error(f"Download failed with status: {response.status}")
            return False
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return False

    async def download_pin(self, url: str) -> Dict:
        """Download all images from a Pinterest pin"""
        try:
            parsed = await self._parse_url(url)
            if parsed["type"] != "pin":
                raise ValueError("URL must be a Pinterest pin")

            logger.info(f"Fetching data for pin: {parsed['id']}")
            pin_data = await self._get_pin_data(parsed["id"])
            
            if not pin_data['images']:
                raise Exception("No images found in pin")

            # Deduplicate images by normalized URL
            unique_images = []
            seen_urls = set()
            for image in pin_data['images']:
                # Replace any resolution with 736x for consistent comparison
                url = image['url']
                base_url = re.sub(r'/\d+x/', '/736x/', url)
                
                if base_url not in seen_urls:
                    seen_urls.add(base_url)
                    # Always use 736x version for download
                    image['url'] = base_url
                    unique_images.append(image)
                    logger.info(f"Added unique image: {base_url}")

            downloaded_files = []
            for idx, image in enumerate(unique_images):
                try:
                    image_url = image['url']
                    suffix = Path(urlparse(image_url).path).suffix or '.jpg'
                    filename = f"pin_{parsed['id']}_{idx+1}{suffix}"
                    
                    logger.info(f"Downloading image {idx+1}/{len(unique_images)}: {filename}")
                    success = await self._download_file(image_url, filename)
                    
                    if success:
                        downloaded_files.append(str(self.download_path / filename))
                except Exception as e:
                    logger.error(f"Error downloading image {idx+1}: {str(e)}")

            if not downloaded_files:
                raise Exception("Failed to download any images")

            return {
                'success': True,
                'id': parsed["id"],
                'title': pin_data.get('title', ''),
                'description': pin_data.get('description', ''),
                'paths': downloaded_files,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error downloading pin: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    async def download_board(self, url: str, limit: Optional[int] = None) -> List[Dict]:
        """Download all pins from a Pinterest board"""
        try:
            parsed = await self._parse_url(url)
            if parsed["type"] != "board":
                raise ValueError("URL must be a Pinterest board")

            logger.info(f"Downloading board: {parsed['username']}/{parsed['board_name']}")
            pin_ids = await self._get_board_pins(parsed["username"], parsed["board_name"])

            if limit:
                pin_ids = pin_ids[:limit]

            results = []
            for pin_id in pin_ids:
                pin_url = f"https://www.pinterest.com/pin/{pin_id}/"
                result = await self.download_pin(pin_url)
                results.append(result)
                await asyncio.sleep(1)  # Rate limiting

            return results

        except Exception as e:
            logger.error(f"Error downloading board: {str(e)}")
            return [{
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }]

    async def _get_board_pins(self, username: str, board_name: str) -> List[str]:
        """Get all pin IDs from a board"""
        board_url = f"https://www.pinterest.com/{username}/{board_name}/"
        pin_ids = []

        try:
            logger.info(f"Fetching board data from: {board_url}")
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(board_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch board data. Status: {response.status}")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Try to find pins in JSON data first
                    for script in soup.find_all('script', type='application/json'):
                        try:
                            data = json.loads(script.string)
                            if 'props' in data and 'initialReduxState' in data['props']:
                                board_data = data['props']['initialReduxState']
                                if 'pins' in board_data:
                                    pin_ids.extend(board_data['pins'].keys())
                        except json.JSONDecodeError:
                            continue
                    
                    # Fallback: Look for pin IDs in various elements
                    if not pin_ids:
                        for element in soup.find_all(['div', 'a']):
                            pin_id = None
                            data_id = element.get('data-test-id', '')
                            href = element.get('href', '')
                            
                            # Try data-test-id attribute
                            if 'pin' in data_id:
                                pin_id = data_id.replace('pin', '')
                            # Try href attribute
                            elif '/pin/' in href:
                                pin_id = href.split('/pin/')[1].split('/')[0]
                            
                            if pin_id and pin_id.isdigit():
                                pin_ids.append(pin_id)

            logger.info(f"Found {len(pin_ids)} pins in board")
            return list(set(pin_ids))  # Remove duplicates

        except Exception as e:
            logger.error(f"Error fetching board data: {str(e)}")
            raise Exception(f"Error fetching board data: {str(e)}")
