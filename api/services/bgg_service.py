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
            print(f"Error searching BGG: {e}")
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
            print(f"Error getting game details from BGG: {e}")
            return None

    def find_rulebook_pdf(self, bgg_id: int) -> Optional[str]:
        """
        Find rulebook PDF URL for a game

        Scrapes the BGG game page to find PDF links in the Files section.

        Args:
            bgg_id: BoardGameGeek game ID

        Returns:
            URL to rulebook PDF or None if not found
        """
        try:
            # Get the game's files page
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
                    return pdf_url

            # Alternative: Check for BGG file links
            for link in soup.find_all('a', href=re.compile(r'/filepage/\d+')):
                # Visit the file page to get actual PDF link
                file_page_url = urljoin(self.site_base, link['href'])
                file_response = requests.get(file_page_url, headers=self.headers, timeout=10)
                file_soup = BeautifulSoup(file_response.content, 'html.parser')

                # Find download link
                download_link = file_soup.find('a', href=re.compile(r'.*\.pdf$', re.IGNORECASE))
                if download_link:
                    pdf_url = urljoin(self.site_base, download_link['href'])
                    return pdf_url

            return None

        except Exception as e:
            print(f"Error finding rulebook PDF: {e}")
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
            print(f"Error downloading PDF: {e}")
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

        # Find and download rulebook
        pdf_url = self.find_rulebook_pdf(bgg_id)
        pdf_path = None

        if pdf_url:
            # Generate filename from game name
            safe_name = re.sub(r'[^\w\s-]', '', game_details['name'])
            safe_name = re.sub(r'[-\s]+', '-', safe_name)
            filename = f"{safe_name}-{bgg_id}-rules.pdf"

            pdf_path = self.download_pdf(pdf_url, filename)

        result = {**game_details, "pdf_path": pdf_path, "pdf_url": pdf_url}
        return result
