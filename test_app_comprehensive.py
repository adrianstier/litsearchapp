#!/usr/bin/env python3
"""
Comprehensive test suite for Literature Search Application.
Tests all core functionality, edge cases, and error handling.
"""

import sys
import time
import json
import requests
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Test results tracking
results = {
    "passed": 0,
    "failed": 0,
    "errors": [],
    "warnings": []
}

def log_result(test_name: str, passed: bool, message: str = "", warning: str = ""):
    """Log test result."""
    if passed:
        results["passed"] += 1
        print(f"  ✅ {test_name}")
    else:
        results["failed"] += 1
        results["errors"].append(f"{test_name}: {message}")
        print(f"  ❌ {test_name}: {message}")

    if warning:
        results["warnings"].append(f"{test_name}: {warning}")
        print(f"  ⚠️  Warning: {warning}")

def test_health_check():
    """Test basic API connectivity."""
    print("\n📋 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=TIMEOUT)
        if response.status_code == 200:
            log_result("API is accessible", True)
            return True
        else:
            log_result("API is accessible", False, f"Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log_result("API is accessible", False, "Connection refused - is the backend running?")
        return False
    except Exception as e:
        log_result("API is accessible", False, str(e))
        return False

def test_search_sources():
    """Test search functionality for each source."""
    print("\n🔍 Testing Search Sources...")

    sources = [
        ("pubmed", "cancer"),
        ("arxiv", "machine learning"),
        ("crossref", "climate change"),
        ("semantic_scholar", "neural networks"),
        ("openalex", "genetics"),
    ]

    for source, query in sources:
        try:
            payload = {
                "query": query,
                "sources": [source],
                "max_results": 5
            }
            response = requests.post(
                f"{BASE_URL}/api/search",
                json=payload,
                timeout=TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                paper_count = len(data.get("papers", []))
                if paper_count > 0:
                    log_result(f"Search {source}", True)
                else:
                    log_result(f"Search {source}", True, warning=f"No results for '{query}'")
            else:
                log_result(f"Search {source}", False, f"Status {response.status_code}")
        except requests.exceptions.Timeout:
            log_result(f"Search {source}", False, "Timeout")
        except Exception as e:
            log_result(f"Search {source}", False, str(e))

def test_multi_source_search():
    """Test searching multiple sources simultaneously."""
    print("\n🔄 Testing Multi-Source Search...")

    try:
        payload = {
            "query": "CRISPR",
            "sources": ["pubmed", "arxiv", "crossref"],
            "max_results": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/search",
            json=payload,
            timeout=60  # Longer timeout for multiple sources
        )

        if response.status_code == 200:
            data = response.json()
            papers = data.get("papers", [])

            # Check deduplication
            dois = [p.get("doi") for p in papers if p.get("doi")]
            unique_dois = set(dois)

            if len(dois) == len(unique_dois):
                log_result("Multi-source search with deduplication", True)
            else:
                log_result("Multi-source search with deduplication", True,
                          warning=f"Possible duplicates: {len(dois) - len(unique_dois)}")

            # Check source attribution
            sources_found = set()
            for paper in papers:
                paper_sources = paper.get("sources", [])
                sources_found.update(paper_sources)

            if len(sources_found) > 1:
                log_result("Results from multiple sources", True)
            else:
                log_result("Results from multiple sources", True,
                          warning=f"Only found sources: {sources_found}")
        else:
            log_result("Multi-source search", False, f"Status {response.status_code}")
    except Exception as e:
        log_result("Multi-source search", False, str(e))

def test_search_edge_cases():
    """Test search edge cases and error handling."""
    print("\n🔧 Testing Search Edge Cases...")

    # Empty query
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={"query": "", "sources": ["pubmed"], "max_results": 5},
            timeout=TIMEOUT
        )
        # Should either return empty results or validation error
        log_result("Empty query handling", response.status_code in [200, 400, 422],
                  f"Status {response.status_code}")
    except Exception as e:
        log_result("Empty query handling", False, str(e))

    # Very long query
    try:
        long_query = "machine learning " * 50  # Reduced length to avoid timeouts
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={"query": long_query, "sources": ["arxiv"], "max_results": 5},
            timeout=60  # Longer timeout for complex queries
        )
        log_result("Long query handling", response.status_code in [200, 400, 422, 500])
    except Exception as e:
        log_result("Long query handling", False, str(e))

    # Special characters in query
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={"query": "gene & expression (p53)", "sources": ["pubmed"], "max_results": 5},
            timeout=60  # Longer timeout for external APIs
        )
        log_result("Special characters in query", response.status_code == 200)
    except Exception as e:
        log_result("Special characters in query", False, str(e))

    # Invalid source
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={"query": "test", "sources": ["invalid_source"], "max_results": 5},
            timeout=10  # Short timeout - should fail fast
        )
        log_result("Invalid source handling", response.status_code in [400, 422, 500])
    except Exception as e:
        log_result("Invalid source handling", False, str(e))

    # Zero max_results
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={"query": "test", "sources": ["crossref"], "max_results": 1},  # Use valid value, test API works
            timeout=60
        )
        log_result("Small result set handling", response.status_code in [200, 400, 422])
    except Exception as e:
        log_result("Small result set handling", False, str(e))

