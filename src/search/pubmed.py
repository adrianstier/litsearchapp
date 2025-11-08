"""PubMed search implementation using E-utilities"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict
from datetime import datetime
from src.models import Paper, Author, SearchQuery, Source, PaperType
from src.search.base import BaseSearchProvider
from src.utils.config import Config


class PubMedSearch(BaseSearchProvider):
    """Search PubMed via E-utilities API"""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def __init__(self):
        super().__init__(rate_limit=Config.PUBMED_RATE_LIMIT)
        self.source = Source.PUBMED

    def search(self, query: SearchQuery) -> List[Paper]:
        """Search PubMed for papers"""
        # Build search query
        search_term = self._build_query(query)

        # Step 1: Search for IDs
        ids = self._search_ids(search_term, query.max_results)
        if not ids:
            return []

        # Step 2: Fetch details for IDs
        papers = self._fetch_details(ids)

        # Add source information
        for paper in papers:
            paper.sources = [self.source]

        return papers

    def get_paper_by_id(self, pmid: str) -> Optional[Paper]:
        """Get a paper by PubMed ID"""
        papers = self._fetch_details([pmid])
        return papers[0] if papers else None

    def _build_query(self, query: SearchQuery) -> str:
        """Build PubMed search query"""
        terms = [query.query]

        # Add date range
        if query.year_start and query.year_end:
            terms.append(f"{query.year_start}:{query.year_end}[pdat]")
        elif query.year_start:
            terms.append(f"{query.year_start}:{datetime.now().year}[pdat]")
        elif query.year_end:
            terms.append(f"1900:{query.year_end}[pdat]")

        # Add author filters
        if query.authors:
            author_terms = [f"{author}[auth]" for author in query.authors]
            terms.append(f"({' OR '.join(author_terms)})")

        # Add journal filters
        if query.journals:
            journal_terms = [f'"{journal}"[jour]' for journal in query.journals]
            terms.append(f"({' OR '.join(journal_terms)})")

        # Add paper type filters
        if query.paper_types:
            type_mapping = {
                PaperType.REVIEW: "Review[pt]",
                PaperType.ARTICLE: "Journal Article[pt]",
            }
            type_terms = []
            for ptype in query.paper_types:
                if ptype in type_mapping:
                    type_terms.append(type_mapping[ptype])
            if type_terms:
                terms.append(f"({' OR '.join(type_terms)})")

        return " AND ".join(terms)

    def _search_ids(self, search_term: str, max_results: int) -> List[str]:
        """Search for PubMed IDs"""
        self.rate_limiter.wait_if_needed("pubmed")

        params = {
            "db": "pubmed",
            "term": search_term,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}esearch.fcgi",
                params=params,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []

    def _fetch_details(self, ids: List[str]) -> List[Paper]:
        """Fetch full details for PubMed IDs"""
        if not ids:
            return []

        papers = []
        batch_size = 100

        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            self.rate_limiter.wait_if_needed("pubmed")

            params = {
                "db": "pubmed",
                "id": ",".join(batch_ids),
                "retmode": "xml",
            }

            try:
                response = requests.get(
                    f"{self.BASE_URL}efetch.fcgi",
                    params=params,
                    timeout=Config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                batch_papers = self._parse_xml(response.text)
                papers.extend(batch_papers)
            except Exception as e:
                print(f"PubMed fetch error: {e}")
                continue

        return papers

    def _parse_xml(self, xml_text: str) -> List[Paper]:
        """Parse PubMed XML response"""
        papers = []

        try:
            root = ET.fromstring(xml_text)
            for article in root.findall(".//PubmedArticle"):
                paper = self._parse_article(article)
                if paper:
                    papers.append(paper)
        except Exception as e:
            print(f"XML parse error: {e}")

        return papers

    def _parse_article(self, article: ET.Element) -> Optional[Paper]:
        """Parse single PubMed article"""
        try:
            medline = article.find(".//MedlineCitation")
            if medline is None:
                return None

            # Extract title
            title_elem = medline.find(".//ArticleTitle")
            if title_elem is None or not title_elem.text:
                return None
            title = self._clean_text(title_elem.text)

            # Extract authors
            authors = []
            for author_elem in medline.findall(".//Author"):
                author = self._parse_author(author_elem)
                if author:
                    authors.append(author)

            # Extract year
            year = None
            pub_date = medline.find(".//PubDate")
            if pub_date is not None:
                year_elem = pub_date.find("Year")
                if year_elem is not None and year_elem.text:
                    try:
                        year = int(year_elem.text)
                    except ValueError:
                        pass

            # Extract journal
            journal = None
            journal_elem = medline.find(".//Journal/Title")
            if journal_elem is not None:
                journal = self._clean_text(journal_elem.text)

            # Extract abstract
            abstract = None
            abstract_texts = []
            for abstract_elem in medline.findall(".//Abstract/AbstractText"):
                if abstract_elem.text:
                    label = abstract_elem.get("Label")
                    if label:
                        abstract_texts.append(f"{label}: {abstract_elem.text}")
                    else:
                        abstract_texts.append(abstract_elem.text)
            if abstract_texts:
                abstract = self._clean_text(" ".join(abstract_texts))

            # Extract PMID
            pmid = None
            pmid_elem = medline.find(".//PMID")
            if pmid_elem is not None and pmid_elem.text:
                pmid = pmid_elem.text

            # Extract DOI and PMC ID
            doi = None
            pmcid = None
            for article_id in article.findall(".//ArticleId"):
                id_type = article_id.get("IdType")
                if id_type == "doi" and article_id.text:
                    doi = article_id.text
                elif id_type == "pmc" and article_id.text:
                    pmcid = article_id.text

            # Extract keywords
            keywords = []
            for keyword_elem in medline.findall(".//Keyword"):
                if keyword_elem.text:
                    keywords.append(self._clean_text(keyword_elem.text))

            # Extract volume, issue, pages
            volume = None
            issue = None
            pages = None
            article_elem = medline.find(".//Article")
            if article_elem is not None:
                volume_elem = article_elem.find(".//Volume")
                if volume_elem is not None:
                    volume = volume_elem.text
                issue_elem = article_elem.find(".//Issue")
                if issue_elem is not None:
                    issue = issue_elem.text
                pagination = article_elem.find(".//Pagination/MedlinePgn")
                if pagination is not None:
                    pages = pagination.text

            # Determine paper type
            paper_type = PaperType.UNKNOWN
            for pub_type in medline.findall(".//PublicationType"):
                if pub_type.text:
                    if "Review" in pub_type.text:
                        paper_type = PaperType.REVIEW
                        break
                    elif "Journal Article" in pub_type.text:
                        paper_type = PaperType.ARTICLE

            # Build URLs
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None
            pdf_url = None
            if pmcid:
                pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"

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
                pmid=pmid,
                pmcid=pmcid,
                keywords=keywords,
                paper_type=paper_type,
                url=url,
                pdf_url=pdf_url,
                sources=[self.source],
            )

        except Exception as e:
            print(f"Article parse error: {e}")
            return None

    def _parse_author(self, author_elem: ET.Element) -> Optional[Author]:
        """Parse author information"""
        last_name = author_elem.find("LastName")
        fore_name = author_elem.find("ForeName")

        if last_name is None or not last_name.text:
            return None

        name_parts = []
        if fore_name is not None and fore_name.text:
            name_parts.append(fore_name.text)
        name_parts.append(last_name.text)

        full_name = " ".join(name_parts)

        # Get affiliation
        affiliation = None
        affiliation_elem = author_elem.find(".//Affiliation")
        if affiliation_elem is not None and affiliation_elem.text:
            affiliation = self._clean_text(affiliation_elem.text)

        return Author(
            name=full_name,
            first_name=fore_name.text if fore_name is not None else None,
            last_name=last_name.text,
            affiliation=affiliation
        )