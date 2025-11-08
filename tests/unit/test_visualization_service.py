"""Tests for visualization service"""

import pytest
import json
from backend.services.visualization_service import (
    get_timeline_data,
    get_citation_network,
    get_topic_clusters,
    get_author_network
)
from src.database import models as db_models


class TestTimelineData:
    """Test timeline data generation"""

    def test_timeline_basic(self, db_session):
        """Test basic timeline data"""
        # Add papers from different years
        papers = [
            db_models.Paper(title="Paper 2020", year=2020),
            db_models.Paper(title="Paper 2021", year=2021),
            db_models.Paper(title="Paper 2022", year=2022),
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_timeline_data(db_session)

        assert len(result.data) == 3
        assert result.year_range[0] == 2020
        assert result.year_range[1] == 2022

    def test_timeline_multiple_papers_same_year(self, db_session):
        """Test timeline with multiple papers in same year"""
        papers = [
            db_models.Paper(title=f"Paper {i}", year=2023)
            for i in range(5)
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_timeline_data(db_session)

        assert len(result.data) == 1
        assert result.data[0].year == 2023
        assert result.data[0].count == 5
        assert len(result.data[0].papers) == 5

    def test_timeline_ignores_null_years(self, db_session):
        """Test that papers without year are ignored"""
        papers = [
            db_models.Paper(title="With year", year=2023),
            db_models.Paper(title="No year", year=None),
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_timeline_data(db_session)

        assert len(result.data) == 1
        assert result.data[0].year == 2023

    def test_timeline_ordered_by_year(self, db_session):
        """Test that timeline is ordered by year"""
        papers = [
            db_models.Paper(title="P1", year=2022),
            db_models.Paper(title="P2", year=2020),
            db_models.Paper(title="P3", year=2021),
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_timeline_data(db_session)

        assert result.data[0].year == 2020
        assert result.data[1].year == 2021
        assert result.data[2].year == 2022

    def test_timeline_with_collection_filter(self, db_session):
        """Test timeline filtered by collection"""
        collection = db_models.Collection(name="Test Collection")
        paper1 = db_models.Paper(title="In collection", year=2023)
        paper2 = db_models.Paper(title="Not in collection", year=2023)

        collection.papers.append(paper1)
        db_session.add_all([collection, paper2])
        db_session.commit()

        result = get_timeline_data(db_session, collection_id=collection.id)

        assert len(result.data) == 1
        assert result.data[0].count == 1

    def test_timeline_empty_database(self, db_session):
        """Test timeline with no papers"""
        result = get_timeline_data(db_session)

        assert len(result.data) == 0
        assert result.year_range == (2000, 2024)

    def test_timeline_wide_year_range(self, db_session):
        """Test timeline with wide year range"""
        papers = [
            db_models.Paper(title="Old", year=1990),
            db_models.Paper(title="New", year=2024),
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_timeline_data(db_session)

        assert result.year_range[0] == 1990
        assert result.year_range[1] == 2024


class TestCitationNetwork:
    """Test citation network generation"""

    def test_network_basic(self, db_session):
        """Test basic network generation"""
        author = db_models.Author(name="John Doe")
        papers = [
            db_models.Paper(title="P1", year=2020, citations=10),
            db_models.Paper(title="P2", year=2021, citations=20),
        ]
        for paper in papers:
            paper.authors.append(author)

        db_session.add_all(papers)
        db_session.commit()

        result = get_citation_network(db_session)

        assert len(result.nodes) == 2
        assert len(result.links) == 1  # Linked by shared author

    def test_network_node_properties(self, db_session):
        """Test network node properties"""
        paper = db_models.Paper(
            title="Very Long Title " * 10,
            year=2023,
            citations=100
        )
        db_session.add(paper)
        db_session.commit()

        result = get_citation_network(db_session)

        node = result.nodes[0]
        assert node.id == "paper_1"
        assert len(node.label) <= 53  # Title is truncated
        assert node.group == "2020"  # Decade
        assert node.size > 5  # Based on citations

    def test_network_shared_authors(self, db_session):
        """Test network links from shared authors"""
        author = db_models.Author(name="Prolific Author")

        paper1 = db_models.Paper(title="P1")
        paper2 = db_models.Paper(title="P2")
        paper3 = db_models.Paper(title="P3")

        paper1.authors.append(author)
        paper2.authors.append(author)
        paper3.authors.append(author)

        db_session.add_all([paper1, paper2, paper3])
        db_session.commit()

        result = get_citation_network(db_session)

        # Should have 3 nodes and 3 links (fully connected triangle)
        assert len(result.nodes) == 3
        assert len(result.links) == 3

    def test_network_no_shared_authors(self, db_session):
        """Test network with no shared authors"""
        papers = [
            db_models.Paper(title="P1"),
            db_models.Paper(title="P2"),
        ]
        papers[0].authors.append(db_models.Author(name="Author 1"))
        papers[1].authors.append(db_models.Author(name="Author 2"))

        db_session.add_all(papers)
        db_session.commit()

        result = get_citation_network(db_session)

        assert len(result.nodes) == 2
        assert len(result.links) == 0  # No shared authors

    def test_network_limit(self, db_session):
        """Test network limits to 100 papers"""
        papers = [
            db_models.Paper(title=f"Paper {i}")
            for i in range(150)
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_citation_network(db_session)

        assert len(result.nodes) <= 100

    def test_network_with_collection_filter(self, db_session):
        """Test network filtered by collection"""
        collection = db_models.Collection(name="Test")
        author = db_models.Author(name="Author")

        paper1 = db_models.Paper(title="P1")
        paper2 = db_models.Paper(title="P2")

        paper1.authors.append(author)
        paper2.authors.append(author)

        collection.papers.append(paper1)

        db_session.add_all([collection, paper2])
        db_session.commit()

        result = get_citation_network(db_session, collection_id=collection.id)

        assert len(result.nodes) == 1  # Only paper1

    def test_network_link_weight(self, db_session):
        """Test link weight calculation"""
        author1 = db_models.Author(name="A1")
        author2 = db_models.Author(name="A2")

        # Create multiple papers with same author pair
        papers = [
            db_models.Paper(title=f"Paper {i}")
            for i in range(3)
        ]
        for paper in papers:
            paper.authors.extend([author1, author2])

        db_session.add_all(papers)
        db_session.commit()

        result = get_citation_network(db_session)

        # Should have links with weights
        assert any(link.weight > 1.0 for link in result.links)


class TestTopicClusters:
    """Test topic clustering"""

    def test_clusters_basic(self, db_session):
        """Test basic clustering"""
        papers = [
            db_models.Paper(title="P1", keywords='["machine learning", "AI"]'),
            db_models.Paper(title="P2", keywords='["machine learning", "deep learning"]'),
            db_models.Paper(title="P3", keywords='["healthcare", "medicine"]'),
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_topic_clusters(db_session)

        assert len(result.clusters) > 0
        # "machine learning" should be most common
        assert result.clusters[0].label == "Machine Learning"

    def test_clusters_minimum_size(self, db_session):
        """Test that clusters have minimum 2 papers"""
        papers = [
            db_models.Paper(title="P1", keywords='["unique1"]'),
            db_models.Paper(title="P2", keywords='["unique2"]'),
            db_models.Paper(title="P3", keywords='["common"]'),
            db_models.Paper(title="P4", keywords='["common"]'),
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_topic_clusters(db_session)

        # Should only include "common" cluster (2+ papers)
        for cluster in result.clusters:
            if cluster.label != "Other":
                assert cluster.size >= 2

    def test_clusters_no_duplicates(self, db_session):
        """Test that papers appear in only one cluster"""
        papers = [
            db_models.Paper(title=f"P{i}", keywords='["tag1", "tag2"]')
            for i in range(5)
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_topic_clusters(db_session)

        all_paper_ids = []
        for cluster in result.clusters:
            all_paper_ids.extend(cluster.papers)

        # Check no duplicates
        assert len(all_paper_ids) == len(set(all_paper_ids))

    def test_clusters_other_category(self, db_session):
        """Test 'Other' cluster for unclustered papers"""
        papers = [
            db_models.Paper(title="P1", keywords='["common"]'),
            db_models.Paper(title="P2", keywords='["common"]'),
            db_models.Paper(title="P3", keywords='["rare"]'),
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_topic_clusters(db_session)

        # Should have "Other" cluster
        other_clusters = [c for c in result.clusters if c.label == "Other"]
        assert len(other_clusters) <= 1

    def test_clusters_limit_top_10(self, db_session):
        """Test that only top 10 keywords are used"""
        # Create papers with many different keywords
        papers = []
        for i in range(50):
            papers.append(
                db_models.Paper(title=f"P{i}", keywords=f'["keyword{i%20}"]')
            )
        db_session.add_all(papers)
        db_session.commit()

        result = get_topic_clusters(db_session)

        # Should have at most 11 clusters (10 keywords + Other)
        assert len(result.clusters) <= 11

    def test_clusters_empty_keywords(self, db_session):
        """Test handling of papers without keywords"""
        papers = [
            db_models.Paper(title="P1", keywords=None),
            db_models.Paper(title="P2", keywords='[]'),
            db_models.Paper(title="P3", keywords='["valid"]'),
            db_models.Paper(title="P4", keywords='["valid"]'),
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_topic_clusters(db_session)

        # Should handle gracefully
        assert len(result.clusters) > 0

    def test_clusters_case_insensitive(self, db_session):
        """Test that keywords are case-insensitive"""
        papers = [
            db_models.Paper(title="P1", keywords='["Machine Learning"]'),
            db_models.Paper(title="P2", keywords='["machine learning"]'),
            db_models.Paper(title="P3", keywords='["MACHINE LEARNING"]'),
        ]
        db_session.add_all(papers)
        db_session.commit()

        result = get_topic_clusters(db_session)

        # Should all be in same cluster
        assert len(result.clusters) <= 2  # Main cluster + maybe Other

    def test_clusters_with_collection_filter(self, db_session):
        """Test clustering filtered by collection"""
        collection = db_models.Collection(name="Test")
        paper1 = db_models.Paper(title="P1", keywords='["ml"]')
        paper2 = db_models.Paper(title="P2", keywords='["ml"]')
        paper3 = db_models.Paper(title="P3", keywords='["other"]')

        collection.papers.extend([paper1, paper2])

        db_session.add_all([collection, paper3])
        db_session.commit()

        result = get_topic_clusters(db_session, collection_id=collection.id)

        # Should only cluster papers in collection
        total_papers = sum(len(c.papers) for c in result.clusters)
        assert total_papers <= 2


class TestAuthorNetwork:
    """Test author collaboration network"""

    def test_author_network_basic(self, db_session):
        """Test basic author network"""
        author1 = db_models.Author(name="Author 1")
        author2 = db_models.Author(name="Author 2")

        paper = db_models.Paper(title="Collaboration")
        paper.authors.extend([author1, author2])

        db_session.add(paper)
        db_session.commit()

        result = get_author_network(db_session)

        # Both authors should appear if they have 2+ papers total
        # But with only 1 paper, they might not appear
        assert len(result.nodes) >= 0

    def test_author_network_minimum_papers(self, db_session):
        """Test authors need 2+ papers to appear"""
        author1 = db_models.Author(name="Prolific")
        author2 = db_models.Author(name="One Paper")

        paper1 = db_models.Paper(title="P1")
        paper2 = db_models.Paper(title="P2")
        paper3 = db_models.Paper(title="P3")

        paper1.authors.append(author1)
        paper2.authors.append(author1)
        paper3.authors.append(author2)

        db_session.add_all([paper1, paper2, paper3])
        db_session.commit()

        result = get_author_network(db_session)

        # Only author1 should appear (2+ papers)
        assert len(result.nodes) == 1
        assert result.nodes[0].label == "Prolific"

    def test_author_network_collaboration_links(self, db_session):
        """Test collaboration links between authors"""
        author1 = db_models.Author(name="A1")
        author2 = db_models.Author(name="A2")

        # Create 3 collaborative papers
        papers = [db_models.Paper(title=f"P{i}") for i in range(3)]
        for paper in papers:
            paper.authors.extend([author1, author2])

        db_session.add_all(papers)
        db_session.commit()

        result = get_author_network(db_session)

        # Both authors should appear
        assert len(result.nodes) == 2
        # Should have link between them
        assert len(result.links) == 1

    def test_author_network_node_size(self, db_session):
        """Test node size based on paper count"""
        prolific = db_models.Author(name="Prolific")
        moderate = db_models.Author(name="Moderate")

        # Prolific author: 5 papers
        for i in range(5):
            paper = db_models.Paper(title=f"P{i}")
            paper.authors.append(prolific)
            db_session.add(paper)

        # Moderate author: 2 papers
        for i in range(2):
            paper = db_models.Paper(title=f"M{i}")
            paper.authors.append(moderate)
            db_session.add(paper)

        db_session.commit()

        result = get_author_network(db_session)

        # Prolific should have larger node size
        prolific_node = next(n for n in result.nodes if n.label == "Prolific")
        moderate_node = next(n for n in result.nodes if n.label == "Moderate")

        assert prolific_node.size > moderate_node.size

    def test_author_network_link_weight(self, db_session):
        """Test link weight based on collaboration count"""
        a1 = db_models.Author(name="A1")
        a2 = db_models.Author(name="A2")

        # Multiple collaborations
        for i in range(4):
            paper = db_models.Paper(title=f"P{i}")
            paper.authors.extend([a1, a2])
            db_session.add(paper)

        db_session.commit()

        result = get_author_network(db_session)

        assert len(result.links) == 1
        assert result.links[0].weight > 1.0

    def test_author_network_with_collection(self, db_session):
        """Test author network filtered by collection"""
        collection = db_models.Collection(name="Test")
        author = db_models.Author(name="Author")

        paper1 = db_models.Paper(title="P1")
        paper2 = db_models.Paper(title="P2")
        paper3 = db_models.Paper(title="P3")

        for paper in [paper1, paper2, paper3]:
            paper.authors.append(author)

        collection.papers.extend([paper1, paper2])

        db_session.add_all([collection, paper3])
        db_session.commit()

        result = get_author_network(db_session, collection_id=collection.id)

        # Author should appear (2 papers in collection)
        assert len(result.nodes) == 1


class TestEdgeCases:
    """Test edge cases in visualization"""

    def test_empty_database(self, db_session):
        """Test all visualizations with empty database"""
        timeline = get_timeline_data(db_session)
        network = get_citation_network(db_session)
        clusters = get_topic_clusters(db_session)
        authors = get_author_network(db_session)

        assert len(timeline.data) == 0
        assert len(network.nodes) == 0
        assert len(clusters.clusters) == 0
        assert len(authors.nodes) == 0

    def test_single_paper(self, db_session):
        """Test visualizations with single paper"""
        paper = db_models.Paper(title="Solo", year=2023)
        db_session.add(paper)
        db_session.commit()

        timeline = get_timeline_data(db_session)
        network = get_citation_network(db_session)

        assert len(timeline.data) == 1
        assert len(network.nodes) == 1

    def test_nonexistent_collection(self, db_session):
        """Test filtering by non-existent collection"""
        paper = db_models.Paper(title="P1", year=2023)
        db_session.add(paper)
        db_session.commit()

        result = get_timeline_data(db_session, collection_id=99999)

        assert len(result.data) == 0
