"""Google Scholar search provider"""

import re
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus

from src.models import Paper, SearchQuery, Source, Author, PaperType
from src.search.base import BaseSearchProvider


class GoogleScholarProvider(BaseSearchProvider):
    """Search provider for Google Scholar"""

    def __init__(self, rate_limit: float = 0.5, ucsb_session: Optional[requests.Session] = None):
        """
        Initialize Google Scholar provider

        Args:
            rate_limit: Requests per second (be conservative with Scholar)
            ucsb_session: Optional UCSB authenticated session for better access
        """
        super().__init__(rate_limit)
        self.source = Source.GOOGLE_SCHOLAR
        self.session = ucsb_session if ucsb_session else requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.base_url = "https://scholar.google.com/scholar"
        self.ucsb_proxy = "https://scholar-google-com.proxy.library.ucsb.edu/scholar"

    def search(self, query: SearchQuery) -> List[Paper]:
        """
        Search Google Scholar

        Args:
            query: Search query parameters

        Returns:
            List of papers
        """
        papers = []

        try:
            # Use UCSB proxy if session available
            search_url = self.ucsb_proxy if hasattr(self.session, 'cookies') and len(self.session.cookies) > 0 else self.base_url

            # Build search parameters
            params = {
                'q': query.query,
                'hl': 'en',
                'as_sdt': '0,5',  # Include patents: 0,5 means all types
            }

            # Add year range if specified
            if query.year_start:
                params['as_ylo'] = query.year_start
            if query.year_end:
                params['as_yhi'] = query.year_end

            # Limit results
            num_results = min(query.max_results, 20)  # Scholar limits results per page

            # Make request with rate limiting
            self.rate_limiter.wait()
            response = self.session.get(search_url, params=params, timeout=15)
            response.raise_for_status()

            # Parse results
            papers = self._parse_results(response.text, limit=num_results)

            print(f"✓ Google Scholar: Found {len(papers)} papers")

        except Exception as e:
            print(f"✗ Google Scholar search failed: {e}")

        return papers

    def _parse_results(self, html: str, limit: int = 20) -> List[Paper]:
        """Parse Google Scholar HTML results"""
        papers = []
        soup = BeautifulSoup(html, 'html.parser')

        # Find all result entries
        results = soup.find_all('div', class_='gs_ri')[:limit]

        for result in results:
            try:
                paper = self._parse_result_entry(result)
                if paper:
                    papers.append(paper)
            except Exception as e:
                print(f"⚠ Failed to parse Scholar result: {e}")
                continue

        return papers

    def _parse_result_entry(self, result) -> Optional[Paper]:
        """Parse a single Scholar result entry"""

        # Extract title
        title_elem = result.find('h3', class_='gs_rt')
        if not title_elem:
            return None

        # Remove citation link if present
        for citation in title_elem.find_all('span', class_='gs_ct1'):
            citation.decompose()
        for citation in title_elem.find_all('span', class_='gs_ct2'):
            citation.decompose()

        title = title_elem.get_text().strip()

        # Extract URL
        url = None
        title_link = title_elem.find('a')
        if title_link and title_link.get('href'):
            url = title_link['href']

        # Extract authors, year, journal from metadata line
        meta_elem = result.find('div', class_='gs_a')
        authors = []
        year = None
        journal = None

        if meta_elem:
            meta_text = meta_elem.get_text()
            # Format is usually: "Authors - Source, Year - Publisher"
            parts = meta_text.split(' - ')

            if len(parts) >= 1:
                # Parse authors
                author_text = parts[0].strip()
                author_names = [a.strip() for a in author_text.split(',')]
                authors = [Author(name=name) for name in author_names if name and not name.isdigit()]

            if len(parts) >= 2:
                # Parse source and year
                source_year = parts[1].strip()
                # Extract year (4 digits)
                year_match = re.search(r'\b(19|20)\d{2}\b', source_year)
                if year_match:
                    year = int(year_match.group())
                    # Journal is everything before the year
                    journal = source_year[:year_match.start()].strip().rstrip(',')

        # Extract abstract/snippet
        abstract_elem = result.find('div', class_='gs_rs')
        abstract = self._clean_text(abstract_elem.get_text()) if abstract_elem else None

        # Extract citation count
        citations = 0
        cite_elem = result.find('div', class_='gs_fl')
        if cite_elem:
            cite_link = cite_elem.find('a', string=re.compile(r'Cited by'))
            if cite_link:
                cite_text = cite_link.get_text()
                cite_match = re.search(r'Cited by (\d+)', cite_text)
                if cite_match:
                    citations = int(cite_match.group(1))

        # Try to extract DOI from URL or PDF link
        doi = None
        if url and 'doi.org' in url:
            doi_match = re.search(r'doi.org/(.+)$', url)
            if doi_match:
                doi = doi_match.group(1)

        # Extract PDF URL if available
        pdf_url = None
        pdf_link = result.find('div', class_='gs_ggs')
        if pdf_link:
            pdf_a = pdf_link.find('a')
            if pdf_a and pdf_a.get('href'):
                pdf_url = pdf_a['href']

        # Create paper object
        paper = Paper(
            title=title,
            doi=doi,
            authors=authors,
            year=year,
            journal=journal,
            abstract=abstract,
            citations=citations,
            url=url,
            pdf_url=pdf_url,
            sources=[Source.GOOGLE_SCHOLAR],
            paper_type=PaperType.ARTICLE
        )

        return paper

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Get paper by Scholar ID (not commonly used)

        Args:
            paper_id: Paper identifier

        Returns:
            Paper if found
        """
        # Scholar doesn't have reliable IDs, search by title instead
        return None
