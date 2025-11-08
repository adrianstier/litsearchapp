"""arXiv search implementation"""

import arxiv
from typing import List, Optional
from src.models import Paper, Author, SearchQuery, Source, PaperType
from src.search.base import BaseSearchProvider
from src.utils.config import Config


class ArxivSearch(BaseSearchProvider):
    """Search arXiv for preprints"""

    def __init__(self):
        super().__init__(rate_limit=Config.ARXIV_RATE_LIMIT)
        self.source = Source.ARXIV

    def search(self, query: SearchQuery) -> List[Paper]:
        """Search arXiv for papers"""
        # Build search query
        search_query = self._build_query(query)

        # Create arxiv search
        search = arxiv.Search(
            query=search_query,
            max_results=query.max_results,
            sort_by=arxiv.SortCriterion.Relevance if query.sort_by == "relevance" else arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers = []
        for result in search.results():
            self.rate_limiter.wait_if_needed("arxiv")
            paper = self._convert_result(result)
            if paper:
                papers.append(paper)

        return papers

    def get_paper_by_id(self, arxiv_id: str) -> Optional[Paper]:
        """Get a paper by arXiv ID"""
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(search.results())
            return self._convert_result(result)
        except:
            return None

    def _build_query(self, query: SearchQuery) -> str:
        """Build arXiv search query"""
        terms = [query.query]

        # Add author filters
        if query.authors:
            author_terms = [f'au:"{author}"' for author in query.authors]
            terms.append(f"({' OR '.join(author_terms)})")

        # Note: arXiv doesn't support year filtering in search query
        # We'll filter results after retrieval

        return " AND ".join(terms)

    def _convert_result(self, result: arxiv.Result) -> Optional[Paper]:
        """Convert arXiv result to Paper model"""
        try:
            # Extract authors
            authors = []
            for author in result.authors:
                authors.append(Author(name=str(author)))

            # Extract year from published date
            year = None
            if result.published:
                year = result.published.year

            # Build URLs
            url = result.entry_id
            pdf_url = result.pdf_url

            # Extract arxiv ID
            arxiv_id = result.get_short_id()

            return Paper(
                title=result.title,
                authors=authors,
                year=year,
                abstract=result.summary,
                arxiv_id=arxiv_id,
                paper_type=PaperType.PREPRINT,
                url=url,
                pdf_url=pdf_url,
                sources=[self.source],
                journal="arXiv",
            )

        except Exception as e:
            print(f"Error converting arXiv result: {e}")
            return None