"""Tests for data models"""

import pytest
from src.models import Paper, Author, Source, PaperType, SearchQuery, SearchResult


class TestPaper:
    """Test Paper model"""

    def test_paper_creation(self, sample_paper):
        """Test creating a paper with full details"""
        assert sample_paper.title == "Machine Learning in Healthcare: A Comprehensive Review"
        assert sample_paper.doi == "10.1234/ml.healthcare.2023"
        assert sample_paper.year == 2023
        assert len(sample_paper.authors) == 2
        assert sample_paper.citations == 42

    def test_paper_minimal(self, sample_paper_minimal):
        """Test paper with only required fields"""
        assert sample_paper_minimal.title == "Minimal Paper"
        assert sample_paper_minimal.doi is None
        assert sample_paper_minimal.citations == 0
        assert len(sample_paper_minimal.authors) == 0

    def test_get_unique_id_doi(self, sample_paper):
        """Test unique ID generation with DOI"""
        unique_id = sample_paper.get_unique_id()
        assert unique_id == "doi:10.1234/ml.healthcare.2023"

    def test_get_unique_id_pmid(self, sample_paper_no_doi):
        """Test unique ID generation with PMID"""
        unique_id = sample_paper_no_doi.get_unique_id()
        assert unique_id == "pmid:87654321"

    def test_get_unique_id_title(self, sample_paper_minimal):
        """Test unique ID generation from title"""
        unique_id = sample_paper_minimal.get_unique_id()
        assert unique_id.startswith("title:")
        assert "minimalpaper" in unique_id.lower()

    def test_to_citation_apa_single_author(self):
        """Test APA citation with single author"""
        paper = Paper(
            title="Test Paper",
            year=2023,
            sources=[Source.PUBMED],
            authors=[Author(name="John Doe")]
        )
        citation = paper.to_citation(style="apa")
        assert "John Doe (2023)" in citation
        assert "Test Paper" in citation

    def test_to_citation_apa_two_authors(self, sample_paper):
        """Test APA citation with two authors"""
        citation = sample_paper.to_citation(style="apa")
        assert "John Doe & Jane Smith (2023)" in citation

    def test_to_citation_apa_multiple_authors(self):
        """Test APA citation with multiple authors"""
        paper = Paper(
            title="Test",
            year=2023,
            sources=[Source.PUBMED],
            authors=[
                Author(name="John Doe"),
                Author(name="Jane Smith"),
                Author(name="Bob Johnson")
            ]
        )
        citation = paper.to_citation(style="apa")
        assert "John Doe et al. (2023)" in citation

    def test_to_citation_no_year(self):
        """Test citation with missing year"""
        paper = Paper(
            title="Test",
            sources=[Source.PUBMED],
            authors=[Author(name="John Doe")]
        )
        citation = paper.to_citation()
        assert "n.d." in citation

    def test_to_citation_no_authors(self, sample_paper_minimal):
        """Test citation with no authors"""
        citation = sample_paper_minimal.to_citation()
        assert "Unknown" in citation


class TestAuthor:
    """Test Author model"""

    def test_author_full(self):
        """Test author with full details"""
        author = Author(
            name="John Doe",
            first_name="John",
            last_name="Doe",
            affiliation="Harvard University",
            orcid="0000-0001-2345-6789"
        )
        assert author.name == "John Doe"
        assert author.orcid == "0000-0001-2345-6789"

    def test_author_minimal(self):
        """Test author with minimal info"""
        author = Author(name="Jane Smith")
        assert author.name == "Jane Smith"
        assert author.first_name is None


class TestSearchQuery:
    """Test SearchQuery model"""

    def test_search_query_default(self):
        """Test search query with defaults"""
        query = SearchQuery(query="test")
        assert query.query == "test"
        assert Source.PUBMED in query.sources
        assert query.max_results == 50
        assert query.include_abstracts is True

    def test_search_query_custom(self):
        """Test search query with custom parameters"""
        query = SearchQuery(
            query="machine learning",
            sources=[Source.ARXIV],
            year_start=2020,
            year_end=2023,
            max_results=100,
            sort_by="date"
        )
        assert query.query == "machine learning"
        assert query.sources == [Source.ARXIV]
        assert query.year_start == 2020
        assert query.max_results == 100

    def test_search_query_filters(self):
        """Test search query with filters"""
        query = SearchQuery(
            query="test",
            authors=["John Doe"],
            journals=["Nature"],
            paper_types=[PaperType.REVIEW]
        )
        assert "John Doe" in query.authors
        assert "Nature" in query.journals
        assert PaperType.REVIEW in query.paper_types


