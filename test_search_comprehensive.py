#!/usr/bin/env python3
"""
Comprehensive test script for backend search functionality
Tests all different search options and configurations
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_result(test_name, result_data, error=None):
    """Print test results in a formatted way"""
    if error:
        print(f"❌ {test_name}")
        print(f"   Error: {error}")
    else:
        print(f"✅ {test_name}")
        if isinstance(result_data, dict):
            if 'total_results' in result_data:
                print(f"   Total Results: {result_data['total_results']}")
            if 'sources' in result_data:
                for source, count in result_data['sources'].items():
                    print(f"   - {source}: {count} papers")
            if 'search_time' in result_data:
                print(f"   Search Time: {result_data['search_time']:.2f}s")

def test_basic_search():
    """Test 1: Basic search with single source"""
    print_section("TEST 1: Basic Search (PubMed only)")

    payload = {
        "query": "machine learning",
        "sources": ["pubmed"],
        "max_results": 5
    }

    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)
        search_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print_result("Basic PubMed Search", {
                'total_results': data.get('total_results', 0),
                'sources': {'PubMed': len(data.get('papers', []))},
                'search_time': search_time
            })

            if data.get('papers'):
                print("\n   Sample Paper:")
                paper = data['papers'][0]
                print(f"   Title: {paper.get('title', 'N/A')[:80]}...")
                print(f"   Authors: {', '.join(paper.get('authors', [])[:3])}")
                print(f"   Year: {paper.get('year', 'N/A')}")
        else:
            print_result("Basic PubMed Search", None, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_result("Basic PubMed Search", None, str(e))

def test_multi_source_search():
    """Test 2: Search across multiple sources"""
    print_section("TEST 2: Multi-Source Search (PubMed + arXiv + Crossref)")

    payload = {
        "query": "neural networks",
        "sources": ["pubmed", "arxiv", "crossref"],
        "max_results": 10
    }

    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=60)
        search_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()

            # Count papers by source
            source_counts = {}
            for paper in data.get('papers', []):
                source = paper.get('source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1

            print_result("Multi-Source Search", {
                'total_results': data.get('total_results', 0),
                'sources': source_counts,
                'search_time': search_time
            })
        else:
            print_result("Multi-Source Search", None, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_result("Multi-Source Search", None, str(e))

def test_year_filter():
    """Test 3: Search with year range filter"""
    print_section("TEST 3: Year Range Filter (2020-2023)")

    payload = {
        "query": "COVID-19",
        "sources": ["pubmed"],
        "year_start": 2020,
        "year_end": 2023,
        "max_results": 10
    }

    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)
        search_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            # Check year range
            years = [p.get('year') for p in papers if p.get('year')]
            years_valid = all(2020 <= y <= 2023 for y in years if y)

            print_result("Year Range Filter", {
                'total_results': data.get('total_results', 0),
                'sources': {'PubMed': len(papers)},
                'search_time': search_time
            })

            if years:
                print(f"   Year Range: {min(years)}-{max(years)}")
                print(f"   ✓ All papers within range" if years_valid else "   ⚠ Some papers outside range")
        else:
            print_result("Year Range Filter", None, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_result("Year Range Filter", None, str(e))

def test_arxiv_search():
    """Test 4: arXiv-specific search"""
    print_section("TEST 4: arXiv Search")

    payload = {
        "query": "quantum computing",
        "sources": ["arxiv"],
        "max_results": 5
    }

    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)
        search_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print_result("arXiv Search", {
                'total_results': data.get('total_results', 0),
                'sources': {'arXiv': len(papers)},
                'search_time': search_time
            })

            if papers:
                print("\n   Sample arXiv Paper:")
                paper = papers[0]
                print(f"   Title: {paper.get('title', 'N/A')[:80]}...")
                print(f"   ArXiv ID: {paper.get('arxiv_id', 'N/A')}")
                if paper.get('pdf_url'):
                    print(f"   PDF URL: {paper.get('pdf_url')}")
        else:
            print_result("arXiv Search", None, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_result("arXiv Search", None, str(e))

def test_crossref_search():
    """Test 5: Crossref search"""
    print_section("TEST 5: Crossref Search")

    payload = {
        "query": "climate change",
        "sources": ["crossref"],
        "max_results": 5
    }

    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)
        search_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print_result("Crossref Search", {
                'total_results': data.get('total_results', 0),
                'sources': {'Crossref': len(papers)},
                'search_time': search_time
            })

            if papers:
                print("\n   Sample Crossref Paper:")
                paper = papers[0]
                print(f"   Title: {paper.get('title', 'N/A')[:80]}...")
                print(f"   DOI: {paper.get('doi', 'N/A')}")
                print(f"   Journal: {paper.get('journal', 'N/A')}")
        else:
            print_result("Crossref Search", None, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_result("Crossref Search", None, str(e))

def test_all_sources_search():
    """Test 6: Search all available sources"""
    print_section("TEST 6: All Sources Search")

    payload = {
        "query": "artificial intelligence",
        "sources": ["pubmed", "arxiv", "crossref", "scholar", "wos"],
        "max_results": 20
    }

    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=120)
        search_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            # Count by source
            source_counts = {}
            for paper in papers:
                source = paper.get('source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1

            print_result("All Sources Search", {
                'total_results': data.get('total_results', 0),
                'sources': source_counts,
                'search_time': search_time
            })

            # Check for duplicates
            titles = [p.get('title', '').lower() for p in papers]
            unique_titles = len(set(titles))
            print(f"\n   Total Papers: {len(papers)}")
            print(f"   Unique Titles: {unique_titles}")
            if unique_titles < len(papers):
                print(f"   ⚠ {len(papers) - unique_titles} potential duplicates detected")
        else:
            print_result("All Sources Search", None, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_result("All Sources Search", None, str(e))

def test_max_results_limit():
    """Test 7: Max results limiting"""
    print_section("TEST 7: Max Results Limit (2 papers)")

    payload = {
        "query": "biology",
        "sources": ["pubmed"],
        "max_results": 2
    }

    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)
        search_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print_result("Max Results Limit", {
                'total_results': data.get('total_results', 0),
                'sources': {'PubMed': len(papers)},
                'search_time': search_time
            })

            if len(papers) <= 2:
                print(f"   ✓ Correctly limited to {len(papers)} papers")
            else:
                print(f"   ⚠ Expected max 2 papers, got {len(papers)}")
        else:
            print_result("Max Results Limit", None, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_result("Max Results Limit", None, str(e))

def test_complex_query():
    """Test 8: Complex query with special characters"""
    print_section("TEST 8: Complex Query")

    payload = {
        "query": "CRISPR-Cas9 gene editing",
        "sources": ["pubmed", "arxiv"],
        "year_start": 2015,
        "max_results": 10
    }

    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=60)
        search_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            source_counts = {}
            for paper in papers:
                source = paper.get('source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1

            print_result("Complex Query", {
                'total_results': data.get('total_results', 0),
                'sources': source_counts,
                'search_time': search_time
            })
        else:
            print_result("Complex Query", None, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        print_result("Complex Query", None, str(e))

def test_empty_query():
    """Test 9: Empty query handling"""
    print_section("TEST 9: Empty Query Error Handling")

    payload = {
        "query": "",
        "sources": ["pubmed"],
        "max_results": 5
    }

    try:
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)

        if response.status_code == 422:  # Validation error expected
            print("✅ Empty Query Handling")
            print("   Correctly rejected empty query with 422 status")
        elif response.status_code == 200:
            print("⚠ Empty Query Handling")
            print("   Warning: Empty query was accepted (should validate)")
        else:
            print_result("Empty Query Handling", None, f"Unexpected status {response.status_code}")
    except Exception as e:
        print_result("Empty Query Handling", None, str(e))

def test_invalid_source():
    """Test 10: Invalid source handling"""
    print_section("TEST 10: Invalid Source Error Handling")

    payload = {
        "query": "test",
        "sources": ["invalid_source"],
        "max_results": 5
    }

    try:
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)

        if response.status_code in [400, 422]:  # Validation error expected
            print("✅ Invalid Source Handling")
            print(f"   Correctly rejected invalid source with {response.status_code} status")
        else:
            print_result("Invalid Source Handling", None, f"Unexpected status {response.status_code}")
    except Exception as e:
        print_result("Invalid Source Handling", None, str(e))

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  COMPREHENSIVE BACKEND SEARCH TESTS")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)

    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        if response.status_code != 200:
            print("\n❌ Backend is not responding correctly")
            print(f"   Status: {response.status_code}")
            return
    except Exception as e:
        print(f"\n❌ Cannot connect to backend at {BASE_URL}")
        print(f"   Error: {e}")
        print("\n   Please ensure the backend is running:")
        print("   cd /Users/adrianstiermbp2023/litsearchapp")
        print("   python -m uvicorn backend.main:app --reload --port 8000")
        return

    print("\n✅ Backend is running\n")

    # Run all tests
    test_basic_search()
    test_multi_source_search()
    test_year_filter()
    test_arxiv_search()
    test_crossref_search()
    test_all_sources_search()
    test_max_results_limit()
    test_complex_query()
    test_empty_query()
    test_invalid_source()

    print("\n" + "="*80)
    print("  TESTS COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
