# search_manager.py
import requests
import xml.etree.ElementTree as ET
from logging import debug, info, warning, error
from urllib.parse import urlparse
from functools import lru_cache
from typing import List

class SearchManager:
    def __init__(self, folder_id: str, api_key: str):
        self.folder_id = folder_id
        self.api_key = api_key
        info("SearchManager initialized with folder ID: %s", folder_id[:4]+"***")

    @lru_cache(maxsize=128)
    def search_urls(self, query: str, max_results: int = 5) -> List[str]:
        """Execute search with result limitation"""
        info("Searching for '%s' with max %d results", query, max_results)
        params = {
            "folderid": self.folder_id,
            "apikey": self.api_key,
            "query": query,
            "groupby": f"attr=d.mode=deep.groups-on-page={max_results}.docs-in-group=1"
        }

        try:
            debug("Sending search request to Yandex XML API")
            response = requests.get(
                "https://yandex.ru/search/xml",
                params=params,
                timeout=10
            )
            info("Search API response status: %d", response.status_code)
            return self.parse_results(response.content, max_results)
        except Exception as e:
            error("Search request failed: %s", str(e), exc_info=True)
            return []

    def parse_results(self, xml_content: bytes, max_results: int) -> List[str]:
        """Parse XML search results"""
        debug("Parsing XML search results")
        urls = []
        try:
            root = ET.fromstring(xml_content)
            for url_elem in root.findall(".//url")[:max_results]:
                if url_elem.text:
                    parsed = urlparse(url_elem.text)
                    if parsed.netloc:
                        urls.append(url_elem.text)
                        debug("Found URL: %s", url_elem.text)
                    else:
                        warning("Invalid URL filtered: %s", url_elem.text)
            info("Parsed %d valid URLs from search results", len(urls))
        except ET.ParseError as e:
            error("XML parsing failed: %s", str(e), exc_info=True)
        return urls
