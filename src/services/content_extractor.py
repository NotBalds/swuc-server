# content_extractor.py
import requests
import re
from typing import Dict
from logging import debug, info, warning

class ContentExtractor:
    def __init__(self, max_chars: int = 5000):
        self.max_chars = max_chars
        info("ContentExtractor initialized with max %d characters", max_chars)

    def get_content(self, url: str) -> Dict:
        """Smart content extraction with cleanup"""
        info("Fetching content from: %s", url)
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            debug("Response status %d for %s", response.status_code, url)
            return self.clean_content(response.text, url)
        except Exception as e:
            warning("Failed to fetch content from %s: %s", url, str(e))
            return {"content": "", "url": url}

    def clean_content(self, html: str, url: str) -> Dict:
        """Clean and extract main content"""
        debug("Cleaning content from %s", url)
        # Remove script/style tags
        cleaned = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
        # Remove HTML tags
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        # Collapse whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        debug("Original length: %d, Cleaned length: %d", 
                    len(html), len(cleaned))

        if len(cleaned) > self.max_chars:
            cutoff = cleaned.rfind('.', self.max_chars//2, self.max_chars)
            if cutoff != -1:
                debug("Truncated to sentence boundary at position %d", cutoff)
                cleaned = cleaned[:cutoff+1]
            else:
                debug("Truncated to max %d characters", self.max_chars)
                cleaned = cleaned[:self.max_chars]
        
        info("Final content length for %s: %d characters", url, len(cleaned))
        info("Content: %s", cleaned)
        return {"content": cleaned, "url": url}
