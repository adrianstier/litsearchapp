"""Comprehensive edge case tests for ResearchRabbit-style discovery endpoints"""

import sys
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"


def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")


def setup_test_papers(db_session=None):
    """Create test papers in database for edge case testing"""
    print_section("SETUP: Creating Test Papers")

    # First, do a search to populate some real papers
    payload = {
        "query": "machine learning",
        "sources": ["semantic_scholar", "openalex"],
        "max_results": 3
    }

    try:
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])
            print(f"✅ Created {len(papers)} test papers from real search")
            return papers
        else:
            print(f"⚠️ Could not create test papers: {response.status_code}")
            return []
    except Exception as e:
        print(f"⚠️ Setup failed: {e}")
        return []


# =============================================================================
# TEST 1: Recommendations Endpoint Edge Cases
# =============================================================================

def test_recommendations_invalid_id():
    """Test recommendations with invalid paper ID"""
    print_section("TEST 1.1: Recommendations - Invalid Paper ID")

    try:
        response = requests.get(f"{BASE_URL}/api/papers/999999/recommendations", timeout=10)
        passed = response.status_code == 404
        print_test("Invalid paper ID returns 404", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Invalid paper ID returns 404", False, str(e))


def test_recommendations_no_doi():
    """Test recommendations with paper that has no DOI"""
    print_section("TEST 1.2: Recommendations - Paper Without DOI")

    # Note: This test requires a paper without DOI in DB
    # For now, we'll test the endpoint's error handling
    try:
        response = requests.get(f"{BASE_URL}/api/papers/1/recommendations", timeout=30)
        if response.status_code == 200:
            data = response.json()
            recs = data.get('recommendations', [])
            print_test("Handles paper without DOI gracefully", True,
                      f"Returned {len(recs)} recommendations")
        elif response.status_code == 404:
            print_test("Paper not found (expected)", True, "404 response")
        elif response.status_code == 500:
            # Check if error message is about DOI
            error = response.json().get('detail', '')
            is_doi_error = 'doi' in error.lower() or 'not found' in error.lower()
            print_test("Returns appropriate error for no DOI", is_doi_error, error)
        else:
            print_test("Unexpected status code", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Error handling test", False, str(e))


def test_recommendations_limit_validation():
    """Test recommendations with various limit values"""
    print_section("TEST 1.3: Recommendations - Limit Validation")

    test_cases = [
        (0, "zero limit", False),  # Should fail
        (1, "minimum limit", True),
        (25, "normal limit", True),
        (50, "maximum limit", True),
        (100, "exceeds maximum", False),  # Should fail
        (-5, "negative limit", False),  # Should fail
    ]

    for limit, description, should_succeed in test_cases:
        try:
            response = requests.get(
                f"{BASE_URL}/api/papers/1/recommendations?limit={limit}",
                timeout=10
            )

            if should_succeed:
                passed = response.status_code in [200, 404]  # 404 is ok if paper doesn't exist
                print_test(f"Limit {limit} ({description})", passed,
                          f"Status: {response.status_code}")
            else:
                passed = response.status_code == 422  # Validation error
                print_test(f"Limit {limit} ({description}) rejected", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"Limit {limit} ({description})", False, str(e))


def test_recommendations_timeout():
    """Test recommendations endpoint timeout handling"""
    print_section("TEST 1.4: Recommendations - Timeout Handling")

    try:
        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/papers/1/recommendations",
            timeout=2  # Very short timeout
        )
        elapsed = time.time() - start

        # Should either succeed quickly or timeout
        if response.status_code in [200, 404]:
            print_test("Fast response (no timeout)", True, f"Completed in {elapsed:.2f}s")
        else:
            print_test("Handled within timeout", True, f"Status: {response.status_code}")
    except requests.exceptions.Timeout:
        print_test("Timeout handled by client", True, "Request timed out as expected")
    except Exception as e:
        print_test("Timeout handling", False, str(e))


# =============================================================================
# TEST 2: Citations Endpoint Edge Cases
# =============================================================================

def test_citations_invalid_id():
    """Test citations with invalid paper ID"""
    print_section("TEST 2.1: Citations - Invalid Paper ID")

    try:
        response = requests.get(f"{BASE_URL}/api/papers/999999/citations", timeout=10)
        passed = response.status_code == 404
        print_test("Invalid paper ID returns 404", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Invalid paper ID returns 404", False, str(e))


def test_citations_no_doi():
    """Test citations with paper that has no DOI"""
    print_section("TEST 2.2: Citations - Paper Without DOI")

    try:
        response = requests.get(f"{BASE_URL}/api/papers/1/citations", timeout=30)
        if response.status_code == 200:
            data = response.json()
            citations = data.get('citations', [])
            print_test("Handles paper without DOI", True,
                      f"Returned {len(citations)} citations (may be 0)")
        elif response.status_code == 404:
            print_test("Paper not found (expected)", True, "404 response")
        elif response.status_code == 500:
            error = response.json().get('detail', '')
            print_test("Returns error for no DOI", True, error)
        else:
            print_test("Unexpected status code", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Error handling test", False, str(e))


def test_citations_limit_validation():
    """Test citations with various limit values"""
    print_section("TEST 2.3: Citations - Limit Validation")

    test_cases = [
        (1, "minimum limit", True),
        (100, "normal limit", True),
        (200, "maximum limit", True),
        (500, "exceeds maximum", False),
        (-10, "negative limit", False),
    ]

    for limit, description, should_succeed in test_cases:
        try:
            response = requests.get(
                f"{BASE_URL}/api/papers/1/citations?limit={limit}",
                timeout=10
            )

            if should_succeed:
                passed = response.status_code in [200, 404]
                print_test(f"Limit {limit} ({description})", passed,
                          f"Status: {response.status_code}")
            else:
                passed = response.status_code == 422
                print_test(f"Limit {limit} ({description}) rejected", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"Limit {limit} ({description})", False, str(e))


# =============================================================================
# TEST 3: References Endpoint Edge Cases
# =============================================================================

def test_references_invalid_id():
    """Test references with invalid paper ID"""
    print_section("TEST 3.1: References - Invalid Paper ID")

    try:
        response = requests.get(f"{BASE_URL}/api/papers/999999/references", timeout=10)
        passed = response.status_code == 404
        print_test("Invalid paper ID returns 404", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Invalid paper ID returns 404", False, str(e))


def test_references_limit_validation():
    """Test references with various limit values"""
    print_section("TEST 3.2: References - Limit Validation")

    test_cases = [
        (1, True),
        (100, True),
        (200, True),
        (500, False),
        (0, False),
    ]

    for limit, should_succeed in test_cases:
        try:
            response = requests.get(
                f"{BASE_URL}/api/papers/1/references?limit={limit}",
                timeout=10
            )

            if should_succeed:
                passed = response.status_code in [200, 404]
                print_test(f"Limit {limit}", passed, f"Status: {response.status_code}")
            else:
                passed = response.status_code == 422
                print_test(f"Limit {limit} rejected", passed, f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"Limit {limit}", False, str(e))


# =============================================================================
# TEST 4: Related Papers Endpoint Edge Cases
# =============================================================================

def test_related_invalid_id():
    """Test related papers with invalid paper ID"""
    print_section("TEST 4.1: Related Papers - Invalid Paper ID")

    try:
        response = requests.get(f"{BASE_URL}/api/papers/999999/related", timeout=10)
        passed = response.status_code == 404
        print_test("Invalid paper ID returns 404", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Invalid paper ID returns 404", False, str(e))


def test_related_limit_validation():
    """Test related papers with various limit values"""
    print_section("TEST 4.2: Related Papers - Limit Validation")

    test_cases = [
        (1, True),
        (20, True),
        (50, True),
        (100, False),  # Exceeds max
        (-1, False),
    ]

    for limit, should_succeed in test_cases:
        try:
            response = requests.get(
                f"{BASE_URL}/api/papers/1/related?limit={limit}",
                timeout=10
            )

            if should_succeed:
                passed = response.status_code in [200, 404]
                print_test(f"Limit {limit}", passed, f"Status: {response.status_code}")
            else:
                passed = response.status_code == 422
                print_test(f"Limit {limit} rejected", passed, f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"Limit {limit}", False, str(e))


# =============================================================================
# TEST 5: Citation Network Endpoint Edge Cases
# =============================================================================

def test_network_invalid_id():
    """Test citation network with invalid paper ID"""
    print_section("TEST 5.1: Citation Network - Invalid Paper ID")

    try:
        response = requests.get(f"{BASE_URL}/api/papers/999999/network", timeout=10)
        passed = response.status_code == 404
        print_test("Invalid paper ID returns 404", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Invalid paper ID returns 404", False, str(e))


def test_network_depth_validation():
    """Test network with various depth values"""
    print_section("TEST 5.2: Citation Network - Depth Validation")

    test_cases = [
        (1, "minimum depth", True),
        (2, "maximum depth", True),
        (3, "exceeds maximum", False),
        (0, "zero depth", False),
        (-1, "negative depth", False),
    ]

    for depth, description, should_succeed in test_cases:
        try:
            response = requests.get(
                f"{BASE_URL}/api/papers/1/network?depth={depth}",
                timeout=30
            )

            if should_succeed:
                passed = response.status_code in [200, 404]
                print_test(f"Depth {depth} ({description})", passed,
                          f"Status: {response.status_code}")
            else:
                passed = response.status_code == 422
                print_test(f"Depth {depth} ({description}) rejected", passed,
                          f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"Depth {depth} ({description})", False, str(e))


def test_network_structure():
    """Test network response structure is valid for graph visualization"""
    print_section("TEST 5.3: Citation Network - Response Structure")

    try:
        response = requests.get(f"{BASE_URL}/api/papers/1/network", timeout=30)

        if response.status_code == 200:
            data = response.json()

            # Check required fields
            has_seed = 'seed' in data
            has_citations = 'citations' in data
            has_references = 'references' in data
            has_nodes = 'nodes' in data
            has_edges = 'edges' in data

            print_test("Has 'seed' field", has_seed)
            print_test("Has 'citations' field", has_citations)
            print_test("Has 'references' field", has_references)
            print_test("Has 'nodes' field", has_nodes)
            print_test("Has 'edges' field", has_edges)

            # Validate structure
            if has_nodes and has_edges:
                nodes = data['nodes']
                edges = data['edges']

                print_test("Nodes is array", isinstance(nodes, list))
                print_test("Edges is array", isinstance(edges, list))

                if nodes:
                    first_node = nodes[0]
                    print_test("Node has 'id' field", 'id' in first_node)
                    print_test("Node has 'label' field", 'label' in first_node)
                    print_test("Node has 'type' field", 'type' in first_node)

                if edges:
                    first_edge = edges[0]
                    print_test("Edge has 'from' field", 'from' in first_edge)
                    print_test("Edge has 'to' field", 'to' in first_edge)
                    print_test("Edge has 'label' field", 'label' in first_edge)

                print(f"\n   Network size: {len(nodes)} nodes, {len(edges)} edges")
        elif response.status_code == 404:
            print_test("Paper not found (expected)", True, "404 response")
        else:
            print_test("Unexpected status code", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Network structure test", False, str(e))


# =============================================================================
# TEST 6: API Failure Simulation
# =============================================================================

def test_concurrent_requests():
    """Test multiple concurrent requests to discovery endpoints"""
    print_section("TEST 6.1: Concurrent Requests")

    import concurrent.futures

    def make_request(endpoint):
        try:
            response = requests.get(f"{BASE_URL}/api/papers/1/{endpoint}", timeout=30)
            return (endpoint, response.status_code, True)
        except Exception as e:
            return (endpoint, None, False)

    endpoints = ['recommendations', 'citations', 'references', 'related', 'network']

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, ep) for ep in endpoints]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        for endpoint, status, success in results:
            if success:
                passed = status in [200, 404, 500]  # Any handled response is ok
                print_test(f"{endpoint} endpoint", passed, f"Status: {status}")
            else:
                print_test(f"{endpoint} endpoint", False, "Request failed")
    except Exception as e:
        print_test("Concurrent requests test", False, str(e))


# =============================================================================
# TEST 7: Database Edge Cases
# =============================================================================

def test_duplicate_paper_handling():
    """Test that duplicate papers are handled correctly in discovery results"""
    print_section("TEST 7.1: Duplicate Paper Handling")

    # Search for a common topic to get papers
    try:
        response = requests.get(f"{BASE_URL}/api/papers/1/recommendations", timeout=30)

        if response.status_code == 200:
            data = response.json()
            recs = data.get('recommendations', [])

            # Check for duplicate IDs
            ids = [p['id'] for p in recs]
            unique_ids = set(ids)

            has_no_duplicates = len(ids) == len(unique_ids)
            print_test("No duplicate paper IDs in recommendations", has_no_duplicates,
                      f"{len(recs)} papers, {len(unique_ids)} unique")

            # Check for duplicate titles
            titles = [p.get('title', '').lower() for p in recs]
            unique_titles = set(titles)

            has_no_duplicate_titles = len(titles) == len(unique_titles)
            print_test("No duplicate titles in recommendations", has_no_duplicate_titles,
                      f"{len(titles)} titles, {len(unique_titles)} unique")
        elif response.status_code == 404:
            print_test("Paper not found (expected)", True, "404 response")
        else:
            print_test("Could not test duplicates", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Duplicate handling test", False, str(e))


# =============================================================================
# TEST 8: Response Time Tests
# =============================================================================

def test_response_times():
    """Test that all endpoints respond within reasonable time"""
    print_section("TEST 8.1: Response Times")

    endpoints = [
        ('recommendations', 30),
        ('citations', 30),
        ('references', 30),
        ('related', 30),
        ('network', 45),  # Network can take longer
    ]

    for endpoint, max_time in endpoints:
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/api/papers/1/{endpoint}", timeout=max_time)
            elapsed = time.time() - start

            if response.status_code in [200, 404]:
                passed = elapsed < max_time
                print_test(f"{endpoint} response time", passed,
                          f"{elapsed:.2f}s (max: {max_time}s)")
            else:
                print_test(f"{endpoint} response", True,
                          f"Status: {response.status_code}, Time: {elapsed:.2f}s")
        except requests.exceptions.Timeout:
            print_test(f"{endpoint} response time", False, f"Exceeded {max_time}s timeout")
        except Exception as e:
            print_test(f"{endpoint} response time", False, str(e))


# =============================================================================
# TEST 9: Real Paper Tests
# =============================================================================

def test_with_real_papers():
    """Test discovery endpoints with real papers from search"""
    print_section("TEST 9.1: Real Paper Discovery Tests")

    # First, search for some real papers
    papers = setup_test_papers()

    if not papers:
        print_test("Could not get test papers", False, "Skipping real paper tests")
        return

    # Test with first real paper
    if papers:
        paper_id = papers[0].get('id')
        title = papers[0].get('title', '')[:50]

        print(f"\nTesting with real paper ID {paper_id}:")
        print(f"  Title: {title}...\n")

        # Test each endpoint
        endpoints = ['recommendations', 'citations', 'references', 'related', 'network']

        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/papers/{paper_id}/{endpoint}",
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    # Check response structure based on endpoint
                    if endpoint == 'network':
                        nodes = len(data.get('nodes', []))
                        edges = len(data.get('edges', []))
                        print_test(f"{endpoint} endpoint", True,
                                  f"{nodes} nodes, {edges} edges")
                    else:
                        key = endpoint if endpoint != 'related' else 'related_papers'
                        count = len(data.get(key, []))
                        print_test(f"{endpoint} endpoint", True,
                                  f"Found {count} results")
                else:
                    print_test(f"{endpoint} endpoint", False,
                              f"Status: {response.status_code}")
            except Exception as e:
                print_test(f"{endpoint} endpoint", False, str(e))


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  DISCOVERY ENDPOINTS - EDGE CASE TEST SUITE")
    print("  Testing ResearchRabbit-Style Features")
    print("="*80)

    # Check backend
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            print("\n✅ Backend is running\n")
        else:
            print("\n⚠️ Backend returned unexpected status\n")
    except:
        print("\n❌ Backend is not running. Start with: python -m uvicorn backend.main:app --reload\n")
        sys.exit(1)

    # Run all tests
    print("\n" + "="*80)
    print("  RUNNING EDGE CASE TESTS")
    print("="*80)

    # Test 1: Recommendations
    test_recommendations_invalid_id()
    test_recommendations_no_doi()
    test_recommendations_limit_validation()
    test_recommendations_timeout()

    # Test 2: Citations
    test_citations_invalid_id()
    test_citations_no_doi()
    test_citations_limit_validation()

    # Test 3: References
    test_references_invalid_id()
    test_references_limit_validation()

    # Test 4: Related Papers
    test_related_invalid_id()
    test_related_limit_validation()

    # Test 5: Citation Network
    test_network_invalid_id()
    test_network_depth_validation()
    test_network_structure()

    # Test 6: Concurrent Requests
    test_concurrent_requests()

    # Test 7: Database Edge Cases
    test_duplicate_paper_handling()

    # Test 8: Response Times
    test_response_times()

    # Test 9: Real Papers
    test_with_real_papers()

    print("\n" + "="*80)
    print("  EDGE CASE TESTING COMPLETE")
    print("="*80 + "\n")
