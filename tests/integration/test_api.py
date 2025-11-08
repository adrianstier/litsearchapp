"""Integration tests for FastAPI endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import json

from backend.main import app
from src.database.models import Base
from src.database.engine import get_db_session
from src.models import Paper, Author, Source, SearchResult


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing"""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db
client = TestClient(app)


class TestSearchEndpoints:
    """Test search API endpoints"""

    @patch('backend.main.SearchOrchestrator')
    def test_search_papers_success(self, mock_orchestrator_class):
        """Test successful paper search"""
        # Mock search results
        mock_result = Mock(spec=SearchResult)
        mock_result.papers = [
            Paper(
                title="Test Paper",
                doi="10.1234/test",
                authors=[Author(name="John Doe")],
                year=2023,
                sources=[Source.PUBMED]
            )
        ]
        mock_result.total_found = 1
        mock_result.search_time = 1.5
        mock_result.sources_searched = [Source.PUBMED]
        mock_result.get_statistics.return_value = {"pubmed": 1}

        mock_orchestrator = Mock()
        mock_orchestrator.search.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator

        response = client.post("/api/search", json={
            "query": "machine learning",
            "sources": ["pubmed"],
            "max_results": 10
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data["papers"]) == 1
        assert data["total_found"] == 1

    def test_search_papers_invalid_request(self):
        """Test search with invalid request data"""
        response = client.post("/api/search", json={
            "query": "",  # Empty query
            "sources": []
        })

        assert response.status_code == 422  # Validation error

    @patch('backend.main.SearchOrchestrator')
    def test_search_papers_with_filters(self, mock_orchestrator_class):
        """Test search with year filters"""
        mock_result = Mock(spec=SearchResult)
        mock_result.papers = []
        mock_result.total_found = 0
        mock_result.search_time = 0.5
        mock_result.sources_searched = [Source.ARXIV]
        mock_result.get_statistics.return_value = {}

        mock_orchestrator = Mock()
        mock_orchestrator.search.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator

        response = client.post("/api/search", json={
            "query": "COVID-19",
            "sources": ["arxiv"],
            "max_results": 10,
            "year_start": 2020,
            "year_end": 2023
        })

        assert response.status_code == 200

    def test_get_search_history(self):
        """Test retrieving search history"""
        # First do a search
        with patch('backend.main.SearchOrchestrator') as mock_orch:
            mock_result = Mock(spec=SearchResult)
            mock_result.papers = []
            mock_result.total_found = 0
            mock_result.search_time = 1.0
            mock_result.sources_searched = [Source.PUBMED]
            mock_result.get_statistics.return_value = {}

            mock_orch.return_value.search.return_value = mock_result

            client.post("/api/search", json={
                "query": "test query",
                "sources": ["pubmed"],
                "max_results": 5
            })

        # Get history
        response = client.get("/api/search/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPaperEndpoints:
    """Test paper management endpoints"""

    def setup_method(self):
        """Setup test data"""
        Base.metadata.create_all(bind=test_engine)

    def test_get_papers_empty(self):
        """Test getting papers from empty database"""
        response = client.get("/api/papers")

        assert response.status_code == 200
        data = response.json()
        assert data["papers"] == []
        assert data["total"] == 0

    def test_get_papers_pagination(self):
        """Test paper pagination"""
        response = client.get("/api/papers?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert "papers" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_get_paper_not_found(self):
        """Test getting non-existent paper"""
        response = client.get("/api/papers/99999")

        assert response.status_code == 404

    def test_full_text_search(self):
        """Test full-text search"""
        response = client.get("/api/papers/search?q=machine learning")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCollectionEndpoints:
    """Test collection management endpoints"""

    def test_get_collections_empty(self):
        """Test getting collections from empty database"""
        response = client.get("/api/collections")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_collection(self):
        """Test creating a collection"""
        response = client.post("/api/collections", json={
            "name": "My Research",
            "description": "Test collection"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Research"

    def test_create_collection_invalid_data(self):
        """Test creating collection with invalid data"""
        response = client.post("/api/collections", json={
            "name": ""  # Empty name
        })

        assert response.status_code == 422


class TestDownloadEndpoints:
    """Test download endpoints"""

    @patch('backend.main.PDFRetriever')
    def test_download_paper_not_found(self, mock_retriever):
        """Test downloading non-existent paper"""
        response = client.post("/api/download/99999")

        assert response.status_code == 404

    def test_batch_download_empty_list(self):
        """Test batch download with empty list"""
        response = client.post("/api/download/batch", json={
            "paper_ids": []
        })

        assert response.status_code == 422


class TestVisualizationEndpoints:
    """Test visualization data endpoints"""

    def test_get_timeline_data(self):
        """Test getting timeline data"""
        response = client.get("/api/visualize/timeline")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "year_range" in data

    def test_get_citation_network(self):
        """Test getting citation network"""
        response = client.get("/api/visualize/network")

        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "links" in data

    def test_get_topic_clusters(self):
        """Test getting topic clusters"""
        response = client.get("/api/visualize/topics")

        assert response.status_code == 200
        data = response.json()
        assert "clusters" in data

    def test_timeline_with_collection_filter(self):
        """Test timeline filtered by collection"""
        response = client.get("/api/visualize/timeline?collection_id=1")

        assert response.status_code == 200

    def test_network_with_invalid_collection(self):
        """Test network with non-existent collection"""
        response = client.get("/api/visualize/network?collection_id=99999")

        assert response.status_code == 200  # Should return empty data


class TestAuthEndpoints:
    """Test authentication endpoints"""

    @patch('backend.main.UCSBAuth')
    def test_get_auth_status(self, mock_auth_class):
        """Test getting auth status"""
        mock_auth = Mock()
        mock_auth.get_status.return_value = {
            "authenticated": False,
            "message": "Not authenticated"
        }
        mock_auth_class.return_value = mock_auth

        response = client.get("/api/auth/status")

        assert response.status_code == 200
        data = response.json()
        assert "authenticated" in data


class TestStatsEndpoint:
    """Test statistics endpoint"""

    def test_get_stats(self):
        """Test getting application statistics"""
        response = client.get("/api/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_papers" in data
        assert "papers_with_pdfs" in data
        assert "collections_count" in data
        assert "total_searches" in data


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint"""
        response = client.get("/api/invalid/endpoint")

        assert response.status_code == 404

    def test_invalid_http_method(self):
        """Test using invalid HTTP method"""
        response = client.delete("/api/search")

        assert response.status_code == 405  # Method not allowed

    def test_malformed_json(self):
        """Test sending malformed JSON"""
        response = client.post(
            "/api/search",
            content="invalid json{",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self):
        """Test that CORS headers are present"""
        response = client.options("/api/papers")

        assert "access-control-allow-origin" in [h.lower() for h in response.headers]


class TestEndToEndFlow:
    """Test complete workflows"""

    @patch('backend.main.SearchOrchestrator')
    def test_search_and_retrieve_workflow(self, mock_orchestrator_class):
        """Test complete search and retrieval workflow"""
        # Mock search
        mock_result = Mock(spec=SearchResult)
        mock_result.papers = [
            Paper(
                title="End to End Test Paper",
                doi="10.1234/e2e",
                authors=[Author(name="Test Author")],
                year=2023,
                sources=[Source.PUBMED]
            )
        ]
        mock_result.total_found = 1
        mock_result.search_time = 1.0
        mock_result.sources_searched = [Source.PUBMED]
        mock_result.get_statistics.return_value = {"pubmed": 1}

        mock_orchestrator = Mock()
        mock_orchestrator.search.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator

        # Step 1: Search
        search_response = client.post("/api/search", json={
            "query": "test",
            "sources": ["pubmed"],
            "max_results": 10
        })

        assert search_response.status_code == 200
        papers = search_response.json()["papers"]
        assert len(papers) > 0

        # Step 2: Get paper details
        paper_id = papers[0]["id"]
        paper_response = client.get(f"/api/papers/{paper_id}")

        assert paper_response.status_code == 200

        # Step 3: Create collection
        collection_response = client.post("/api/collections", json={
            "name": "E2E Test Collection"
        })

        assert collection_response.status_code == 200
        collection_id = collection_response.json()["id"]

        # Step 4: Add paper to collection
        add_response = client.post(
            f"/api/collections/{collection_id}/papers/{paper_id}"
        )

        assert add_response.status_code == 200

    @patch('backend.main.SearchOrchestrator')
    def test_search_and_visualize_workflow(self, mock_orchestrator_class):
        """Test search followed by visualization"""
        # Mock search with papers from different years
        mock_result = Mock(spec=SearchResult)
        mock_result.papers = [
            Paper(title=f"Paper {i}", year=2020 + i, sources=[Source.PUBMED])
            for i in range(3)
        ]
        mock_result.total_found = 3
        mock_result.search_time = 1.0
        mock_result.sources_searched = [Source.PUBMED]
        mock_result.get_statistics.return_value = {"pubmed": 3}

        mock_orchestrator = Mock()
        mock_orchestrator.search.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator

        # Step 1: Search
        search_response = client.post("/api/search", json={
            "query": "test",
            "sources": ["pubmed"],
            "max_results": 10
        })

        assert search_response.status_code == 200

        # Step 2: Get timeline visualization
        timeline_response = client.get("/api/visualize/timeline")

        assert timeline_response.status_code == 200
        timeline_data = timeline_response.json()
        assert len(timeline_data["data"]) > 0


class TestPerformance:
    """Test performance characteristics"""

    def test_pagination_performance(self):
        """Test that pagination works efficiently"""
        # Test various page sizes
        for page_size in [10, 20, 50]:
            response = client.get(f"/api/papers?page=1&page_size={page_size}")
            assert response.status_code == 200

    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import threading

        results = []

        def make_request():
            response = client.get("/api/stats")
            results.append(response.status_code == 200)

        threads = [threading.Thread(target=make_request) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(results)


class TestValidation:
    """Test input validation"""

    def test_negative_page_number(self):
        """Test negative page number"""
        response = client.get("/api/papers?page=-1")

        assert response.status_code == 422

    def test_excessive_page_size(self):
        """Test excessively large page size"""
        response = client.get("/api/papers?page=1&page_size=10000")

        assert response.status_code == 422

    def test_invalid_year_range(self):
        """Test invalid year range"""
        response = client.post("/api/search", json={
            "query": "test",
            "sources": ["pubmed"],
            "max_results": 10,
            "year_start": 2023,
            "year_end": 2020  # End before start
        })

        assert response.status_code == 422

    def test_empty_collection_name(self):
        """Test creating collection with empty name"""
        response = client.post("/api/collections", json={
            "name": "   "  # Whitespace only
        })

        assert response.status_code == 422

    def test_sql_injection_attempt(self):
        """Test SQL injection prevention"""
        response = client.get("/api/papers/search?q='; DROP TABLE papers; --")

        # Should not crash, should sanitize input
        assert response.status_code in [200, 422]
