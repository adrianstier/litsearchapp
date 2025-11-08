"""Data models for literature search"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class Source(str, Enum):
    """Available search sources"""
    PUBMED = "pubmed"
    ARXIV = "arxiv"
    CROSSREF = "crossref"
    GOOGLE_SCHOLAR = "scholar"
    WEB_OF_SCIENCE = "wos"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    PMC = "pmc"


class PaperType(str, Enum):
    """Types of academic papers"""
    ARTICLE = "article"
    REVIEW = "review"
    PREPRINT = "preprint"
    CONFERENCE = "conference"
    BOOK_CHAPTER = "book_chapter"
    THESIS = "thesis"
    UNKNOWN = "unknown"


class Author(BaseModel):
    """Author information"""
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    affiliation: Optional[str] = None
    orcid: Optional[str] = None


class Paper(BaseModel):
    """Academic paper model"""
    # Identifiers
    title: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    arxiv_id: Optional[str] = None

    # Authors and publication
    authors: List[Author] = []
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None

    # Content
    abstract: Optional[str] = None
    keywords: List[str] = []

    # Metrics
    citations: int = 0
    altmetric_score: Optional[float] = None
    relevance_score: Optional[float] = None

    # URLs
    url: Optional[HttpUrl] = None
    pdf_url: Optional[HttpUrl] = None

    # Metadata
    paper_type: PaperType = PaperType.UNKNOWN
    sources: List[Source] = []
    retrieved_at: datetime = Field(default_factory=datetime.now)

    # Local storage
    local_pdf_path: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: str
        }

    def get_unique_id(self) -> str:
        """Get a unique identifier for the paper"""
        if self.doi:
            return f"doi:{self.doi}"
        elif self.pmid:
            return f"pmid:{self.pmid}"
        elif self.arxiv_id:
            return f"arxiv:{self.arxiv_id}"
        else:
            # Generate ID from title and year
            title_slug = "".join(c for c in self.title[:50] if c.isalnum()).lower()
            return f"title:{title_slug}_{self.year or 'unknown'}"

    def to_citation(self, style: str = "apa") -> str:
        """Generate a citation string"""
        if not self.authors:
            author_str = "Unknown"
        elif len(self.authors) == 1:
            author_str = self.authors[0].name
        elif len(self.authors) == 2:
            author_str = f"{self.authors[0].name} & {self.authors[1].name}"
        else:
            author_str = f"{self.authors[0].name} et al."

        year_str = str(self.year) if self.year else "n.d."

        if style == "apa":
            citation = f"{author_str} ({year_str}). {self.title}."
            if self.journal:
                citation += f" {self.journal}"
                if self.volume:
                    citation += f", {self.volume}"
                    if self.issue:
                        citation += f"({self.issue})"
                if self.pages:
                    citation += f", {self.pages}"
            citation += "."
            if self.doi:
                citation += f" https://doi.org/{self.doi}"
        else:
            # Default simple format
            citation = f"{author_str} ({year_str}). {self.title}"

        return citation


class SearchQuery(BaseModel):
    """Search query parameters"""
    query: str
    sources: List[Source] = [Source.PUBMED, Source.ARXIV, Source.CROSSREF]
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    max_results: int = 50
    paper_types: Optional[List[PaperType]] = None
    authors: Optional[List[str]] = None
    journals: Optional[List[str]] = None
    sort_by: str = "relevance"  # relevance, date, citations
    include_abstracts: bool = True


class SearchResult(BaseModel):
    """Search result containing papers and metadata"""
    query: SearchQuery
    papers: List[Paper]
    total_found: int
    sources_searched: List[Source]
    search_time: float
    timestamp: datetime = Field(default_factory=datetime.now)
    errors: Dict[str, str] = {}

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the search results"""
        stats = {
            "total_papers": len(self.papers),
            "total_found": self.total_found,
            "sources_searched": len(self.sources_searched),
            "papers_by_source": {},
            "papers_by_year": {},
            "papers_by_type": {},
            "avg_citations": 0,
            "search_time": self.search_time
        }

        # Count papers by source
        for paper in self.papers:
            for source in paper.sources:
                stats["papers_by_source"][source.value] = stats["papers_by_source"].get(source.value, 0) + 1

        # Count papers by year
        for paper in self.papers:
            if paper.year:
                stats["papers_by_year"][paper.year] = stats["papers_by_year"].get(paper.year, 0) + 1

        # Count papers by type
        for paper in self.papers:
            stats["papers_by_type"][paper.paper_type.value] = stats["papers_by_type"].get(paper.paper_type.value, 0) + 1

        # Calculate average citations
        if self.papers:
            total_citations = sum(p.citations for p in self.papers)
            stats["avg_citations"] = total_citations / len(self.papers)

        return stats


class SynthesisRequest(BaseModel):
    """Request for paper synthesis"""
    papers: List[Paper]
    research_question: str
    focus_areas: Optional[List[str]] = None
    max_length: int = 2000
    include_gaps: bool = True
    include_future_directions: bool = True


class SynthesisResult(BaseModel):
    """Result of paper synthesis"""
    research_question: str
    num_papers: int
    synthesis: str
    key_findings: List[str]
    consensus_points: List[str]
    contradictions: List[str]
    research_gaps: List[str]
    future_directions: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)