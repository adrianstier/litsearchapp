#!/usr/bin/env python3
"""
Dedicated Google Scholar search test
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

def test_google_scholar_basic():
    """Test 1: Basic Google Scholar search"""
    print_section("TEST 1: Basic Google Scholar Search")

    payload = {
        "query": "machine learning",
        "sources": ["scholar"],
        "max_results": 5
    }

    try:
        print("Sending request...")
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=60)
        search_time = time.time() - start_time

        print(f"Response Status: {response.status_code}")
        print(f"Search Time: {search_time:.2f}s")

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print(f"\n✅ Google Scholar Search Successful")
            print(f"   Total Results: {data.get('total_results', 0)}")
            print(f"   Papers Retrieved: {len(papers)}")
            print(f"   Search Time: {search_time:.2f}s")

            if papers:
                print("\n" + "-"*80)
                for i, paper in enumerate(papers, 1):
                    print(f"\nPaper {i}:")
                    print(f"  Title: {paper.get('title', 'N/A')}")
                    print(f"  Authors: {', '.join([a if isinstance(a, str) else a.get('name', 'Unknown') for a in paper.get('authors', [])])}")
                    print(f"  Year: {paper.get('year', 'N/A')}")
                    print(f"  Citations: {paper.get('citations', 'N/A')}")
                    print(f"  Source: {paper.get('source', 'N/A')}")
                    if paper.get('url'):
                        print(f"  URL: {paper.get('url')}")
                    if paper.get('pdf_url'):
                        print(f"  PDF: {paper.get('pdf_url')}")
                    if paper.get('abstract'):
                        abstract = paper.get('abstract', '')
                        print(f"  Abstract: {abstract[:200]}...")
                print("-"*80)
            else:
                print("\n⚠ No papers returned")
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_google_scholar_with_year():
    """Test 2: Google Scholar with year filter"""
    print_section("TEST 2: Google Scholar with Year Filter (2020-2023)")

    payload = {
        "query": "deep learning",
        "sources": ["scholar"],
        "year_start": 2020,
        "year_end": 2023,
        "max_results": 5
    }

    try:
        print("Sending request with year filter...")
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=60)
        search_time = time.time() - start_time

        print(f"Response Status: {response.status_code}")
        print(f"Search Time: {search_time:.2f}s")

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print(f"\n✅ Google Scholar Year Filter Search Successful")
            print(f"   Papers Retrieved: {len(papers)}")

            years = [p.get('year') for p in papers if p.get('year')]
            if years:
                print(f"\n   Years found: {sorted(years)}")
                years_valid = all(2020 <= y <= 2023 for y in years if isinstance(y, int))
                if years_valid:
                    print(f"   ✓ All papers within requested range (2020-2023)")
                else:
                    print(f"   ⚠ Some papers outside requested range")
                    for paper in papers:
                        year = paper.get('year')
                        if year and (year < 2020 or year > 2023):
                            print(f"      - {paper.get('title', 'Unknown')[:60]}... ({year})")
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def test_google_scholar_complex_query():
    """Test 3: Complex scholarly query"""
    print_section("TEST 3: Complex Query - Multiple Keywords")

    payload = {
        "query": "natural language processing transformers BERT",
        "sources": ["scholar"],
        "max_results": 5
    }

    try:
        print("Sending complex query...")
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=60)
        search_time = time.time() - start_time

        print(f"Response Status: {response.status_code}")
        print(f"Search Time: {search_time:.2f}s")

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print(f"\n✅ Complex Query Successful")
            print(f"   Papers Retrieved: {len(papers)}")

            if papers:
                print("\n   Top Results:")
                for i, paper in enumerate(papers[:3], 1):
                    print(f"\n   {i}. {paper.get('title', 'N/A')}")
                    print(f"      Year: {paper.get('year', 'N/A')}, Citations: {paper.get('citations', 'N/A')}")
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def test_google_scholar_ucsb_access():
    """Test 4: Check UCSB authentication status"""
    print_section("TEST 4: UCSB Authentication Status")

    try:
        response = requests.get(f"{BASE_URL}/api/auth/status", timeout=10)

        if response.status_code == 200:
            data = response.json()
            authenticated = data.get('authenticated', False)

            print(f"UCSB Authentication Status: {'✅ Enabled' if authenticated else '❌ Not Configured'}")

            if authenticated:
                print("\n✅ Google Scholar will use UCSB proxy for enhanced access")
                print("   This should provide access to paywalled content")
            else:
                print("\n⚠ Google Scholar will use public access only")
                print("   Some papers may not be fully accessible")
        else:
            print(f"❌ Could not check auth status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking auth: {str(e)}")

def test_google_scholar_comparison():
    """Test 5: Compare Google Scholar with other sources"""
    print_section("TEST 5: Google Scholar vs Other Sources Comparison")

    query = "climate change"

    sources_to_test = [
        ("scholar", "Google Scholar"),
        ("pubmed", "PubMed"),
        ("arxiv", "arXiv")
    ]

    results = {}

    for source_key, source_name in sources_to_test:
        payload = {
            "query": query,
            "sources": [source_key],
            "max_results": 5
        }

        try:
            print(f"\nTesting {source_name}...")
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=60)
            search_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                papers = data.get('papers', [])
                results[source_name] = {
                    'count': len(papers),
                    'time': search_time,
                    'success': True
                }
                print(f"  ✅ {len(papers)} papers in {search_time:.2f}s")
            else:
                results[source_name] = {
                    'count': 0,
                    'time': search_time,
                    'success': False,
                    'error': response.status_code
                }
                print(f"  ❌ Failed: {response.status_code}")
        except Exception as e:
            results[source_name] = {
                'count': 0,
                'time': 0,
                'success': False,
                'error': str(e)
            }
            print(f"  ❌ Error: {str(e)}")

    print("\n" + "-"*80)
    print("COMPARISON SUMMARY:")
    print("-"*80)
    print(f"{'Source':<20} {'Papers':<10} {'Time':<10} {'Status'}")
    print("-"*80)
    for source_name in [s[1] for s in sources_to_test]:
        if source_name in results:
            r = results[source_name]
            status = "✅ OK" if r['success'] else f"❌ {r.get('error', 'Failed')}"
            print(f"{source_name:<20} {r['count']:<10} {r['time']:<10.2f} {status}")
    print("-"*80)

def main():
    """Run all Google Scholar tests"""
    print("\n" + "="*80)
    print("  GOOGLE SCHOLAR SEARCH TESTS")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)

    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        if response.status_code != 200:
            print("\n❌ Backend is not responding correctly")
            return
    except Exception as e:
        print(f"\n❌ Cannot connect to backend at {BASE_URL}")
        print(f"   Error: {e}")
        return

    print("\n✅ Backend is running")

    # Run tests
    test_google_scholar_ucsb_access()
    test_google_scholar_basic()
    test_google_scholar_with_year()
    test_google_scholar_complex_query()
    test_google_scholar_comparison()

    print("\n" + "="*80)
    print("  GOOGLE SCHOLAR TESTS COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