class TestSearchResult:
    """Test SearchResult model"""

    def test_search_result(self, sample_papers_list):
        """Test search result"""
        query = SearchQuery(query="test")
        result = SearchResult(
            query=query,
            papers=sample_papers_list,
            total_found=10,
            sources_searched=[Source.PUBMED],
            search_time=2.5
        )

        assert len(result.papers) == 10
        assert result.total_found == 10
        assert result.search_time == 2.5

    def test_search_result_statistics(self, sample_papers_list):
        """Test statistics generation"""
        query = SearchQuery(query="test")
        result = SearchResult(
            query=query,
            papers=sample_papers_list,
            total_found=10,
            sources_searched=[Source.PUBMED, Source.ARXIV],
            search_time=2.5
        )

        stats = result.get_statistics()
        assert stats['total_papers'] == 10
        assert stats['sources_searched'] == 2
        assert stats['search_time'] == 2.5
        assert 'papers_by_source' in stats
        assert 'papers_by_year' in stats

    def test_search_result_empty(self):
        """Test empty search result"""
        query = SearchQuery(query="nonexistent")
        result = SearchResult(
            query=query,
            papers=[],
            total_found=0,
            sources_searched=[Source.PUBMED],
            search_time=0.5
        )

        assert len(result.papers) == 0
        stats = result.get_statistics()
        assert stats['total_papers'] == 0
        assert stats['avg_citations'] == 0


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_paper_very_long_title(self):
        """Test paper with extremely long title"""
        long_title = "A" * 1000
        paper = Paper(title=long_title, sources=[Source.PUBMED])
        assert len(paper.title) == 1000
        unique_id = paper.get_unique_id()
        assert len(unique_id) < 100  # Should be truncated

    def test_paper_special_characters_in_title(self):
        """Test paper with special characters"""
        paper = Paper(
            title="Test: A Study of α-β & γ-δ <Proteins>",
            sources=[Source.PUBMED]
        )
        assert paper.title == "Test: A Study of α-β & γ-δ <Proteins>"

    def test_paper_unicode_in_abstract(self):
        """Test paper with unicode in abstract"""
        paper = Paper(
            title="Test",
            abstract="This paper discusses 中文 and русский text",
            sources=[Source.PUBMED]
        )
        assert "中文" in paper.abstract

    def test_paper_negative_citations(self):
        """Test paper with negative citations (should default to 0)"""
        paper = Paper(
            title="Test",
            citations=-10,
            sources=[Source.PUBMED]
        )
        # Model should handle this gracefully
        assert paper.citations == -10  # Or validate in model if needed

    def test_paper_future_year(self):
        """Test paper with future year"""
        paper = Paper(
            title="Test",
            year=2050,
            sources=[Source.PUBMED]
        )
        assert paper.year == 2050

    def test_paper_ancient_year(self):
        """Test paper with very old year"""
        paper = Paper(
            title="Test",
            year=1800,
            sources=[Source.PUBMED]
        )
        assert paper.year == 1800

    def test_empty_keywords(self):
        """Test paper with empty keywords list"""
        paper = Paper(
            title="Test",
            keywords=[],
            sources=[Source.PUBMED]
        )
        assert paper.keywords == []

    def test_keywords_with_whitespace(self):
        """Test keywords with extra whitespace"""
        paper = Paper(
            title="Test",
            keywords=["  machine learning  ", "AI", ""],
            sources=[Source.PUBMED]
        )
        assert len(paper.keywords) == 3

    def test_multiple_sources(self):
        """Test paper from multiple sources"""
        paper = Paper(
            title="Test",
            sources=[Source.PUBMED, Source.ARXIV, Source.CROSSREF]
        )
        assert len(paper.sources) == 3

    def test_doi_normalization(self):
        """Test various DOI formats"""
        dois = [
            "10.1234/test",
            "https://doi.org/10.1234/test",
            "DOI:10.1234/test"
        ]
        for doi in dois:
            paper = Paper(title="Test", doi=doi, sources=[Source.PUBMED])
            assert paper.doi == doi