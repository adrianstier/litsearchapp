"""Crossref search implementation"""

import requests
from typing import List, Optional
from src.models import Paper, Author, SearchQuery, Source, PaperType
from src.search.base import BaseSearchProvider
from src.utils.config import Config


class CrossrefSearch(BaseSearchProvider):
    """Search Crossref for academic papers"""

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self):
        super().__init__(rate_limit=Config.CROSSREF_RATE_LIMIT)
        self.source = Source.CROSSREF
        self.session = requests.Session()
        if Config.CROSSREF_MAILTO:
            self.session.headers["User-Agent"] = f"LiteratureSearch/1.0 (mailto:{Config.CROSSREF_MAILTO})"

    def search(self, query: SearchQuery) -> List[Paper]:
        """Search Crossref for papers"""
        self.rate_limiter.wait_if_needed("crossref")

        params = self._build_params(query)

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            papers = []
            items = data.get("message", {}).get("items", [])
            for item in items:
                paper = self._convert_item(item)
                if paper:
                    papers.append(paper)

            return papers

        except Exception as e:
            print(f"Crossref search error: {e}")
            return []

    def get_paper_by_id(self, doi: str) -> Optional[Paper]:
        """Get a paper by DOI"""
        self.rate_limiter.wait_if_needed("crossref")

        try:
            response = self.session.get(
                f"{self.BASE_URL}/{doi}",
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            item = data.get("message")
            if item:
                return self._convert_item(item)
        except:
            pass
        return None

    def _build_params(self, query: SearchQuery) -> dict:
        """Build Crossref API parameters"""
        params = {
            "query": query.query,
            "rows": query.max_results,
        }

        # Add filters
        filters = []

        # Year filter
        if query.year_start or query.year_end:
            year_start = query.year_start or 1900
            year_end = query.year_end or 2100
            filters.append(f"from-pub-date:{year_start},until-pub-date:{year_end}")

        # Type filter
        if query.paper_types:
            type_mapping = {
                PaperType.ARTICLE: "journal-article",
                PaperType.CONFERENCE: "proceedings-article",
                PaperType.BOOK_CHAPTER: "book-chapter",
            }
            types = []
            for ptype in query.paper_types:
                if ptype in type_mapping:
                    types.append(type_mapping[ptype])
            if types:
                filters.append(f"type:{','.join(types)}")

        if filters:
            params["filter"] = ",".join(filters)

        # Sort
        if query.sort_by == "relevance":
            params["sort"] = "relevance"
        elif query.sort_by == "date":
            params["sort"] = "published"
        elif query.sort_by == "citations":
            params["sort"] = "is-referenced-by-count"

        return params

    def _convert_item(self, item: dict) -> Optional[Paper]:
        """Convert Crossref item to Paper model"""
        try:
            # Extract title
            titles = item.get("title", [])
            if not titles:
                return None
            title = self._clean_text(titles[0])

            # Extract authors
            authors = []
            for author_data in item.get("author", []):
                given = author_data.get("given", "")
                family = author_data.get("family", "")
                if family:
                    name = f"{given} {family}".strip()
                    authors.append(Author(
                        name=name,
                        first_name=given,
                        last_name=family,
                        affiliation=author_data.get("affiliation", [{}])[0].get("name") if author_data.get("affiliation") else None
                    ))

            # Extract year
            year = None
            date_parts = item.get("published-print", {}).get("date-parts", [[]])
            if not date_parts:
                date_parts = item.get("published-online", {}).get("date-parts", [[]])
            if date_parts and date_parts[0]:
                try:
                    year = int(date_parts[0][0])
                except:
                    pass

            # Extract journal
            journal = None
            container_titles = item.get("container-title", [])
            if container_titles:
                journal = container_titles[0]

            # Extract DOI
            doi = item.get("DOI")

            # Extract abstract
            abstract = item.get("abstract")
            if abstract:
                # Remove HTML tags from abstract
                import re
                abstract = re.sub('<[^<]+?>', '', abstract)
                abstract = self._clean_text(abstract)

            # Extract volume, issue, pages
            volume = item.get("volume")
            issue = item.get("issue")
            pages = item.get("page")

            # Extract citation count
            citations = item.get("is-referenced-by-count", 0)

            # Determine paper type
            paper_type = PaperType.UNKNOWN
            item_type = item.get("type", "")
            if "journal-article" in item_type:
                paper_type = PaperType.ARTICLE
            elif "proceedings" in item_type:
                paper_type = PaperType.CONFERENCE
            elif "book-chapter" in item_type:
                paper_type = PaperType.BOOK_CHAPTER

            # Build URL
            url = f"https://doi.org/{doi}" if doi else item.get("URL")

            return Paper(
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                volume=volume,
                issue=issue,
                pages=pages,
                abstract=abstract,
                doi=doi,
                citations=citations,
                paper_type=paper_type,
                url=url,
                sources=[self.source],
            )

        except Exception as e:
            print(f"Error converting Crossref item: {e}")
            return None