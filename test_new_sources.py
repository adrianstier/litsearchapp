"""Test Semantic Scholar and OpenAlex integrations"""

import sys
import requests
import time

BASE_URL = "http://127.0.0.1:8000"


def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_semantic_scholar():
    """Test Semantic Scholar search"""
    print_section("TEST 1: Semantic Scholar Search")

    payload = {
        "query": "machine learning",
        "sources": ["semantic_scholar"],
        "max_results": 5
    }

    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)
        elapsed = time.time() - start

        print(f"Status: {response.status_code}")
        print(f"Time: {elapsed:.2f}s\n")

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print(f"✅ Found {len(papers)} papers\n")

            if papers:
                print("Sample paper:")
                paper = papers[0]
                print(f"  Title: {paper.get('title', 'N/A')}")
                print(f"  Authors: {', '.join([a['name'] for a in paper.get('authors', [])[:3]])}")
                print(f"  Year: {paper.get('year', 'N/A')}")
                print(f"  Citations: {paper.get('citations', 0)}")
                print(f"  DOI: {paper.get('doi', 'N/A')}")
                print(f"  PDF URL: {paper.get('pdf_url', 'N/A')}")

                # Check for AI features
                if paper.get('abstract') and '[AI Summary]' in paper.get('abstract', ''):
                    print(f"  ✨ Has AI-generated summary!")
                if paper.get('keywords'):
                    print(f"  Keywords: {', '.join(paper['keywords'][:5])}")

        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"✗ Test failed: {e}")


def test_openalex():
    """Test OpenAlex search"""
    print_section("TEST 2: OpenAlex Search")

    payload = {
        "query": "artificial intelligence",
        "sources": ["openalex"],
        "max_results": 5
    }

    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)
        elapsed = time.time() - start

        print(f"Status: {response.status_code}")
        print(f"Time: {elapsed:.2f}s\n")

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print(f"✅ Found {len(papers)} papers\n")

            if papers:
                print("Sample paper:")
                paper = papers[0]
                print(f"  Title: {paper.get('title', 'N/A')}")
                print(f"  Authors: {', '.join([a['name'] for a in paper.get('authors', [])[:3]])}")
                print(f"  Year: {paper.get('year', 'N/A')}")
                print(f"  Citations: {paper.get('citations', 0)}")
                print(f"  DOI: {paper.get('doi', 'N/A')}")
                print(f"  Journal: {paper.get('journal', 'N/A')}")
                print(f"  PDF URL: {paper.get('pdf_url', 'N/A')}")

                if paper.get('keywords'):
                    print(f"  Topics: {', '.join(paper['keywords'][:5])}")

        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"✗ Test failed: {e}")


def test_combined_search():
    """Test search combining new sources with existing ones"""
    print_section("TEST 3: Combined Multi-Source Search")

    payload = {
        "query": "neural networks",
        "sources": ["pubmed", "arxiv", "semantic_scholar", "openalex"],
        "max_results": 10
    }

    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=60)
        elapsed = time.time() - start

        print(f"Status: {response.status_code}")
        print(f"Time: {elapsed:.2f}s\n")

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])
            stats = data.get('total_found', len(papers))

            print(f"✅ Found {len(papers)} papers (total before dedup: {stats})")
            print(f"   Search time: {elapsed:.2f}s\n")

            # Count by source
            source_counts = {}
            for paper in papers:
                for source in paper.get('sources', []):
                    source_counts[source] = source_counts.get(source, 0) + 1

            print("Papers by source:")
            for source, count in sorted(source_counts.items()):
                print(f"  {source}: {count} papers")

            # Show sample from new sources
            print("\nSample papers from new sources:")
            for paper in papers[:5]:
                sources = paper.get('sources', [])
                if 'semantic_scholar' in sources or 'openalex' in sources:
                    print(f"  • {paper.get('title', 'N/A')[:80]}...")
                    print(f"    Sources: {', '.join(sources)}")

        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"✗ Test failed: {e}")


def test_year_filtering():
    """Test year filtering with new sources"""
    print_section("TEST 4: Year Filtering (2020-2023)")

    payload = {
        "query": "COVID-19",
        "sources": ["semantic_scholar", "openalex"],
        "year_start": 2020,
        "year_end": 2023,
        "max_results": 10
    }

    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=30)
        elapsed = time.time() - start

        print(f"Status: {response.status_code}")
        print(f"Time: {elapsed:.2f}s\n")

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print(f"✅ Found {len(papers)} papers\n")

            years = [p.get('year') for p in papers if p.get('year')]
            if years:
                print(f"Year range: {min(years)} - {max(years)}")
                all_in_range = all(2020 <= y <= 2023 for y in years)
                print(f"All papers in 2020-2023 range: {'✅' if all_in_range else '✗'}")

                # Show year distribution
                year_counts = {}
                for y in years:
                    year_counts[y] = year_counts.get(y, 0) + 1
                print("\nPapers by year:")
                for year in sorted(year_counts.keys()):
                    print(f"  {year}: {year_counts[year]} papers")

        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"✗ Test failed: {e}")


def test_all_sources():
    """Test search with ALL available sources"""
    print_section("TEST 5: ALL Sources (Including New Ones)")

    payload = {
        "query": "climate change",
        "sources": ["pubmed", "arxiv", "crossref", "semantic_scholar", "openalex"],
        "max_results": 20
    }

    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/search", json=payload, timeout=90)
        elapsed = time.time() - start

        print(f"Status: {response.status_code}")
        print(f"Time: {elapsed:.2f}s\n")

        if response.status_code == 200:
            data = response.json()
            papers = data.get('papers', [])

            print(f"✅ Found {len(papers)} papers")
            print(f"   Search time: {elapsed:.2f}s\n")

            # Detailed source breakdown
            source_counts = {}
            for paper in papers:
                for source in paper.get('sources', []):
                    source_counts[source] = source_counts.get(source, 0) + 1

            print("Results by source:")
            print("-" * 40)
            for source in ['pubmed', 'arxiv', 'crossref', 'semantic_scholar', 'openalex']:
                count = source_counts.get(source, 0)
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {source:20} {count:3} papers")

        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"✗ Test failed: {e}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("  NEW SOURCES TEST SUITE")
    print("  Testing Semantic Scholar + OpenAlex Integration")
    print("="*80)

    # Check backend
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            print("\n✅ Backend is running\n")
        else:
            print("\n⚠️ Backend returned unexpected status\n")
    except:
        print("\n✗ Backend is not running. Start with: python -m uvicorn backend.main:app --reload\n")
        sys.exit(1)

    # Run tests
    test_semantic_scholar()
    test_openalex()
    test_combined_search()
    test_year_filtering()
    test_all_sources()

    print("\n" + "="*80)
    print("  TESTS COMPLETE")
    print("="*80 + "\n")
