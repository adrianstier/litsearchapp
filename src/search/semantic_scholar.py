"""Semantic Scholar search provider with official API"""

import requests
from typing import List, Optional
from src.models import Paper, SearchQuery, Source, Author, PaperType
from src.search.base import BaseSearchProvider


class SemanticScholarProvider(BaseSearchProvider):
    """Search provider for Semantic Scholar with official API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Semantic Scholar provider

        Args:
            api_key: Optional API key for higher rate limits (100 req/5min free, more with key)
        """
        super().__init__(rate_limit=2.0)  # 2 requests per second for free tier
        self.source = Source.SEMANTIC_SCHOLAR
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.api_key = api_key

        # Fields to request from API
        self.paper_fields = [
            'paperId',
            'title',
            'abstract',
            'authors',
            'year',
            'citationCount',
            'influentialCitationCount',  # AI-powered influential citations
            'url',
            'openAccessPdf',
            'publicationTypes',
            'publicationDate',
            'journal',
            'venue',
            's2FieldsOfStudy',  # Auto-categorized research topics
            'tldr',  # AI-generated summary
            'externalIds'  # DOI, ArXiv, PubMed IDs
        ]

    def search(self, query: SearchQuery) -> List[Paper]:
        """
        Search Semantic Scholar using official API

        Args:
            query: Search query parameters

        Returns:
            List of papers with AI-powered features
        """
        papers = []

        try:
            self.rate_limiter.wait_if_needed()

            # Build query string with filters
            query_str = query.query

            # Add year filter if specified
            if query.year_start or query.year_end:
                year_start = query.year_start or 1900
                year_end = query.year_end or 2025
                query_str = f"{query_str} year:{year_start}-{year_end}"

            # Build request parameters
            params = {
                'query': query_str,
                'limit': min(query.max_results, 100),  # API allows up to 100
                'fields': ','.join(self.paper_fields)
            }

            headers = {}
            if self.api_key:
                headers['x-api-key'] = self.api_key

            # Make request
            response = requests.get(
                f"{self.base_url}/paper/search",
                params=params,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()

            # Parse papers
            for item in data.get('data', []):
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

            print(f"✓ Semantic Scholar: Found {len(papers)} papers")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"⚠ Semantic Scholar rate limited. Consider using API key for higher limits.")
            else:
                print(f"✗ Semantic Scholar HTTP error: {e}")
        except Exception as e:
            print(f"✗ Semantic Scholar search failed: {e}")

        return papers

    def _parse_paper(self, item: dict) -> Optional[Paper]:
        """
        Parse Semantic Scholar API response

        Args:
            item: Paper data from API

        Returns:
            Paper object with rich metadata
        """
        try:
            # Extract authors
            authors = []
            for author_data in item.get('authors', []):
                authors.append(Author(name=author_data.get('name', 'Unknown')))

            # Extract external IDs (DOI, ArXiv, PubMed)
            external_ids = item.get('externalIds', {}) or {}
            doi = external_ids.get('DOI')
            arxiv_id = external_ids.get('ArXiv')
            pmid = external_ids.get('PubMed')

            # Extract PDF URL
            pdf_url = None
            if item.get('openAccessPdf'):
                url = item['openAccessPdf'].get('url')
                if url and url.strip():  # Only set if non-empty
                    pdf_url = url

            # Determine paper type
            paper_type = PaperType.ARTICLE
            pub_types = item.get('publicationTypes', []) or []
            if 'Review' in pub_types:
                paper_type = PaperType.REVIEW
            elif 'Conference' in pub_types:
                paper_type = PaperType.CONFERENCE

            # Extract journal/venue
            journal = item.get('journal', {})
            if isinstance(journal, dict):
                journal = journal.get('name')
            if not journal:
                journal = item.get('venue')

            # Extract keywords from AI-categorized fields
            keywords = []
            s2_fields = item.get('s2FieldsOfStudy', []) or []
            for field in s2_fields:
                if isinstance(field, dict):
                    keywords.append(field.get('category', ''))
                else:
                    keywords.append(str(field))

            # Build abstract - prefer TLDR if available
            abstract = item.get('abstract')
            tldr = item.get('tldr', {})
            if tldr and isinstance(tldr, dict):
                tldr_text = tldr.get('text')
                if tldr_text:
                    # Prepend AI summary to abstract
                    abstract = f"[AI Summary] {tldr_text}\n\n{abstract}" if abstract else f"[AI Summary] {tldr_text}"

            return Paper(
                title=item.get('title', 'Untitled'),
                doi=doi,
                pmid=pmid,
                arxiv_id=arxiv_id,
                authors=authors,
                year=item.get('year'),
                journal=journal,
                abstract=abstract,
                keywords=keywords,
                citations=item.get('citationCount', 0),
                url=item.get('url'),
                pdf_url=pdf_url,
                sources=[Source.SEMANTIC_SCHOLAR],
                paper_type=paper_type
            )
        except Exception as e:
            print(f"⚠ Failed to parse Semantic Scholar paper: {e}")
            return None

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Get paper by Semantic Scholar ID or DOI

        Args:
            paper_id: Paper identifier (S2 ID, DOI, ArXiv ID, or PubMed ID)

        Returns:
            Paper if found
        """
        try:
            self.rate_limiter.wait_if_needed()

            headers = {}
            if self.api_key:
                headers['x-api-key'] = self.api_key

            # API supports multiple ID types
            response = requests.get(
                f"{self.base_url}/paper/{paper_id}",
                params={'fields': ','.join(self.paper_fields)},
                headers=headers,
                timeout=15
            )
            response.raise_for_status()

            return self._parse_paper(response.json())
        except Exception as e:
            print(f"✗ Failed to get paper {paper_id}: {e}")
            return None

    def get_recommendations(self, paper_id: str, limit: int = 10) -> List[Paper]:
        """
        Get paper recommendations based on a seed paper

        Args:
            paper_id: Seed paper ID
            limit: Number of recommendations

        Returns:
            List of recommended papers
        """
        papers = []

        try:
            self.rate_limiter.wait_if_needed()

            headers = {}
            if self.api_key:
                headers['x-api-key'] = self.api_key

            response = requests.get(
                f"{self.base_url}/paper/{paper_id}/recommendations",
                params={
                    'fields': ','.join(self.paper_fields),
                    'limit': limit
                },
                headers=headers,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()
            for item in data.get('recommendedPapers', []):
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

            print(f"✓ Found {len(papers)} recommendations")

        except Exception as e:
            print(f"✗ Failed to get recommendations: {e}")

        return papers

    def get_citations(self, paper_id: str, limit: int = 100) -> List[Paper]:
        """
        Get papers that cite this paper

        Args:
            paper_id: Paper ID
            limit: Number of citations to retrieve

        Returns:
            List of citing papers
        """
        papers = []

        try:
            self.rate_limiter.wait_if_needed()

            headers = {}
            if self.api_key:
                headers['x-api-key'] = self.api_key

            response = requests.get(
                f"{self.base_url}/paper/{paper_id}/citations",
                params={
                    'fields': ','.join(self.paper_fields),
                    'limit': limit
                },
                headers=headers,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()
            for item in data.get('data', []):
                citing_paper = item.get('citingPaper', {})
                paper = self._parse_paper(citing_paper)
                if paper:
                    papers.append(paper)

        except Exception as e:
            print(f"✗ Failed to get citations: {e}")

        return papers
