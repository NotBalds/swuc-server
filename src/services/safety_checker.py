# safety_checker.py
import requests
from logging import debug, info, warning, error
from typing import List, Dict

class SafetyChecker:
    def __init__(self, api_key: str):
        self.api_key = api_key
        info("SafetyChecker initialized with API key: %s", api_key[:4]+"***")

    def check_batch(self, urls: List[str], batch_size: int = 500) -> Dict[str, bool]:
        """Batch URL safety check"""
        info("Starting safety check for %d URLs", len(urls))
        results = {}
        for batch_num, i in enumerate(range(0, len(urls), batch_size), 1):
            batch = urls[i:i+batch_size]
            debug("Processing batch %d with %d URLs", batch_num, len(batch))
            
            payload = {
                "client": {"clientId": "version_checker", "clientVersion": "1.0"},
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
                    "threatEntries": [{"url": url} for url in batch]
                }
            }
            
            try:
                response = requests.post(
                    "https://sba.yandex.net/v4/threatMatches:find",
                    params={"key": self.api_key},
                    json=payload,
                    timeout=15
                )
                debug("Safety API response for batch %d: %d", 
                            batch_num, response.status_code)
                batch_result = self.process_batch(response.json(), batch)
                results.update(batch_result)
                
                safe_count = sum(batch_result.values())
                info("Batch %d: %d/%d URLs safe", 
                           batch_num, safe_count, len(batch))
                
            except Exception as e:
                error("Safety check failed for batch %d: %s", 
                            batch_num, str(e), exc_info=True)
                results.update({url: False for url in batch})
        return results

    def process_batch(self, response_data: Dict, batch: List[str]) -> Dict[str, bool]:
        """Process safety check response"""
        safe_results = {url: True for url in batch}
        if "matches" in response_data:
            unsafe_count = len(response_data["matches"])
            warning("Found %d unsafe URLs in batch", unsafe_count)
            for match in response_data["matches"]:
                unsafe_url = match["threat"]["url"]
                safe_results[unsafe_url] = False
                debug("Marked as unsafe: %s", unsafe_url)
        return safe_results
