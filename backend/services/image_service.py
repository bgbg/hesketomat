"""Image service for extracting images from web search results."""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ImageService:
    """Service for extracting and formatting images from search results."""

    def extract_images_from_tavily(self, tavily_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract images from Tavily search response.

        Args:
            tavily_response: Raw response from Tavily API

        Returns:
            List of formatted image results
        """
        images = []

        try:
            # Tavily returns images as a list of URLs
            for img_url in tavily_response.get("images", []):
                images.append({
                    "url": img_url,
                    "thumbnail_url": img_url,  # Use same URL for thumbnail
                    "title": None,  # Tavily doesn't provide image titles
                    "source_url": None,  # Tavily doesn't provide source page
                })

            logger.info(f"Extracted {len(images)} images from Tavily response")
            return images

        except Exception as e:
            logger.error(f"Error extracting images from Tavily response: {e}", exc_info=True)
            return []

    def filter_images(self, images: List[Dict[str, Any]], max_count: int = 10) -> List[Dict[str, Any]]:
        """Filter and limit images."""
        return images[:max_count]


# Global image service instance
image_service = ImageService()
