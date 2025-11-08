"""SQLAlchemy database models"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# Association tables
paper_authors = Table(
    'paper_authors',
    Base.metadata,
    Column('paper_id', Integer, ForeignKey('papers.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id'), primary_key=True),
    Column('author_order', Integer, default=0)
)

collection_papers = Table(
    'collection_papers',
    Base.metadata,
    Column('collection_id', Integer, ForeignKey('collections.id'), primary_key=True),
    Column('paper_id', Integer, ForeignKey('papers.id'), primary_key=True),
    Column('added_at', DateTime, default=datetime.utcnow)
)

paper_tags = Table(
    'paper_tags',
    Base.metadata,
    Column('paper_id', Integer, ForeignKey('papers.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Paper(Base):
    """Paper model"""
    __tablename__ = 'papers'

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identifiers
    title: Mapped[str] = mapped_column(Text, nullable=False)
    doi: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    pmid: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    pmcid: Mapped[Optional[str]] = mapped_column(String(50))
    arxiv_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)

    # Content
    abstract: Mapped[Optional[str]] = mapped_column(Text)
    keywords: Mapped[Optional[str]] = mapped_column(Text)  # JSON string

    # Publication info
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    journal: Mapped[Optional[str]] = mapped_column(String(500))
    volume: Mapped[Optional[str]] = mapped_column(String(50))
    issue: Mapped[Optional[str]] = mapped_column(String(50))
    pages: Mapped[Optional[str]] = mapped_column(String(50))

    # Metrics
    citations: Mapped[int] = mapped_column(Integer, default=0)
    altmetric_score: Mapped[Optional[float]] = mapped_column()
    relevance_score: Mapped[Optional[float]] = mapped_column()

    # URLs
    url: Mapped[Optional[str]] = mapped_column(Text)
    pdf_url: Mapped[Optional[str]] = mapped_column(Text)

    # Local storage
    local_pdf_path: Mapped[Optional[str]] = mapped_column(Text)

    # Metadata
    paper_type: Mapped[Optional[str]] = mapped_column(String(50))
    sources: Mapped[Optional[str]] = mapped_column(Text)  # JSON string

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    authors: Mapped[List["Author"]] = relationship(
        secondary=paper_authors,
        back_populates="papers"
    )
    collections: Mapped[List["Collection"]] = relationship(
        secondary=collection_papers,
        back_populates="papers"
    )
    tags: Mapped[List["Tag"]] = relationship(
        secondary=paper_tags,
        back_populates="papers"
    )
    notes: Mapped[List["Note"]] = relationship(back_populates="paper", cascade="all, delete-orphan")
    pdf_content: Mapped[Optional["PDFContent"]] = relationship(back_populates="paper", uselist=False)


class Author(Base):
    """Author model"""
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    affiliation: Mapped[Optional[str]] = mapped_column(Text)
    orcid: Mapped[Optional[str]] = mapped_column(String(50), unique=True)

    # Relationships
    papers: Mapped[List["Paper"]] = relationship(
        secondary=paper_authors,
        back_populates="authors"
    )


class PDFContent(Base):
    """PDF full-text content"""
    __tablename__ = 'pdf_content'

    paper_id: Mapped[int] = mapped_column(ForeignKey('papers.id'), primary_key=True)
    full_text: Mapped[str] = mapped_column(Text)
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    extracted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    paper: Mapped["Paper"] = relationship(back_populates="pdf_content")


class Collection(Base):
    """Collection/folder for organizing papers"""
    __tablename__ = 'collections'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    papers: Mapped[List["Paper"]] = relationship(
        secondary=collection_papers,
        back_populates="collections"
    )


class SearchHistory(Base):
    """Search history"""
    __tablename__ = 'search_history'

    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    filters: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    searched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class Tag(Base):
    """Tags for papers"""
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Relationships
    papers: Mapped[List["Paper"]] = relationship(
        secondary=paper_tags,
        back_populates="tags"
    )


class Note(Base):
    """Notes on papers"""
    __tablename__ = 'notes'

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey('papers.id'))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    paper: Mapped["Paper"] = relationship(back_populates="notes")