"""Paper service for database operations"""

import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.database import models as db_models
from src.models import Paper as PaperModel, Author as AuthorModel
from backend import schemas


def save_paper(db: Session, paper: PaperModel) -> db_models.Paper:
    """
    Save paper to database

    Args:
        db: Database session
        paper: Paper model from search

    Returns:
        Database paper model
    """
    try:
        # Check if paper already exists
        existing = None
        if paper.doi:
            existing = db.query(db_models.Paper).filter(db_models.Paper.doi == paper.doi).first()
        if not existing and paper.pmid:
            existing = db.query(db_models.Paper).filter(db_models.Paper.pmid == paper.pmid).first()
        if not existing and paper.arxiv_id:
            existing = db.query(db_models.Paper).filter(db_models.Paper.arxiv_id == paper.arxiv_id).first()

        if existing:
            # Update existing paper
            update_paper(db, existing, paper)
            return existing

        # Create new paper
        db_paper = db_models.Paper(
            title=paper.title,
            doi=paper.doi,
            pmid=paper.pmid,
            pmcid=paper.pmcid,
            arxiv_id=paper.arxiv_id,
            abstract=paper.abstract,
            keywords=json.dumps(paper.keywords),
            year=paper.year,
            journal=paper.journal,
            volume=paper.volume,
            issue=paper.issue,
            pages=paper.pages,
            citations=paper.citations,
            altmetric_score=paper.altmetric_score,
            relevance_score=paper.relevance_score,
            url=str(paper.url) if paper.url else None,
            pdf_url=str(paper.pdf_url) if paper.pdf_url else None,
            local_pdf_path=paper.local_pdf_path,
            paper_type=paper.paper_type.value if paper.paper_type else None,
            sources=json.dumps([s.value for s in paper.sources])
        )

        # Add authors (avoid duplicates by checking IDs)
        existing_author_ids = set()
        for author in paper.authors:
            db_author = get_or_create_author(db, author)
            if db_author.id not in existing_author_ids:
                db_paper.authors.append(db_author)
                existing_author_ids.add(db_author.id)

        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)

        return db_paper

    except Exception as e:
        db.rollback()
        print(f"Error saving paper '{paper.title[:50]}...': {e}")
        raise


def update_paper(db: Session, db_paper: db_models.Paper, paper: PaperModel):
    """Update existing paper with new data"""
    # Update fields that might have changed
    if paper.abstract and not db_paper.abstract:
        db_paper.abstract = paper.abstract

    if paper.citations > db_paper.citations:
        db_paper.citations = paper.citations

    if paper.pdf_url and not db_paper.pdf_url:
        db_paper.pdf_url = str(paper.pdf_url)

    if paper.local_pdf_path:
        db_paper.local_pdf_path = paper.local_pdf_path

    # Merge sources
    existing_sources = set(json.loads(db_paper.sources or "[]"))
    new_sources = set([s.value for s in paper.sources])
    db_paper.sources = json.dumps(list(existing_sources | new_sources))

    db.commit()


def get_or_create_author(db: Session, author: AuthorModel) -> db_models.Author:
    """Get existing author or create new one"""
    # Try to find by ORCID first
    if author.orcid:
        db_author = db.query(db_models.Author).filter(db_models.Author.orcid == author.orcid).first()
        if db_author:
            return db_author

    # Try to find by name
    db_author = db.query(db_models.Author).filter(db_models.Author.name == author.name).first()
    if db_author:
        return db_author

    # Create new author
    db_author = db_models.Author(
        name=author.name,
        first_name=author.first_name,
        last_name=author.last_name,
        affiliation=author.affiliation,
        orcid=author.orcid
    )
    db.add(db_author)
    db.commit()
    db.refresh(db_author)

    return db_author


def paper_to_schema(db_paper: db_models.Paper) -> schemas.Paper:
    """Convert database paper to schema"""
    return schemas.Paper(
        id=db_paper.id,
        title=db_paper.title,
        doi=db_paper.doi,
        pmid=db_paper.pmid,
        pmcid=db_paper.pmcid,
        arxiv_id=db_paper.arxiv_id,
        abstract=db_paper.abstract,
        year=db_paper.year,
        journal=db_paper.journal,
        volume=db_paper.volume,
        issue=db_paper.issue,
        pages=db_paper.pages,
        citations=db_paper.citations,
        url=db_paper.url,
        pdf_url=db_paper.pdf_url,
        paper_type=db_paper.paper_type,
        authors=[schemas.Author(
            id=a.id,
            name=a.name,
            first_name=a.first_name,
            last_name=a.last_name,
            affiliation=a.affiliation,
            orcid=a.orcid
        ) for a in db_paper.authors],
        keywords=json.loads(db_paper.keywords or "[]"),
        sources=json.loads(db_paper.sources or "[]"),
        local_pdf_path=db_paper.local_pdf_path,
        relevance_score=db_paper.relevance_score,
        created_at=db_paper.created_at,
        updated_at=db_paper.updated_at,
        has_pdf=bool(db_paper.local_pdf_path),
        has_text=bool(db_paper.pdf_content)
    )


def db_to_paper_model(db_paper: db_models.Paper) -> PaperModel:
    """Convert database paper to Paper model for downloading"""
    from src.models import Author as AuthorModel, Source, PaperType

    return PaperModel(
        title=db_paper.title,
        doi=db_paper.doi,
        pmid=db_paper.pmid,
        pmcid=db_paper.pmcid,
        arxiv_id=db_paper.arxiv_id,
        abstract=db_paper.abstract,
        year=db_paper.year,
        journal=db_paper.journal,
        volume=db_paper.volume,
        issue=db_paper.issue,
        pages=db_paper.pages,
        citations=db_paper.citations,
        url=db_paper.url,
        pdf_url=db_paper.pdf_url,
        local_pdf_path=db_paper.local_pdf_path,
        paper_type=PaperType(db_paper.paper_type) if db_paper.paper_type else PaperType.UNKNOWN,
        sources=[Source(s) for s in json.loads(db_paper.sources or "[]")],
        authors=[AuthorModel(
            name=a.name,
            first_name=a.first_name,
            last_name=a.last_name,
            affiliation=a.affiliation,
            orcid=a.orcid
        ) for a in db_paper.authors],
        keywords=json.loads(db_paper.keywords or "[]")
    )


def full_text_search(db: Session, query: str, limit: int = 50) -> List[db_models.Paper]:
    """
    Full-text search across papers

    Args:
        db: Database session
        query: Search query
        limit: Maximum results

    Returns:
        List of matching papers
    """
    # Simple search for now - can be enhanced with FTS5
    search_term = f"%{query}%"

    results = db.query(db_models.Paper).filter(
        or_(
            db_models.Paper.title.ilike(search_term),
            db_models.Paper.abstract.ilike(search_term),
            db_models.Paper.keywords.ilike(search_term)
        )
    ).limit(limit).all()

    # Also search PDF content if available
    pdf_results = db.query(db_models.Paper).join(
        db_models.PDFContent
    ).filter(
        db_models.PDFContent.full_text.ilike(search_term)
    ).limit(limit).all()

    # Combine and deduplicate
    seen_ids = set()
    combined = []
    for paper in results + pdf_results:
        if paper.id not in seen_ids:
            combined.append(paper)
            seen_ids.add(paper.id)

    return combined[:limit]