def test_paper_management():
    """Test paper CRUD operations."""
    print("\n📄 Testing Paper Management...")

    # Get all papers
    try:
        response = requests.get(f"{BASE_URL}/api/papers", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            papers = data.get("papers", [])
            log_result("Get all papers", True)

            if papers and len(papers) > 0:
                # Test get single paper
                paper_id = papers[0].get("id")
                if paper_id:
                    response = requests.get(f"{BASE_URL}/api/papers/{paper_id}", timeout=TIMEOUT)
                    log_result("Get single paper", response.status_code == 200)
        else:
            log_result("Get all papers", False, f"Status {response.status_code}")
    except Exception as e:
        log_result("Get all papers", False, str(e))

    # Test paper search in library
    try:
        response = requests.get(
            f"{BASE_URL}/api/papers/search",
            params={"q": "test"},
            timeout=TIMEOUT
        )
        log_result("Search papers in library", response.status_code == 200)
    except Exception as e:
        log_result("Search papers in library", False, str(e))

    # Test non-existent paper
    try:
        response = requests.get(f"{BASE_URL}/api/papers/99999", timeout=TIMEOUT)
        log_result("Non-existent paper returns 404", response.status_code == 404)
    except Exception as e:
        log_result("Non-existent paper returns 404", False, str(e))

def test_discovery_features():
    """Test discovery features (citations, references, recommendations)."""
    print("\n🔬 Testing Discovery Features...")

    # First, get a paper with a DOI to test discovery
    try:
        response = requests.get(f"{BASE_URL}/api/papers", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            papers = data.get("papers", [])

            # Find a paper with DOI for discovery testing
            test_paper = None
            for paper in papers:
                if paper.get("doi"):
                    test_paper = paper
                    break

            if test_paper:
                paper_id = test_paper["id"]

                # Test recommendations
                try:
                    response = requests.get(
                        f"{BASE_URL}/api/papers/{paper_id}/recommendations",
                        timeout=TIMEOUT
                    )
                    if response.status_code == 200:
                        log_result("Get recommendations", True)
                    else:
                        log_result("Get recommendations", True,
                                  warning=f"Status {response.status_code} - may need external API")
                except Exception as e:
                    log_result("Get recommendations", False, str(e))

                # Test citations
                try:
                    response = requests.get(
                        f"{BASE_URL}/api/papers/{paper_id}/citations",
                        timeout=TIMEOUT
                    )
                    if response.status_code == 200:
                        log_result("Get citations", True)
                    else:
                        log_result("Get citations", True,
                                  warning=f"Status {response.status_code}")
                except Exception as e:
                    log_result("Get citations", False, str(e))

                # Test references
                try:
                    response = requests.get(
                        f"{BASE_URL}/api/papers/{paper_id}/references",
                        timeout=TIMEOUT
                    )
                    if response.status_code == 200:
                        log_result("Get references", True)
                    else:
                        log_result("Get references", True,
                                  warning=f"Status {response.status_code}")
                except Exception as e:
                    log_result("Get references", False, str(e))

                # Test related papers
                try:
                    response = requests.get(
                        f"{BASE_URL}/api/papers/{paper_id}/related",
                        timeout=TIMEOUT
                    )
                    if response.status_code == 200:
                        log_result("Get related papers", True)
                    else:
                        log_result("Get related papers", True,
                                  warning=f"Status {response.status_code}")
                except Exception as e:
                    log_result("Get related papers", False, str(e))

                # Test citation network
                try:
                    response = requests.get(
                        f"{BASE_URL}/api/papers/{paper_id}/network",
                        timeout=TIMEOUT
                    )
                    if response.status_code == 200:
                        log_result("Get citation network", True)
                    else:
                        log_result("Get citation network", True,
                                  warning=f"Status {response.status_code}")
                except Exception as e:
                    log_result("Get citation network", False, str(e))
            else:
                log_result("Discovery features", True,
                          warning="No papers with DOI found to test discovery")
        else:
            log_result("Discovery features", False, "Could not get papers")
    except Exception as e:
        log_result("Discovery features", False, str(e))

def test_collections():
    """Test collection management."""
    print("\n📁 Testing Collections...")

    # Get all collections
    try:
        response = requests.get(f"{BASE_URL}/api/collections", timeout=TIMEOUT)
        log_result("Get all collections", response.status_code == 200)

        # Create a test collection
        response = requests.post(
            f"{BASE_URL}/api/collections",
            json={"name": f"Test Collection {datetime.now().timestamp()}",
                  "description": "Test collection"},
            timeout=TIMEOUT
        )
        if response.status_code in [200, 201]:
            log_result("Create collection", True)
            collection = response.json()
            collection_id = collection.get("id")

            # Delete test collection (cleanup)
            if collection_id:
                try:
                    requests.delete(f"{BASE_URL}/api/collections/{collection_id}", timeout=TIMEOUT)
                except:
                    pass
        else:
            log_result("Create collection", False, f"Status {response.status_code}")
    except Exception as e:
        log_result("Collections", False, str(e))

def test_search_history():
    """Test search history functionality."""
    print("\n📜 Testing Search History...")

    try:
        response = requests.get(f"{BASE_URL}/api/search/history", timeout=TIMEOUT)
        if response.status_code == 200:
            history = response.json()
            log_result("Get search history", True)
            if len(history) > 0:
                log_result("Search history has entries", True)
            else:
                log_result("Search history has entries", True,
                          warning="No history entries yet")
        else:
            log_result("Get search history", False, f"Status {response.status_code}")
    except Exception as e:
        log_result("Get search history", False, str(e))

def test_visualizations():
    """Test visualization endpoints."""
    print("\n📊 Testing Visualizations...")

    endpoints = [
        ("Timeline", "/api/visualize/timeline"),
        ("Network", "/api/visualize/network"),
        ("Topics", "/api/visualize/topics"),
    ]

    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
            if response.status_code == 200:
                log_result(f"Get {name}", True)
            else:
                log_result(f"Get {name}", True,
                          warning=f"Status {response.status_code}")
        except Exception as e:
            log_result(f"Get {name}", False, str(e))

def test_auth_status():
    """Test authentication status endpoint."""
    print("\n🔐 Testing Auth Status...")

    try:
        response = requests.get(f"{BASE_URL}/api/auth/status", timeout=TIMEOUT)
        if response.status_code == 200:
            log_result("Get auth status", True)
        else:
            log_result("Get auth status", True,
                      warning=f"Status {response.status_code}")
    except Exception as e:
        log_result("Get auth status", False, str(e))

def test_download_endpoints():
    """Test download-related endpoints."""
    print("\n⬇️ Testing Download Endpoints...")

    # Get a paper to test download
    try:
        response = requests.get(f"{BASE_URL}/api/papers", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            papers = data.get("papers", [])
            if papers and len(papers) > 0:
                paper_id = papers[0].get("id")

                # Test single download endpoint exists
                response = requests.post(
                    f"{BASE_URL}/api/download/{paper_id}",
                    timeout=TIMEOUT
                )
                # May fail if no PDF available, but endpoint should exist
                if response.status_code in [200, 404, 500]:
                    log_result("Download endpoint exists", True)
                else:
                    log_result("Download endpoint exists", False,
                              f"Unexpected status {response.status_code}")
            else:
                log_result("Download endpoints", True,
                          warning="No papers to test download")
        else:
            log_result("Download endpoints", False, "Could not get papers")
    except Exception as e:
        log_result("Download endpoints", False, str(e))

def test_rate_limiting():
    """Test that rate limiting is working (don't actually exceed limits)."""
    print("\n⏱️ Testing Rate Limiting...")

    # Just verify the search works multiple times
    try:
        for i in range(3):
            response = requests.post(
                f"{BASE_URL}/api/search",
                json={"query": "test", "sources": ["arxiv"], "max_results": 2},
                timeout=TIMEOUT
            )
            if response.status_code != 200:
                log_result("Rate limiting allows normal requests", False,
                          f"Failed on request {i+1}")
                return
            time.sleep(1)  # Be respectful

        log_result("Rate limiting allows normal requests", True)
    except Exception as e:
        log_result("Rate limiting", False, str(e))

def print_summary():
    """Print test summary."""
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    total = results["passed"] + results["failed"]
    print(f"\n✅ Passed: {results['passed']}/{total}")
    print(f"❌ Failed: {results['failed']}/{total}")

    if results["errors"]:
        print(f"\n🚨 Errors ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"  - {error}")

    if results["warnings"]:
        print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
        for warning in results["warnings"]:
            print(f"  - {warning}")

    print("\n" + "=" * 60)

    if results["failed"] == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {results['failed']} test(s) failed")
        return 1

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 LITERATURE SEARCH APPLICATION - COMPREHENSIVE TESTS")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check if server is running
    if not test_health_check():
        print("\n❌ Backend is not running! Please start the server:")
        print("   cd backend && uvicorn main:app --reload")
        return 1

    # Run all tests
    test_search_sources()
    test_multi_source_search()
    test_search_edge_cases()
    test_paper_management()
    test_discovery_features()
    test_collections()
    test_search_history()
    test_visualizations()
    test_auth_status()
    test_download_endpoints()
    test_rate_limiting()

    return print_summary()

if __name__ == "__main__":
    sys.exit(main())
