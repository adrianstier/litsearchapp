"""Pytest configuration and fixtures"""

import pytest
import tempfile
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.database.models import Base
from src.models import Paper, Author, Source, PaperType


@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory for tests"""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def sample_paper():
    """Sample paper for testing"""
    return Paper(
        title="Machine Learning in Healthcare: A Comprehensive Review",
        doi="10.1234/ml.healthcare.2023",
        pmid="12345678",
        abstract="This paper reviews machine learning applications in healthcare...",
        year=2023,
        journal="Journal of Medical AI",
        volume="10",
        issue="2",
        pages="123-145",
        citations=42,
        paper_type=PaperType.REVIEW,
        authors=[
            Author(name="John Doe", first_name="John", last_name="Doe"),
            Author(name="Jane Smith", first_name="Jane", last_name="Smith")
        ],
        sources=[Source.PUBMED],
        keywords=["machine learning", "healthcare", "AI"],
        url="https://example.com/paper",
        pdf_url="https://example.com/paper.pdf"
    )


@pytest.fixture
def sample_paper_minimal():
    """Minimal paper with only required fields"""
    return Paper(
        title="Minimal Paper",
        sources=[Source.ARXIV]
    )


@pytest.fixture
def sample_paper_no_doi():
    """Paper without DOI"""
    return Paper(
        title="Paper Without DOI",
        pmid="87654321",
        abstract="A paper without DOI...",
        year=2024,
        sources=[Source.PUBMED]
    )


@pytest.fixture
def sample_papers_list():
    """List of sample papers for bulk testing"""
    papers = []
    for i in range(10):
        papers.append(Paper(
            title=f"Test Paper {i}",
            doi=f"10.1234/test.{i}" if i % 2 == 0 else None,
            pmid=f"1234567{i}" if i % 3 == 0 else None,
            year=2020 + i % 5,
            citations=i * 10,
            sources=[Source.PUBMED if i % 2 == 0 else Source.ARXIV],
            authors=[
                Author(name=f"Author {i}", last_name=f"Author{i}")
            ]
        ))
    return papers


@pytest.fixture
def sample_duplicate_papers():
    """Papers with same DOI for deduplication testing"""
    paper1 = Paper(
        title="Original Paper",
        doi="10.1234/duplicate",
        abstract="Original abstract",
        year=2023,
        sources=[Source.PUBMED]
    )

    paper2 = Paper(
        title="Duplicate Paper",  # Different title
        doi="10.1234/duplicate",  # Same DOI
        abstract="Different abstract but more detailed",
        year=2023,
        citations=100,  # More citations
        sources=[Source.CROSSREF]  # Different source
    )

    return [paper1, paper2]


@pytest.fixture
def sample_pdf_path(temp_dir):
    """Create a fake PDF file for testing"""
    pdf_path = temp_dir / "test.pdf"
    # Write PDF magic number
    pdf_path.write_bytes(b'%PDF-1.4\n%EOF\n')
    return pdf_path


@pytest.fixture
def sample_cookies_file(temp_dir):
    """Create a sample Netscape cookies file"""
    cookies_path = temp_dir / "cookies.txt"
    cookies_content = """# Netscape HTTP Cookie File
.library.ucsb.edu\tTRUE\t/\tTRUE\t0\tezproxy\tvalue123
.library.ucsb.edu\tTRUE\t/\tFALSE\t0\tsession\tabc456
"""
    cookies_path.write_text(cookies_content)
    return cookies_path