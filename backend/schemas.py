"""Pydantic schemas for API requests and responses"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# =============================================================================
# AUTHOR SCHEMAS
# =============================================================================

class AuthorBase(BaseModel):
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    affiliation: Optional[str] = None
    orcid: Optional[str] = None


class Author(AuthorBase):
    id: int

    class Config:
        from_attributes = True


# =============================================================================
# PAPER SCHEMAS
# =============================================================================

class PaperBase(BaseModel):
    title: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    arxiv_id: Optional[str] = None
    abstract: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    citations: int = 0
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    paper_type: Optional[str] = None


class Paper(PaperBase):
    id: int
    authors: List[Author] = []
    keywords: List[str] = []
    sources: List[str] = []
    local_pdf_path: Optional[str] = None
    relevance_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    has_pdf: bool = False
    has_text: bool = False

    class Config:
        from_attributes = True


class PaperDetail(Paper):
    """Extended paper with relationships"""
    collections: List["Collection"] = []
    tags: List["Tag"] = []
    notes: List["Note"] = []


class PaperListResponse(BaseModel):
    papers: List[Paper]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# SEARCH SCHEMAS
# =============================================================================

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    sources: List[str] = ["pubmed", "arxiv", "crossref"]
    max_results: int = Field(50, ge=1, le=200)
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    paper_types: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    journals: Optional[List[str]] = None


class SearchResultResponse(BaseModel):
    papers: List[Paper]
    total_found: int
    search_time: float
    sources_searched: List[str]
    statistics: Dict[str, Any]


class SearchHistoryItem(BaseModel):
    id: int
    query: str
    sources: Optional[str] = None
    results_count: int
    searched_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# COLLECTION SCHEMAS
# =============================================================================

class CollectionBase(BaseModel):
    name: str
    description: Optional[str] = None


class CollectionCreate(CollectionBase):
    pass


class Collection(CollectionBase):
    id: int
    created_at: datetime
    paper_count: int = 0

    class Config:
        from_attributes = True


# =============================================================================
# TAG SCHEMAS
# =============================================================================

class TagBase(BaseModel):
    name: str


class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True


# =============================================================================
# NOTE SCHEMAS
# =============================================================================

class NoteBase(BaseModel):
    content: str


class NoteCreate(NoteBase):
    paper_id: int


class Note(NoteBase):
    id: int
    paper_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# VISUALIZATION SCHEMAS
# =============================================================================

class TimelineDataPoint(BaseModel):
    year: int
    count: int
    papers: List[int]  # Paper IDs


class TimelineResponse(BaseModel):
    data: List[TimelineDataPoint]
    year_range: tuple[int, int]


class NetworkNode(BaseModel):
    id: str
    label: str
    size: int
    group: str


class NetworkLink(BaseModel):
    source: str
    target: str
    weight: float


class NetworkResponse(BaseModel):
    nodes: List[NetworkNode]
    links: List[NetworkLink]


class TopicCluster(BaseModel):
    cluster_id: int
    label: str
    papers: List[int]
    size: int
    keywords: List[str]


class TopicResponse(BaseModel):
    clusters: List[TopicCluster]


# =============================================================================
# DOWNLOAD SCHEMAS
# =============================================================================

class DownloadResponse(BaseModel):
    success: bool
    path: Optional[str] = None
    error: Optional[str] = None


class BatchDownloadRequest(BaseModel):
    paper_ids: List[int]


class BatchDownloadResponse(BaseModel):
    successful: int
    failed: int
    total: int


# =============================================================================
# AUTH SCHEMAS
# =============================================================================

class AuthStatus(BaseModel):
    authenticated: bool
    session_file_exists: bool
    cookies_count: int
    config_dir: str
    message: str


# =============================================================================
# STATS SCHEMAS
# =============================================================================

class StatsResponse(BaseModel):
    total_papers: int
    total_pdfs: int
    total_collections: int
    total_searches: int
    pdf_percentage: float


# =============================================================================
# PDF SCHEMAS
# =============================================================================

class PDFTextExtractResponse(BaseModel):
    message: str
    page_count: int
    text_length: int


class FullTextSearchResult(BaseModel):
    results: List[Paper]
    query: str
    count: int