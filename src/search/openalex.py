"""OpenAlex search provider with official API"""

import requests
from typing import List, Optional
from src.models import Paper, SearchQuery, Source, Author, PaperType
from src.search.base import BaseSearchProvider


class OpenAlexProvider(BaseSearchProvider):
    """Search provider for OpenAlex with official API"""

    def __init__(self, email: Optional[str] = None):
        """
        Initialize OpenAlex provider

        Args:
            email: Optional email for polite pool (faster rate limits and better caching)
        """
        super().__init__(rate_limit=10.0)  # 10 requests per second allowed
        self.source = Source.OPENALEX
        self.base_url = "https://api.openalex.org"
        self.email = email

        # Add polite pool headers if email provided
        self.headers = {}
        if email:
            self.headers['User-Agent'] = f'mailto:{email}'

    def search(self, query: SearchQuery) -> List[Paper]:
        """
        Search OpenAlex using official API

        Args:
            query: Search query parameters

        Returns:
            List of papers with citation network data
        """
        papers = []

        try:
            self.rate_limiter.wait_if_needed()

            # Build filter parameters
            filters = []

            # Add search query filter
            # OpenAlex uses 'search' parameter for full-text search
            params = {
                'search': query.query,
                'per-page': min(query.max_results, 100),  # Max 100 per page
            }

            # Add year filter if specified
            if query.year_start or query.year_end:
                year_start = query.year_start or 1900
                year_end = query.year_end or 2025
                filters.append(f'publication_year:{year_start}-{year_end}')

            # Add filters to params
            if filters:
                params['filter'] = ','.join(filters)

            # Make request
            response = requests.get(
                f"{self.base_url}/works",
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()

            # Parse papers
            for item in data.get('results', []):
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

            print(f"✓ OpenAlex: Found {len(papers)} papers")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"⚠ OpenAlex rate limited. Consider adding email for polite pool.")
            else:
                print(f"✗ OpenAlex HTTP error: {e}")
        except Exception as e:
            print(f"✗ OpenAlex search failed: {e}")

        return papers

    def _parse_paper(self, item: dict) -> Optional[Paper]:
        """
        Parse OpenAlex API response

        Args:
            item: Work data from API

        Returns:
            Paper object with citation network data
        """
        try:
            # Extract title
            title = item.get('title', 'Untitled')

            # Extract DOI
            doi = item.get('doi')
            if doi and doi.startswith('https://doi.org/'):
                doi = doi.replace('https://doi.org/', '')

            # Extract authors
            authors = []
            authorships = item.get('authorships', [])
            for authorship in authorships:
                author_data = authorship.get('author', {})
                author_name = author_data.get('display_name', 'Unknown')

                # Extract affiliation if available
                institutions = authorship.get('institutions', [])
                affiliation = None
                if institutions:
                    affiliation = institutions[0].get('display_name')

                authors.append(Author(
                    name=author_name,
                    affiliation=affiliation,
                    orcid=author_data.get('orcid')
                ))

            # Extract publication year
            year = item.get('publication_year')

            # Extract journal/venue
            journal = None
            primary_location = item.get('primary_location', {})
            if primary_location:
                source = primary_location.get('source', {})
                if source:
                    journal = source.get('display_name')

            # Extract abstract (inverted index format)
            abstract = self._extract_abstract(item.get('abstract_inverted_index'))

            # Extract keywords/concepts
            keywords = []
            concepts = item.get('concepts', [])
            for concept in concepts[:10]:  # Limit to top 10
                if concept.get('score', 0) > 0.3:  # Only high-confidence concepts
                    keywords.append(concept.get('display_name', ''))

            # Extract external IDs
            ids = item.get('ids', {})
            pmid = ids.get('pmid')
            if pmid and pmid.startswith('https://pubmed.ncbi.nlm.nih.gov/'):
                pmid = pmid.replace('https://pubmed.ncbi.nlm.nih.gov/', '')

            # Extract PDF URL
            pdf_url = None
            if primary_location:
                url = primary_location.get('pdf_url')
                if url and url.strip():  # Only set if non-empty
                    pdf_url = url
            if not pdf_url:
                # Check alternative locations
                for location in item.get('locations', []):
                    url = location.get('pdf_url')
                    if url and url.strip():  # Only set if non-empty
                        pdf_url = url
                        break

            # Extract citation count
            citations = item.get('cited_by_count', 0)

            # Determine paper type
            paper_type = self._determine_paper_type(item)

            # Extract URL
            url = item.get('doi', item.get('id'))  # Use DOI or OpenAlex ID

            return Paper(
                title=title,
                doi=doi,
                pmid=pmid,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                keywords=keywords,
                citations=citations,
                url=url,
                pdf_url=pdf_url,
                sources=[Source.OPENALEX],
                paper_type=paper_type
            )
        except Exception as e:
            print(f"⚠ Failed to parse OpenAlex paper: {e}")
            return None

    def _extract_abstract(self, inverted_index: Optional[dict]) -> Optional[str]:
        """
        Convert OpenAlex inverted index format to plain text

        Args:
            inverted_index: Inverted index from API

        Returns:
            Plain text abstract
        """
        if not inverted_index:
            return None

        try:
            # Inverted index format: {"word": [positions...]}
            # Reconstruct by creating list of (position, word) and sorting
            words_with_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    words_with_positions.append((pos, word))

            # Sort by position and join
            words_with_positions.sort(key=lambda x: x[0])
            abstract = ' '.join(word for _, word in words_with_positions)

            # Limit length
            if len(abstract) > 5000:
                abstract = abstract[:5000] + '...'

            return abstract
        except Exception:
            return None

    def _determine_paper_type(self, item: dict) -> PaperType:
        """
        Determine paper type from OpenAlex data

        Args:
            item: Work data

        Returns:
            Paper type
        """
        type_str = item.get('type', '').lower()

        if 'review' in type_str:
            return PaperType.REVIEW
        elif type_str in ['proceedings-article', 'conference-paper']:
            return PaperType.CONFERENCE
        elif type_str == 'book-chapter':
            return PaperType.BOOK_CHAPTER
        elif type_str == 'dissertation':
            return PaperType.THESIS
        elif type_str in ['article', 'journal-article']:
            return PaperType.ARTICLE
        elif type_str == 'preprint':
            return PaperType.PREPRINT
        else:
            return PaperType.UNKNOWN

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Get paper by OpenAlex ID or DOI

        Args:
            paper_id: Paper identifier (OpenAlex ID or DOI)

        Returns:
            Paper if found
        """
        try:
            self.rate_limiter.wait_if_needed()

            # Convert DOI to OpenAlex format if needed
            if not paper_id.startswith('W') and not paper_id.startswith('https://'):
                # Assume it's a DOI
                paper_id = f'https://doi.org/{paper_id}'

            response = requests.get(
                f"{self.base_url}/works/{paper_id}",
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()

            return self._parse_paper(response.json())
        except Exception as e:
            print(f"✗ Failed to get paper {paper_id}: {e}")
            return None

    def get_citations(self, paper_id: str, limit: int = 100) -> List[Paper]:
        """
        Get papers that cite this paper

        Args:
            paper_id: OpenAlex work ID
            limit: Number of citations to retrieve

        Returns:
            List of citing papers
        """
        papers = []

        try:
            self.rate_limiter.wait_if_needed()

            # Search for papers that cite this work
            params = {
                'filter': f'cites:{paper_id}',
                'per-page': min(limit, 100)
            }

            response = requests.get(
                f"{self.base_url}/works",
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()
            for item in data.get('results', []):
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

        except Exception as e:
            print(f"✗ Failed to get citations: {e}")

        return papers

    def get_references(self, paper_id: str, limit: int = 100) -> List[Paper]:
        """
        Get papers that this paper cites

        Args:
            paper_id: OpenAlex work ID
            limit: Number of references to retrieve

        Returns:
            List of referenced papers
        """
        papers = []

        try:
            self.rate_limiter.wait_if_needed()

            # Search for papers cited by this work
            params = {
                'filter': f'cited_by:{paper_id}',
                'per-page': min(limit, 100)
            }

            response = requests.get(
                f"{self.base_url}/works",
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()
            for item in data.get('results', []):
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

        except Exception as e:
            print(f"✗ Failed to get references: {e}")

        return papers

    def get_related_papers(self, paper_id: str, limit: int = 10) -> List[Paper]:
        """
        Get related papers using concept similarity

        Args:
            paper_id: OpenAlex work ID
            limit: Number of related papers

        Returns:
            List of related papers
        """
        papers = []

        try:
            # First get the paper's concepts
            paper = self.get_paper_by_id(paper_id)
            if not paper or not paper.keywords:
                return papers

            # Search for papers with similar concepts
            self.rate_limiter.wait_if_needed()

            # Use first few keywords as search terms
            search_terms = ' '.join(paper.keywords[:3])

            params = {
                'search': search_terms,
                'per-page': limit
            }

            response = requests.get(
                f"{self.base_url}/works",
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()
            for item in data.get('results', []):
                related_paper = self._parse_paper(item)
                if related_paper and related_paper.title != paper.title:
                    papers.append(related_paper)

        except Exception as e:
            print(f"✗ Failed to get related papers: {e}")

        return papers
