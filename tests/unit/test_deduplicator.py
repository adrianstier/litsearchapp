"""Tests for deduplication logic"""

import pytest
from src.search.deduplicator import Deduplicator
from src.models import Paper, Author, Source


class TestDeduplicator:
    """Test Deduplicator class"""

    @pytest.fixture
    def deduplicator(self):
        return Deduplicator()

    def test_deduplicate_empty_list(self, deduplicator):
        """Test deduplication with empty list"""
        result = deduplicator.deduplicate([])
        assert result == []

    def test_deduplicate_single_paper(self, deduplicator, sample_paper):
        """Test deduplication with single paper"""
        result = deduplicator.deduplicate([sample_paper])
        assert len(result) == 1
        assert result[0].title == sample_paper.title

    def test_deduplicate_by_doi(self, deduplicator, sample_duplicate_papers):
        """Test deduplication by DOI"""
        result = deduplicator.deduplicate(sample_duplicate_papers)
        assert len(result) == 1

        # Should merge metadata
        merged = result[0]
        assert merged.doi == "10.1234/duplicate"
        # Should have both sources
        assert len(merged.sources) == 2
        # Should take higher citation count
        assert merged.citations == 100

    def test_deduplicate_by_pmid(self, deduplicator):
        """Test deduplication by PMID"""
        paper1 = Paper(
            title="Paper 1",
            pmid="12345",
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="Paper 2",
            pmid="12345",
            sources=[Source.CROSSREF]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 1
        assert len(result[0].sources) == 2

    def test_deduplicate_by_arxiv_id(self, deduplicator):
        """Test deduplication by arXiv ID"""
        paper1 = Paper(
            title="Paper 1",
            arxiv_id="2301.12345",
            sources=[Source.ARXIV]
        )
        paper2 = Paper(
            title="Paper 2",
            arxiv_id="2301.12345",
            sources=[Source.CROSSREF]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 1

    def test_deduplicate_by_title_similarity(self, deduplicator):
        """Test deduplication by title similarity"""
        paper1 = Paper(
            title="Machine Learning in Healthcare Applications",
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="Machine Learning in Healthcare Applications",  # Identical
            sources=[Source.ARXIV]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 1

    def test_deduplicate_similar_titles(self, deduplicator):
        """Test deduplication with very similar titles"""
        paper1 = Paper(
            title="A Study of Machine Learning",
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="A Study of Machine Learning!",  # Minor difference
            sources=[Source.ARXIV]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        # Should deduplicate due to high similarity
        assert len(result) == 1

    def test_dont_deduplicate_different_titles(self, deduplicator):
        """Test that different papers aren't deduplicated"""
        paper1 = Paper(
            title="Machine Learning",
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="Deep Learning",
            sources=[Source.ARXIV]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 2

    def test_merge_abstracts(self, deduplicator):
        """Test merging abstracts (prefer longer)"""
        paper1 = Paper(
            title="Test",
            doi="10.1234/test",
            abstract="Short",
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="Test",
            doi="10.1234/test",
            abstract="Much longer abstract with more details",
            sources=[Source.CROSSREF]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 1
        assert result[0].abstract == "Much longer abstract with more details"

    def test_merge_keywords(self, deduplicator):
        """Test merging keywords"""
        paper1 = Paper(
            title="Test",
            doi="10.1234/test",
            keywords=["ML", "AI"],
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="Test",
            doi="10.1234/test",
            keywords=["AI", "DL"],  # One duplicate, one new
            sources=[Source.CROSSREF]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 1
        # Should have all unique keywords
        assert set(result[0].keywords) == {"ML", "AI", "DL"}

    def test_merge_authors(self, deduplicator):
        """Test merging authors (prefer more complete list)"""
        paper1 = Paper(
            title="Test",
            doi="10.1234/test",
            authors=[Author(name="John Doe")],
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="Test",
            doi="10.1234/test",
            authors=[Author(name="John Doe"), Author(name="Jane Smith")],
            sources=[Source.CROSSREF]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 1
        # Should prefer longer author list
        assert len(result[0].authors) == 2

    def test_merge_pdf_urls(self, deduplicator):
        """Test merging PDF URLs (prefer non-empty)"""
        paper1 = Paper(
            title="Test",
            doi="10.1234/test",
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="Test",
            doi="10.1234/test",
            pdf_url="https://example.com/paper.pdf",
            sources=[Source.ARXIV]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 1
        assert str(result[0].pdf_url) == "https://example.com/paper.pdf"

    def test_deduplicate_large_list(self, deduplicator, sample_papers_list):
        """Test deduplication with larger list"""
        # Test deduplication works on large list
        # Add explicit duplicates with matching DOIs
        papers = sample_papers_list + [
            Paper(title="Unique Paper A", doi="10.9999/unique.a", sources=[Source.ARXIV]),
            Paper(title="Unique Paper B", doi="10.9999/unique.b", sources=[Source.CROSSREF]),
            Paper(title="Unique Paper A", doi="10.9999/unique.a", sources=[Source.PUBMED])  # Duplicate of A
        ]

        result = deduplicator.deduplicate(papers)
        # Should merge the duplicate "Unique Paper A" (13 papers - at least 1 duplicate)
        # Don't test exact number since title similarity may match some sample papers
        assert len(result) < len(papers)
        assert len(result) >= len(sample_papers_list)

    def test_title_normalization(self, deduplicator):
        """Test title normalization for comparison"""
        normalized1 = deduplicator._normalize_title("Machine Learning: A Study!")
        normalized2 = deduplicator._normalize_title("Machine Learning A Study")

        assert normalized1 == normalized2
        assert ":" not in normalized1
        assert "!" not in normalized1

    def test_title_similarity_case_insensitive(self, deduplicator):
        """Test that title similarity is case insensitive"""
        assert deduplicator._titles_similar(
            "Machine Learning",
            "machine learning"
        )

    def test_title_similarity_punctuation(self, deduplicator):
        """Test that punctuation doesn't affect similarity"""
        assert deduplicator._titles_similar(
            "Machine Learning: A Study",
            "Machine Learning A Study"
        )

    def test_title_similarity_threshold(self, deduplicator):
        """Test similarity threshold"""
        # These should be similar enough
        assert deduplicator._titles_similar(
            "Machine Learning in Healthcare",
            "Machine Learning in Healthcare Systems"
        )

        # These should not be similar enough
        assert not deduplicator._titles_similar(
            "Machine Learning",
            "Deep Learning Networks"
        )

    def test_priority_doi_over_pmid(self, deduplicator):
        """Test that DOI takes priority over PMID"""
        paper1 = Paper(
            title="Paper 1",
            doi="10.1234/test",
            pmid="12345",
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="Paper 2",
            pmid="12345",  # Same PMID, no DOI
            sources=[Source.CROSSREF]
        )
        paper3 = Paper(
            title="Paper 3",
            doi="10.1234/test",  # Same DOI as paper1
            sources=[Source.ARXIV]
        )

        result = deduplicator.deduplicate([paper1, paper2, paper3])
        # paper1 and paper3 should merge by DOI
        # paper2 is separate despite same PMID as paper1
        assert len(result) == 2

    def test_empty_title_handling(self, deduplicator):
        """Test handling of empty or None titles"""
        paper1 = Paper(title="", sources=[Source.PUBMED])
        paper2 = Paper(title="Test", sources=[Source.ARXIV])

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 2  # Should not crash


class TestEdgeCases:
    """Test edge cases in deduplication"""

    @pytest.fixture
    def deduplicator(self):
        return Deduplicator()

    def test_all_papers_identical(self, deduplicator):
        """Test when all papers are identical"""
        papers = [
            Paper(title="Test", doi="10.1234/test", sources=[Source.PUBMED])
            for _ in range(10)
        ]

        result = deduplicator.deduplicate(papers)
        assert len(result) == 1

    def test_chain_of_duplicates(self, deduplicator):
        """Test chain where A==B by DOI, B==C by PMID"""
        paper_a = Paper(
            title="A",
            doi="10.1234/a",
            sources=[Source.PUBMED]
        )
        paper_b = Paper(
            title="B",
            doi="10.1234/a",  # Same as A
            pmid="12345",
            sources=[Source.CROSSREF]
        )
        paper_c = Paper(
            title="C",
            pmid="12345",  # Same as B
            sources=[Source.ARXIV]
        )

        result = deduplicator.deduplicate([paper_a, paper_b, paper_c])
        # A and B merge by DOI, but C should be separate
        assert len(result) == 2

    def test_unicode_title_similarity(self, deduplicator):
        """Test similarity with unicode characters"""
        paper1 = Paper(
            title="机器学习在医疗中的应用",
            sources=[Source.PUBMED]
        )
        paper2 = Paper(
            title="机器学习在医疗中的应用",
            sources=[Source.ARXIV]
        )

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 1

    def test_very_short_titles(self, deduplicator):
        """Test with very short titles"""
        paper1 = Paper(title="AI", sources=[Source.PUBMED])
        paper2 = Paper(title="ML", sources=[Source.ARXIV])

        result = deduplicator.deduplicate([paper1, paper2])
        assert len(result) == 2  # Should not merge short different titles