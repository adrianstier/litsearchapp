"""Tests for database models and operations"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.database import models as db_models


class TestPaperModel:
    """Test Paper database model"""

    def test_create_paper(self, db_session):
        """Test creating a paper"""
        paper = db_models.Paper(
            title="Test Paper",
            doi="10.1234/test",
            abstract="Test abstract",
            year=2023,
            citations=10
        )
        db_session.add(paper)
        db_session.commit()

        assert paper.id is not None
        assert paper.title == "Test Paper"
        assert paper.doi == "10.1234/test"
        assert paper.created_at is not None

    def test_unique_doi_constraint(self, db_session):
        """Test DOI uniqueness constraint"""
        paper1 = db_models.Paper(
            title="Paper 1",
            doi="10.1234/same"
        )
        db_session.add(paper1)
        db_session.commit()

        paper2 = db_models.Paper(
            title="Paper 2",
            doi="10.1234/same"
        )
        db_session.add(paper2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_paper_author_relationship(self, db_session):
        """Test many-to-many relationship between papers and authors"""
        author1 = db_models.Author(name="John Doe", email="john@example.com")
        author2 = db_models.Author(name="Jane Smith")

        paper = db_models.Paper(title="Test Paper")
        paper.authors.extend([author1, author2])

        db_session.add(paper)
        db_session.commit()

        assert len(paper.authors) == 2
        assert paper.authors[0].name == "John Doe"
        assert len(author1.papers) == 1

    def test_paper_collection_relationship(self, db_session):
        """Test many-to-many relationship between papers and collections"""
        collection = db_models.Collection(name="My Collection")
        paper1 = db_models.Paper(title="Paper 1")
        paper2 = db_models.Paper(title="Paper 2")

        collection.papers.extend([paper1, paper2])

        db_session.add(collection)
        db_session.commit()

        assert len(collection.papers) == 2
        assert len(paper1.collections) == 1

    def test_paper_with_pdf_content(self, db_session):
        """Test one-to-one relationship with PDF content"""
        paper = db_models.Paper(title="Test Paper")
        pdf_content = db_models.PDFContent(
            paper=paper,
            extracted_text="Sample PDF text content",
            page_count=10
        )

        db_session.add(paper)
        db_session.commit()

        assert paper.pdf_content is not None
        assert paper.pdf_content.extracted_text == "Sample PDF text content"
        assert paper.pdf_content.page_count == 10

    def test_paper_with_tags(self, db_session):
        """Test many-to-many relationship with tags"""
        paper = db_models.Paper(title="Test Paper")
        tag1 = db_models.Tag(name="machine-learning")
        tag2 = db_models.Tag(name="healthcare")

        paper.tags.extend([tag1, tag2])

        db_session.add(paper)
        db_session.commit()

        assert len(paper.tags) == 2
        assert tag1.name in [t.name for t in paper.tags]

    def test_paper_with_notes(self, db_session):
        """Test one-to-many relationship with notes"""
        paper = db_models.Paper(title="Test Paper")
        note1 = db_models.Note(paper=paper, content="First note")
        note2 = db_models.Note(paper=paper, content="Second note")

        db_session.add(paper)
        db_session.commit()

        assert len(paper.notes) == 2
        assert paper.notes[0].content == "First note"

    def test_cascade_delete_pdf_content(self, db_session):
        """Test that PDF content is deleted when paper is deleted"""
        paper = db_models.Paper(title="Test Paper")
        pdf_content = db_models.PDFContent(paper=paper, extracted_text="Text")

        db_session.add(paper)
        db_session.commit()

        paper_id = paper.id
        db_session.delete(paper)
        db_session.commit()

        # PDF content should be deleted
        result = db_session.query(db_models.PDFContent).filter_by(paper_id=paper_id).first()
        assert result is None

    def test_null_optional_fields(self, db_session):
        """Test that optional fields can be null"""
        paper = db_models.Paper(title="Minimal Paper")
        db_session.add(paper)
        db_session.commit()

        assert paper.doi is None
        assert paper.pmid is None
        assert paper.arxiv_id is None
        assert paper.abstract is None
        assert paper.year is None


class TestAuthorModel:
    """Test Author database model"""

    def test_create_author(self, db_session):
        """Test creating an author"""
        author = db_models.Author(
            name="John Doe",
            email="john@example.com",
            affiliation="University"
        )
        db_session.add(author)
        db_session.commit()

        assert author.id is not None
        assert author.name == "John Doe"

    def test_author_deduplication_by_email(self, db_session):
        """Test finding authors by email"""
        author1 = db_models.Author(name="John Doe", email="john@example.com")
        db_session.add(author1)
        db_session.commit()

        # Try to find existing author
        existing = db_session.query(db_models.Author).filter_by(
            email="john@example.com"
        ).first()

        assert existing is not None
        assert existing.id == author1.id

    def test_author_multiple_papers(self, db_session):
        """Test author associated with multiple papers"""
        author = db_models.Author(name="Prolific Researcher")
        paper1 = db_models.Paper(title="Paper 1")
        paper2 = db_models.Paper(title="Paper 2")
        paper3 = db_models.Paper(title="Paper 3")

        author.papers.extend([paper1, paper2, paper3])

        db_session.add(author)
        db_session.commit()

        assert len(author.papers) == 3


class TestCollectionModel:
    """Test Collection database model"""

    def test_create_collection(self, db_session):
        """Test creating a collection"""
        collection = db_models.Collection(
            name="My Collection",
            description="A test collection"
        )
        db_session.add(collection)
        db_session.commit()

        assert collection.id is not None
        assert collection.name == "My Collection"

    def test_collection_paper_count(self, db_session):
        """Test adding multiple papers to collection"""
        collection = db_models.Collection(name="Test")
        papers = [db_models.Paper(title=f"Paper {i}") for i in range(5)]
        collection.papers.extend(papers)

        db_session.add(collection)
        db_session.commit()

        assert len(collection.papers) == 5

    def test_multiple_collections_per_paper(self, db_session):
        """Test paper can be in multiple collections"""
        paper = db_models.Paper(title="Popular Paper")
        col1 = db_models.Collection(name="Collection 1")
        col2 = db_models.Collection(name="Collection 2")

        col1.papers.append(paper)
        col2.papers.append(paper)

        db_session.add_all([col1, col2])
        db_session.commit()

        assert len(paper.collections) == 2


class TestSearchHistoryModel:
    """Test SearchHistory database model"""

    def test_create_search_history(self, db_session):
        """Test creating search history entry"""
        search = db_models.SearchHistory(
            query="machine learning",
            sources_json='["pubmed", "arxiv"]',
            result_count=25
        )
        db_session.add(search)
        db_session.commit()

        assert search.id is not None
        assert search.query == "machine learning"
        assert search.created_at is not None

    def test_search_history_ordering(self, db_session):
        """Test that searches are ordered by creation time"""
        search1 = db_models.SearchHistory(query="first", result_count=10)
        db_session.add(search1)
        db_session.commit()

        search2 = db_models.SearchHistory(query="second", result_count=20)
        db_session.add(search2)
        db_session.commit()

        results = db_session.query(db_models.SearchHistory).order_by(
            db_models.SearchHistory.created_at.desc()
        ).all()

        assert results[0].query == "second"
        assert results[1].query == "first"


class TestPDFContentModel:
    """Test PDFContent database model"""

    def test_create_pdf_content(self, db_session):
        """Test creating PDF content"""
        paper = db_models.Paper(title="Test Paper")
        pdf = db_models.PDFContent(
            paper=paper,
            extracted_text="Sample text",
            page_count=15
        )
        db_session.add(paper)
        db_session.commit()

        assert pdf.id is not None
        assert pdf.extracted_at is not None

    def test_pdf_content_large_text(self, db_session):
        """Test storing large PDF text"""
        paper = db_models.Paper(title="Long Paper")
        large_text = "Lorem ipsum " * 10000  # Large text
        pdf = db_models.PDFContent(paper=paper, extracted_text=large_text, page_count=100)

        db_session.add(paper)
        db_session.commit()

        assert len(pdf.extracted_text) > 100000


class TestTagModel:
    """Test Tag database model"""

    def test_create_tag(self, db_session):
        """Test creating a tag"""
        tag = db_models.Tag(name="machine-learning")
        db_session.add(tag)
        db_session.commit()

        assert tag.id is not None
        assert tag.name == "machine-learning"

    def test_unique_tag_name(self, db_session):
        """Test tag name uniqueness"""
        tag1 = db_models.Tag(name="ai")
        db_session.add(tag1)
        db_session.commit()

        tag2 = db_models.Tag(name="ai")
        db_session.add(tag2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_tag_case_sensitivity(self, db_session):
        """Test that tags are case-sensitive"""
        tag1 = db_models.Tag(name="AI")
        tag2 = db_models.Tag(name="ai")

        db_session.add(tag1)
        db_session.commit()

        db_session.add(tag2)
        # This should work - different case
        db_session.commit()

        assert tag1.id != tag2.id


class TestNoteModel:
    """Test Note database model"""

    def test_create_note(self, db_session):
        """Test creating a note"""
        paper = db_models.Paper(title="Test Paper")
        note = db_models.Note(
            paper=paper,
            content="This is a great paper!"
        )
        db_session.add(paper)
        db_session.commit()

        assert note.id is not None
        assert note.created_at is not None

    def test_note_updates(self, db_session):
        """Test updating note content"""
        paper = db_models.Paper(title="Test Paper")
        note = db_models.Note(paper=paper, content="Original content")

        db_session.add(paper)
        db_session.commit()

        original_created = note.created_at
        original_updated = note.updated_at

        # Update note
        note.content = "Updated content"
        db_session.commit()

        assert note.content == "Updated content"
        assert note.created_at == original_created
        # Note: updated_at might not change in SQLite without triggers


class TestEdgeCases:
    """Test edge cases in database operations"""

    def test_very_long_title(self, db_session):
        """Test paper with extremely long title"""
        long_title = "A" * 5000
        paper = db_models.Paper(title=long_title)
        db_session.add(paper)
        db_session.commit()

        assert len(paper.title) == 5000

    def test_special_characters_in_title(self, db_session):
        """Test special characters in title"""
        paper = db_models.Paper(title="Test: A Study of α, β, and γ-rays! (2023)")
        db_session.add(paper)
        db_session.commit()

        assert "α" in paper.title
        assert "!" in paper.title

    def test_unicode_in_database(self, db_session):
        """Test unicode characters in database"""
        paper = db_models.Paper(title="机器学习研究")
        author = db_models.Author(name="李明", affiliation="北京大学")
        paper.authors.append(author)

        db_session.add(paper)
        db_session.commit()

        assert paper.title == "机器学习研究"
        assert paper.authors[0].name == "李明"

    def test_empty_collections(self, db_session):
        """Test collection with no papers"""
        collection = db_models.Collection(name="Empty Collection")
        db_session.add(collection)
        db_session.commit()

        assert len(collection.papers) == 0

    def test_paper_with_many_authors(self, db_session):
        """Test paper with large number of authors"""
        paper = db_models.Paper(title="Large Collaboration")
        authors = [db_models.Author(name=f"Author {i}") for i in range(100)]
        paper.authors.extend(authors)

        db_session.add(paper)
        db_session.commit()

        assert len(paper.authors) == 100

    def test_query_nonexistent_paper(self, db_session):
        """Test querying for non-existent paper"""
        result = db_session.query(db_models.Paper).filter_by(doi="10.9999/nonexistent").first()
        assert result is None

    def test_negative_year(self, db_session):
        """Test paper with negative year (BC dates)"""
        paper = db_models.Paper(title="Ancient Philosophy", year=-350)
        db_session.add(paper)
        db_session.commit()

        assert paper.year == -350

    def test_zero_citations(self, db_session):
        """Test paper with zero citations"""
        paper = db_models.Paper(title="New Paper", citations=0)
        db_session.add(paper)
        db_session.commit()

        assert paper.citations == 0

    def test_bulk_insert_papers(self, db_session):
        """Test bulk inserting many papers"""
        papers = [
            db_models.Paper(title=f"Paper {i}", doi=f"10.{i}/test")
            for i in range(100)
        ]
        db_session.add_all(papers)
        db_session.commit()

        count = db_session.query(db_models.Paper).count()
        assert count == 100
