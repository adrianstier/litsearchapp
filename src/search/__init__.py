"""Search module for various academic databases"""

from .pubmed import PubMedSearch
from .arxiv import ArxivSearch
from .crossref import CrossrefSearch

__all__ = ["PubMedSearch", "ArxivSearch", "CrossrefSearch"]