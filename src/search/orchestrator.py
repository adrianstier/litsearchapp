"""Orchestrate searches across multiple sources"""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from src.models import Paper, SearchQuery, SearchResult, Source
from src.search.pubmed import PubMedSearch
from src.search.arxiv import ArxivSearch
from src.search.crossref import CrossrefSearch
from src.search.scholar import GoogleScholarProvider
from src.search.wos import WebOfScienceProvider
from src.search.deduplicator import Deduplicator
from src.utils.config import Config


class SearchOrchestrator:
    """Coordinate searches across multiple sources"""

    def __init__(self, ucsb_session=None):
        """
        Initialize search orchestrator

        Args:
            ucsb_session: Optional UCSB authenticated session for enhanced access
        """
        self.ucsb_session = ucsb_session
        self.providers = {
            Source.PUBMED: PubMedSearch(),
            Source.ARXIV: ArxivSearch(),
            Source.CROSSREF: CrossrefSearch(),
            Source.GOOGLE_SCHOLAR: GoogleScholarProvider(ucsb_session=ucsb_session),
            Source.WEB_OF_SCIENCE: WebOfScienceProvider(ucsb_session=ucsb_session),
        }
        self.deduplicator = Deduplicator()

    def search(self, query: SearchQuery) -> SearchResult:
        """
        Execute parallel searches across multiple sources

        Args:
            query: Search parameters

        Returns:
            Search results with deduplicated papers
        """
        start_time = time.time()
        results_by_source = {}
        errors = {}

        # Execute searches in parallel
        with ThreadPoolExecutor(max_workers=Config.MAX_CONCURRENT_REQUESTS) as executor:
            future_to_source = {}

            for source in query.sources:
                if source in self.providers:
                    future = executor.submit(self._search_source, source, query)
                    future_to_source[future] = source

            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    papers = future.result()
                    results_by_source[source] = papers
                    print(f"✓ {source.value}: {len(papers)} papers found")
                except Exception as e:
                    error_msg = str(e)
                    errors[source.value] = error_msg
                    print(f"✗ {source.value}: {error_msg}")
                    results_by_source[source] = []

        # Deduplicate and merge results
        all_papers = []
        for papers in results_by_source.values():
            all_papers.extend(papers)

        deduplicated_papers = self.deduplicator.deduplicate(all_papers)

        # Rank papers
        ranked_papers = self._rank_papers(deduplicated_papers, query)

        # Calculate total found (before deduplication)
        total_found = sum(len(papers) for papers in results_by_source.values())

        search_time = time.time() - start_time

        return SearchResult(
            query=query,
            papers=ranked_papers,
            total_found=total_found,
            sources_searched=list(results_by_source.keys()),
            search_time=search_time,
            errors=errors
        )

    def _search_source(self, source: Source, query: SearchQuery) -> List[Paper]:
        """Search a single source"""
        provider = self.providers.get(source)
        if not provider:
            raise ValueError(f"Unknown source: {source}")

        try:
            return provider.search(query)
        except Exception as e:
            raise Exception(f"Search failed: {e}")

    def _rank_papers(self, papers: List[Paper], query: SearchQuery) -> List[Paper]:
        """
        Rank papers by relevance

        Ranking factors:
        - Query term matches in title and abstract
        - Citation count (log scale)
        - Recency
        - Number of sources
        """
        import math
        from datetime import datetime

        query_terms = set(query.query.lower().split())
        current_year = datetime.now().year

        for paper in papers:
            score = 0.0

            # Title relevance (highest weight)
            title_lower = (paper.title or "").lower()
            title_matches = sum(1 for term in query_terms if term in title_lower)
            score += title_matches * 20

            # Abstract relevance
            if paper.abstract:
                abstract_lower = paper.abstract.lower()
                abstract_matches = sum(1 for term in query_terms if term in abstract_lower)
                score += abstract_matches * 5

            # Citation score (logarithmic)
            if paper.citations > 0:
                score += min(30, 5 * math.log10(paper.citations + 1))

            # Recency score
            if paper.year:
                years_old = current_year - paper.year
                if years_old <= 2:
                    score += 20
                elif years_old <= 5:
                    score += 15
                elif years_old <= 10:
                    score += 10
                elif years_old <= 20:
                    score += 5

            # Multi-source bonus
            score += len(paper.sources) * 10

            # Paper type bonus
            if query.paper_types and paper.paper_type in query.paper_types:
                score += 15

            paper.relevance_score = score

        # Sort by relevance score
        ranked = sorted(papers, key=lambda p: p.relevance_score or 0, reverse=True)

        return ranked

    def get_paper_by_id(self, identifier: str, source: Optional[Source] = None) -> Optional[Paper]:
        """
        Get a specific paper by identifier

        Args:
            identifier: Paper ID (PMID, DOI, arXiv ID)
            source: Optional source hint

        Returns:
            Paper if found
        """
        # Try to determine source from identifier
        if identifier.startswith("10."):  # Likely a DOI
            provider = self.providers.get(Source.CROSSREF)
            if provider:
                paper = provider.get_paper_by_id(identifier)
                if paper:
                    return paper

        # Try numeric ID as PMID
        if identifier.isdigit():
            provider = self.providers.get(Source.PUBMED)
            if provider:
                paper = provider.get_paper_by_id(identifier)
                if paper:
                    return paper

        # Try as arXiv ID
        if "arxiv" in identifier.lower() or identifier.count(".") == 1:
            provider = self.providers.get(Source.ARXIV)
            if provider:
                paper = provider.get_paper_by_id(identifier)
                if paper:
                    return paper

        # Try specific source if provided
        if source and source in self.providers:
            return self.providers[source].get_paper_by_id(identifier)

        return None