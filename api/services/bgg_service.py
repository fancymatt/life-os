"""
BoardGameGeek Integration Service

Handles searching BoardGameGeek and downloading rulebooks.
Uses BGG XML API v2 for game search and details.
"""

import requests
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from api.config import settings
from api.logging_config import get_logger

logger = get_logger(__name__)


class BGGService:
    """Service for BoardGameGeek integration"""

    def __init__(self):
        """Initialize BGG service"""
        self.api_base = "https://boardgamegeek.com/xmlapi2"
        self.site_base = "https://boardgamegeek.com"
        self.downloads_dir = Path(settings.base_dir) / "data" / "downloads" / "pdfs"
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

        # User agent to avoid being blocked
        self.headers = {
            "User-Agent": "Life-OS Board Game Rules Assistant (educational use)"
        }

    def search_games(self, query: str, exact: bool = False) -> List[Dict[str, Any]]:
        """
        Search BoardGameGeek for games

        Args:
            query: Search query
            exact: If True, only return exact matches

        Returns:
            List of game search results with bgg_id, name, year, type
        """
        try:
            params = {
                "query": query,
                "type": "boardgame,boardgameexpansion"
            }
            if exact:
                params["exact"] = 1

            response = requests.get(
                f"{self.api_base}/search",
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)
            results = []

            for item in root.findall("item"):
                bgg_id = int(item.get("id"))
                name = item.find("name").get("value")
                year_elem = item.find("yearpublished")
                year = int(year_elem.get("value")) if year_elem is not None else None
                item_type = item.get("type")

                results.append({
                    "bgg_id": bgg_id,
                    "name": name,
                    "year": year,
                    "type": item_type
                })

            return results

        except Exception as e:
            logger.error(f"Error searching BGG: {e}")
            return []

    def get_game_details(self, bgg_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed game information from BGG

        Args:
            bgg_id: BoardGameGeek game ID

        Returns:
            Game details dict with name, year, designer, publisher, description, etc.
        """
        try:
            params = {
                "id": bgg_id,
                "stats": 1
            }

            response = requests.get(
                f"{self.api_base}/thing",
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)
            item = root.find("item")

            if item is None:
                return None

            # Extract basic info
            name_elem = item.find("name[@type='primary']")
            name = name_elem.get("value") if name_elem is not None else None

            year_elem = item.find("yearpublished")
            year = int(year_elem.get("value")) if year_elem is not None else None

            description_elem = item.find("description")
            description = description_elem.text if description_elem is not None else None

            # Extract designers
            designers = [
                link.get("value")
                for link in item.findall("link[@type='boardgamedesigner']")
            ]
            designer = ", ".join(designers) if designers else None

            # Extract publishers
            publishers = [
                link.get("value")
                for link in item.findall("link[@type='boardgamepublisher']")
            ]
            publisher = ", ".join(publishers) if publishers else None

            # Extract player count
            minplayers_elem = item.find("minplayers")
            maxplayers_elem = item.find("maxplayers")
            player_count_min = int(minplayers_elem.get("value")) if minplayers_elem is not None else None
            player_count_max = int(maxplayers_elem.get("value")) if maxplayers_elem is not None else None

            # Extract playtime
            minplaytime_elem = item.find("minplaytime")
            maxplaytime_elem = item.find("maxplaytime")
            playtime_min = int(minplaytime_elem.get("value")) if minplaytime_elem is not None else None
            playtime_max = int(maxplaytime_elem.get("value")) if maxplaytime_elem is not None else None

            # Extract complexity (average weight)
            stats = item.find("statistics/ratings")
            complexity = None
            if stats is not None:
                averageweight_elem = stats.find("averageweight")
                if averageweight_elem is not None:
                    complexity = float(averageweight_elem.get("value"))

            return {
                "bgg_id": bgg_id,
                "name": name,
                "year": year,
                "designer": designer,
                "publisher": publisher,
                "description": description,
                "player_count_min": player_count_min,
                "player_count_max": player_count_max,
                "playtime_min": playtime_min,
                "playtime_max": playtime_max,
                "complexity": complexity
            }

        except Exception as e:
            logger.error(f"Error getting game details from BGG: {e}")
            return None

    def find_publisher_website(self, bgg_id: int) -> Optional[str]:
        """
        Extract publisher website link from BGG page

        Args:
            bgg_id: BoardGameGeek game ID

        Returns:
            Publisher website URL or None if not found
        """
        try:
            # Get the main game page
            game_url = f"{self.site_base}/boardgame/{bgg_id}"
            logger.info(f"[BGG] Checking game page: {game_url}")
            response = requests.get(game_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            content = response.text

            # Strategy 1: Parse JSON data embedded in the page
            # BGG embeds game data in JavaScript objects like: "website":{"url":"...","title":"..."}
            website_match = re.search(r'"website":\s*\{\s*"url":\s*"([^"]+)"', content)
            if website_match:
                website_url = website_match.group(1)
                # Unescape JSON string (e.g., \/ -> /)
                website_url = website_url.replace('\\/', '/')
                logger.info(f"[BGG] Found publisher website in JSON data: {website_url}")
                return website_url

            # Strategy 2: Look for HTML links
            soup = BeautifulSoup(content, 'html.parser')

            # Look for external links section
            # Common patterns: "Official Website", "Publisher Website", etc.
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True).lower()
                href = link['href']

                # Skip BGG internal links
                if 'boardgamegeek.com' in href:
                    continue

                # Look for website-related text
                if any(keyword in link_text for keyword in ['official', 'website', 'publisher', 'homepage']):
                    # Make absolute URL if needed
                    if href.startswith('http'):
                        logger.info(f"[BGG] Found publisher website in HTML link: {href}")
                        return href

            # Strategy 3: Look for links in the credits/designer area
            # BGG usually has a "Web" or "Link" icon near publisher info
            for link in soup.find_all('a', href=re.compile(r'^https?://(?!.*boardgamegeek\.com)')):
                # If it's not a BGG link and looks like a website
                href = link['href']
                # Exclude social media, videos, etc.
                if not any(x in href.lower() for x in ['youtube', 'facebook', 'twitter', 'instagram', 'kickstarter']):
                    logger.info(f"[BGG] Found potential website link in HTML: {href}")
                    return href

            logger.info(f"[BGG] No publisher website found on BGG page")
            return None

        except Exception as e:
            logger.info(f"[BGG] Error finding publisher website: {e}")
            return None

    def search_website_for_rulebook(self, website_url: str, game_name: str) -> Optional[str]:
        """
        Search a publisher website for rulebook PDF

        Args:
            website_url: Publisher website URL
            game_name: Name of the game to search for

        Returns:
            URL to rulebook PDF or None if not found
        """
        try:
            logger.info(f"[BGG] Searching website for rulebook: {website_url}")
            response = requests.get(website_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # PDF link patterns
            pdf_patterns = [
                r'rulebook.*\.pdf',
                r'rules.*\.pdf',
                r'manual.*\.pdf',
                r'instructions.*\.pdf',
                r'.*rule.*\.pdf'
            ]

            # Find all PDF links
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Check if it's a PDF link
                if any(re.search(pattern, href, re.IGNORECASE) for pattern in pdf_patterns):
                    # Make absolute URL
                    pdf_url = urljoin(website_url, href)
                    pdf_links.append((pdf_url, link.get_text(strip=True)))
                    logger.info(f"[BGG] Found PDF: {pdf_url} ({link.get_text(strip=True)})")

            # Prioritize links with game name or "rule" in the text/URL
            for pdf_url, link_text in pdf_links:
                combined = f"{pdf_url} {link_text}".lower()
                if any(word in combined for word in game_name.lower().split()):
                    logger.info(f"[BGG] Selected PDF (matches game name): {pdf_url}")
                    return pdf_url

            # Return first rulebook PDF if any found
            if pdf_links:
                selected_url = pdf_links[0][0]
                logger.info(f"[BGG] Selected first PDF found: {selected_url}")
                return selected_url

            logger.info(f"[BGG] No PDFs found on publisher website")
            return None

        except Exception as e:
            logger.info(f"[BGG] Error searching website for rulebook: {e}")
            return None

    def find_rulebook_pdf(self, bgg_id: int, game_name: Optional[str] = None) -> Optional[str]:
        """
        Find rulebook PDF URL for a game

        Tries multiple strategies:
        1. BGG Files section
        2. Publisher website (if linked from BGG)

        Args:
            bgg_id: BoardGameGeek game ID
            game_name: Optional game name to help matching

        Returns:
            URL to rulebook PDF or None if not found
        """
        logger.info(f"[BGG] Starting rulebook search for BGG ID {bgg_id}")

        try:
            # Strategy 1: Check BGG Files section
            logger.info(f"[BGG] Strategy 1: Checking BGG Files section")
            files_url = f"{self.site_base}/boardgame/{bgg_id}/files"
            response = requests.get(files_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for PDF links (common patterns)
            pdf_patterns = [
                r'rulebook.*\.pdf',
                r'rules.*\.pdf',
                r'manual.*\.pdf',
                r'.*rules.*\.pdf'
            ]

            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Check if it's a PDF link
                if any(re.search(pattern, href, re.IGNORECASE) for pattern in pdf_patterns):
                    # Make absolute URL
                    pdf_url = urljoin(self.site_base, href)
                    logger.info(f"[BGG] Found PDF in Files section: {pdf_url}")
                    return pdf_url

            # Alternative: Check for BGG file links
            for link in soup.find_all('a', href=re.compile(r'/filepage/\d+')):
                # Visit the file page to get actual PDF link
                file_page_url = urljoin(self.site_base, link['href'])
                logger.info(f"[BGG] Checking file page: {file_page_url}")
                file_response = requests.get(file_page_url, headers=self.headers, timeout=10)
                file_soup = BeautifulSoup(file_response.content, 'html.parser')

                # Find download link
                download_link = file_soup.find('a', href=re.compile(r'.*\.pdf$', re.IGNORECASE))
                if download_link:
                    pdf_url = urljoin(self.site_base, download_link['href'])
                    logger.info(f"[BGG] Found PDF via file page: {pdf_url}")
                    return pdf_url

            logger.info(f"[BGG] No PDF found in BGG Files section")

            # Strategy 2: Check publisher website
            logger.info(f"[BGG] Strategy 2: Checking publisher website")
            publisher_website = self.find_publisher_website(bgg_id)

            if publisher_website and game_name:
                pdf_url = self.search_website_for_rulebook(publisher_website, game_name)
                if pdf_url:
                    return pdf_url

            logger.info(f"[BGG] No rulebook PDF found via any strategy")
            return None

        except Exception as e:
            logger.info(f"[BGG] Error finding rulebook PDF: {e}")
            return None

    def download_pdf(self, url: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Download a PDF file

        Args:
            url: URL to PDF
            filename: Optional custom filename (defaults to URL basename)

        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Generate filename from URL if not provided
            if filename is None:
                parsed_url = urlparse(url)
                filename = Path(parsed_url.path).name

                # Ensure .pdf extension
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'

            # Download PDF
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()

            # Save to file
            file_path = self.downloads_dir / filename
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return str(file_path)

        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return None

    def get_game_and_rulebook(self, bgg_id: int) -> Optional[Dict[str, Any]]:
        """
        Get game details and download rulebook in one operation

        Args:
            bgg_id: BoardGameGeek game ID

        Returns:
            Dict with game details and pdf_path, or None if failed
        """
        # Get game details
        game_details = self.get_game_details(bgg_id)
        if not game_details:
            return None

        # Find and download rulebook (pass game name to help with matching)
        pdf_url = self.find_rulebook_pdf(bgg_id, game_details.get('name'))
        pdf_path = None

        if pdf_url:
            # Generate filename from game name
            safe_name = re.sub(r'[^\w\s-]', '', game_details['name'])
            safe_name = re.sub(r'[-\s]+', '-', safe_name)
            filename = f"{safe_name}-{bgg_id}-rules.pdf"

            pdf_path = self.download_pdf(pdf_url, filename)

        result = {**game_details, "pdf_path": pdf_path, "pdf_url": pdf_url}
        return result
