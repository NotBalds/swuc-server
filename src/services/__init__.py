from .search_manager import SearchManager
from .safety_checker import SafetyChecker
from .content_extractor import ContentExtractor
from .content_analyzer import ContentAnalyzer

from dotenv import load_dotenv
import os
from logging import info, warning, error
from typing import Dict, List

# Configure logging


class VersionFinder:
    def __init__(self):
        info("Initializing VersionFinder")
        load_dotenv()
        self.config = {
            "folder_id": os.getenv("YANDEX_FOLDER_ID", ""),
            "search_api_key": os.getenv("YANDEX_SEARCH_API_KEY", ""),
            "safety_api_key": os.getenv("YANDEX_SAFE_BROWSING_API_KEY", ""),
            "gpt_api_key": os.getenv("YANDEX_GPT_API_KEY", "")
        }
        
        self.search = SearchManager(
            self.config["folder_id"],
            self.config["search_api_key"]
        )
        self.safety = SafetyChecker(self.config["safety_api_key"])
        self.extractor = ContentExtractor()
        self.analyzer = ContentAnalyzer(
            self.config["folder_id"],
            self.config["gpt_api_key"]
        )

    def find_version(self, software_name: str, max_results: int = 5):
        """Full version search workflow with structured JSON output"""
        response_template = {
            "name": software_name,
            "sources": [],
            "version": None,
            "error": None,
            "analysis_time": None
        }
        
        try:
            # Step 1: Search for URLs
            info("Searching for URLs...")
            urls = self.search.search_urls(
                f"{software_name} latest version",
                max_results
            )
            response_template["metadata"]["urls_searched"] = len(urls)
            
            if not urls:
                response_template["error"] = "No search results found"
                return response_template

            # Step 2: Safety check (temporarily disabled)
            safe_urls = urls  # Bypassing safety check for now
            
            # Step 3: Content extraction
            contents: List[str] = []
            valid_urls: List[str] = []
            for url in safe_urls:
                content = self.extractor.get_content(url)
                if content and content.get("content"):
                    contents.append(content["content"])
                    valid_urls.append(url)
            
            response_template["sources"] = valid_urls
            response_template["metadata"]["urls_analyzed"] = len(valid_urls)
            
            if not contents:
                response_template["error"] = "No extractable content found"
                return response_template

            # Step 4: Version analysis
            version = self.analyzer.analyze(software_name, contents)
            if version:
                response_template["version"] = version
                response_template["metadata"]["analysis_time"] = "2023-12-20T00:00:00Z"  # Add actual timestamp
            else:
                response_template["error"] = "Version detection failed"

            return response_template

        except Exception as e:
            error("Version search failed: %s", str(e), exc_info=True)
            response_template["error"] = f"System error: {str(e)}"
            return response_template

