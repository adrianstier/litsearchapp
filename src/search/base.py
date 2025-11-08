"""Base class for search providers"""

from abc import ABC, abstractmethod
from typing import List, Optional
import time
from src.models import Paper, SearchQuery, Source
from src.utils.rate_limiter import RateLimiter


class BaseSearchProvider(ABC):
    """Abstract base class for search providers"""

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize search provider

        Args:
            rate_limit: Requests per second
        """
        self.rate_limiter = RateLimiter(rate_limit)
        self.source = Source.PUBMED  # Override in subclass

    @abstractmethod
    def search(self, query: SearchQuery) -> List[Paper]:
        """
        Search for papers

        Args:
            query: Search query parameters

        Returns:
            List of papers
        """
        pass

    @abstractmethod
    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Get a specific paper by ID

        Args:
            paper_id: Paper identifier

        Returns:
            Paper if found, None otherwise
        """
        pass

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean and normalize text"""
        if not text:
            return None
        # Remove extra whitespace
        text = " ".join(text.split())
        # Remove common HTML entities
        text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        return text.strip() if text else None