"""Tavily search service for web search integration."""
import logging
import os
from typing import List, Dict, Any, Optional
from tavily import TavilyClient

logger = logging.getLogger(__name__)


class SearchService:
    """Service for web search using Tavily API."""

    def __init__(self):
        """Initialize Tavily search client."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            logger.warning("TAVILY_API_KEY not found in environment")
            self.client = None
        else:
            self.client = TavilyClient(api_key=api_key)
            logger.info("Tavily search client initialized")

    def search(
        self,
        query: str,
        max_results: int = 10,
        include_images: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform web search using Tavily.

        Returns:
            Dict with keys:
            - results: List of search results with title, url, snippet, domain
            - images: List of image results (if include_images=True)
            - raw_results: Full Tavily response for debugging
        """
        if not self.client:
            raise ValueError("Tavily client not initialized. Check TAVILY_API_KEY.")

        try:
            logger.info(f"Searching Tavily for: {query}")

            # Perform search with Tavily
            response = self.client.search(
                query=query,
                max_results=max_results,
                include_images=include_images,
                include_answer=False,  # We'll generate our own summary with LLM
            )

            # Extract and format web results
            web_results = []
            for result in response.get("results", []):
                web_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", ""),
                    "domain": self._extract_domain(result.get("url", "")),
                })

            # Extract and format image results
            image_results = []
            if include_images:
                for img in response.get("images", []):
                    image_results.append({
                        "url": img,
                        "thumbnail_url": img,  # Tavily returns image URLs directly
                        "title": None,
                        "source_url": None,
                    })

            logger.info(f"Found {len(web_results)} results and {len(image_results)} images")

            return {
                "results": web_results,
                "images": image_results,
                "raw_results": response,
            }

        except Exception as e:
            logger.error(f"Tavily search error for query '{query}': {e}", exc_info=True)
            raise

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix if present
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return url


# Global search service instance
search_service = SearchService()
