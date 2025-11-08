"""Web of Science search provider"""

import re
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus, urlencode

from src.models import Paper, SearchQuery, Source, Author, PaperType
from src.search.base import BaseSearchProvider


class WebOfScienceProvider(BaseSearchProvider):
    """Search provider for Web of Science (via UCSB proxy)"""

    def __init__(self, rate_limit: float = 0.5, ucsb_session: Optional[requests.Session] = None):
        """
        Initialize Web of Science provider

        Args:
            rate_limit: Requests per second
            ucsb_session: UCSB authenticated session (required for access)
        """
        super().__init__(rate_limit)
        self.source = Source.WEB_OF_SCIENCE
        self.session = ucsb_session if ucsb_session else requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

        # UCSB proxy URL for Web of Science
        self.base_url = "https://www-webofscience-com.proxy.library.ucsb.edu"
        self.search_url = f"{self.base_url}/wos/woscc/basic-search"

        # Check if we have UCSB session
        self.has_ucsb_access = hasattr(self.session, 'cookies') and len(self.session.cookies) > 0

    def search(self, query: SearchQuery) -> List[Paper]:
        """
        Search Web of Science via UCSB proxy

        Args:
            query: Search query parameters

        Returns:
            List of papers
        """
        papers = []

        if not self.has_ucsb_access:
            print("⚠ Web of Science requires UCSB authentication - skipping")
            return papers

        try:
            # Build query parameters for WoS
            search_params = {
                'value(input1)': query.query,
                'value(select1)': 'TS',  # Topic search (title, abstract, keywords)
                'value(bool_1_2)': 'AND',
                'limitStatus': 'collapsed',
                'expand': 'false',
                'citationCount': 'true',
            }

            # Add year range if specified
            if query.year_start or query.year_end:
                year_start = query.year_start or 1900
                year_end = query.year_end or 2100
                search_params['timeSpan'] = f'{year_start}-{year_end}'
                search_params['edition'] = 'SCI'

            # Make request with rate limiting
            self.rate_limiter.wait()

            # First, access the search page to get session
            response = self.session.get(self.search_url, timeout=15)

            if response.status_code != 200:
                print(f"⚠ Web of Science: Access denied (status {response.status_code})")
                return papers

            # Since WoS uses complex JavaScript/AJAX, we'll use an alternative approach
            # Try to access via OpenURL or DOI resolution
            papers = self._search_via_api_alternative(query)

            print(f"✓ Web of Science: Found {len(papers)} papers")

        except Exception as e:
            print(f"✗ Web of Science search failed: {e}")

        return papers

    def _search_via_api_alternative(self, query: SearchQuery) -> List[Paper]:
        """
        Alternative search method using WoS Lite API or exports

        This is a simplified version that searches via the web interface
        """
        papers = []

        try:
            # Construct search URL for WoS Lite/Advanced search
            search_term = quote_plus(query.query)

            # Use the summary format which is easier to parse
            wos_search_url = (
                f"{self.base_url}/wos/woscc/summary/"
                f"{search_term}/relevance/1"
            )

            self.rate_limiter.wait()
            response = self.session.get(wos_search_url, timeout=15, allow_redirects=True)

            if response.status_code == 200:
                # Parse the HTML response
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for result entries (this is approximate - WoS structure varies)
                # Try multiple selectors
                result_divs = (
                    soup.find_all('div', class_='search-results-data-item') or
                    soup.find_all('div', class_='search-result') or
                    soup.find_all('app-summary-record') or
                    []
                )

                limit = min(query.max_results, 20)
                for result_div in result_divs[:limit]:
                    paper = self._parse_wos_result(result_div)
                    if paper:
                        papers.append(paper)

        except Exception as e:
            print(f"⚠ WoS alternative search error: {e}")

        return papers

    def _parse_wos_result(self, result_elem) -> Optional[Paper]:
        """Parse a Web of Science result entry"""

        try:
            # Extract title
            title_elem = (
                result_elem.find('span', class_='title') or
                result_elem.find('a', class_='article-title') or
                result_elem.find('h3')
            )

            if not title_elem:
                return None

            title = self._clean_text(title_elem.get_text())

            # Extract authors
            authors = []
            author_elem = (
                result_elem.find('div', class_='authors') or
                result_elem.find('span', class_='authors')
            )

            if author_elem:
                author_text = author_elem.get_text()
                # Authors are usually separated by semicolons in WoS
                author_names = [a.strip() for a in re.split(r'[;,]', author_text)]
                authors = [Author(name=name) for name in author_names[:10] if name]

            # Extract year
            year = None
            year_elem = result_elem.find('span', class_='year')
            if year_elem:
                year_text = year_elem.get_text()
                year_match = re.search(r'(19|20)\d{2}', year_text)
                if year_match:
                    year = int(year_match.group())

            # Extract journal
            journal = None
            journal_elem = (
                result_elem.find('span', class_='source') or
                result_elem.find('i')
            )
            if journal_elem:
                journal = self._clean_text(journal_elem.get_text())

            # Extract citation count
            citations = 0
            cite_elem = result_elem.find('span', class_='citation-count')
            if cite_elem:
                cite_text = cite_elem.get_text()
                cite_match = re.search(r'\d+', cite_text)
                if cite_match:
                    citations = int(cite_match.group())

            # Extract DOI
            doi = None
            doi_elem = result_elem.find('span', class_='doi') or result_elem.find('a', href=re.compile(r'doi\.org'))
            if doi_elem:
                doi_text = doi_elem.get_text() if hasattr(doi_elem, 'get_text') else doi_elem.get('href', '')
                doi_match = re.search(r'10\.\d{4,}/[^\s]+', doi_text)
                if doi_match:
                    doi = doi_match.group()

            # Extract abstract if available
            abstract = None
            abstract_elem = result_elem.find('div', class_='abstract') or result_elem.find('p', class_='abstract')
            if abstract_elem:
                abstract = self._clean_text(abstract_elem.get_text())

            # Construct URL
            url = None
            if doi:
                url = f"https://doi.org/{doi}"

            paper = Paper(
                title=title,
                doi=doi,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                citations=citations,
                url=url,
                sources=[Source.WEB_OF_SCIENCE],
                paper_type=PaperType.ARTICLE
            )

            return paper

        except Exception as e:
            print(f"⚠ Failed to parse WoS result: {e}")
            return None

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Get paper by WoS accession number

        Args:
            paper_id: WoS accession number (UT)

        Returns:
            Paper if found
        """
        if not self.has_ucsb_access:
            return None

        try:
            # Construct URL for specific record
            record_url = f"{self.base_url}/wos/woscc/full-record/{paper_id}"

            self.rate_limiter.wait()
            response = self.session.get(record_url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Parse the full record page
                # This would need detailed implementation based on WoS HTML structure
                pass

        except Exception as e:
            print(f"✗ Failed to get WoS paper: {e}")

        return None
