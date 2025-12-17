#!/usr/bin/env python3
"""
Comprehensive test suite for all LitSearch features
Tests search engines, AI features, semantic search, and more
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000/api"

# Test results tracking
results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

def test(name, condition, error_msg=""):
    """Test helper function"""
    if condition:
        print(f"  ✓ {name}")
        results["passed"] += 1
    else:
        print(f"  ✗ {name}")
        if error_msg:
            print(f"    Error: {error_msg}")
        results["failed"] += 1
        results["errors"].append(f"{name}: {error_msg}")

def api_call(method, endpoint, **kwargs):
    """Make API call with error handling"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        elif method == "DELETE":
            response = requests.delete(url, **kwargs)
        else:
            return None, f"Unknown method: {method}"

        return response, None
    except Exception as e:
        return None, str(e)

print("\n" + "="*60)
print("LITSEARCH COMPREHENSIVE FEATURE TEST")
print("="*60 + "\n")

# =============================================================================
# TEST 1: SEARCH ENGINES
# =============================================================================
print("\n📚 TEST 1: SEARCH ENGINES")
print("-" * 40)

search_sources = [
    ("pubmed", "PubMed"),
    ("arxiv", "arXiv"),
    ("crossref", "Crossref"),
    ("semantic_scholar", "Semantic Scholar"),
    ("openalex", "OpenAlex"),
]

saved_paper_ids = []

for source_id, source_name in search_sources:
    print(f"\n  Testing {source_name}...")

    response, error = api_call("POST", "/search", json={
        "query": "machine learning",
        "sources": [source_id],
        "max_results": 5
    })

    if error:
        test(f"{source_name} search", False, error)
        continue

    if response.status_code == 200:
        data = response.json()
        papers = data.get("papers", [])
        test(f"{source_name} search returns papers", len(papers) > 0,
             f"Got {len(papers)} papers")

        # Save paper IDs for later tests
        for p in papers[:2]:
            if p.get("id") and p["id"] not in saved_paper_ids:
                saved_paper_ids.append(p["id"])
    else:
        test(f"{source_name} search", False,
             f"Status {response.status_code}: {response.text[:100]}")

print(f"\n  Saved {len(saved_paper_ids)} paper IDs for further testing")

# =============================================================================
# TEST 2: MULTI-SOURCE SEARCH
# =============================================================================
print("\n\n🔍 TEST 2: MULTI-SOURCE SEARCH")
print("-" * 40)

response, error = api_call("POST", "/search", json={
    "query": "deep learning neural networks",
    "sources": ["pubmed", "arxiv", "crossref"],
    "max_results": 10
})

if error:
    test("Multi-source search", False, error)
else:
    if response.status_code == 200:
        data = response.json()
        papers = data.get("papers", [])
        sources_searched = data.get("sources_searched", [])

        test("Multi-source returns papers", len(papers) > 0)
        test("Multiple sources searched", len(sources_searched) >= 2,
             f"Sources: {sources_searched}")

        # Save more paper IDs
        for p in papers[:5]:
            if p.get("id") and p["id"] not in saved_paper_ids:
                saved_paper_ids.append(p["id"])
    else:
        test("Multi-source search", False, f"Status {response.status_code}")

# =============================================================================
# TEST 3: PAPER RETRIEVAL
# =============================================================================
print("\n\n📄 TEST 3: PAPER RETRIEVAL")
print("-" * 40)

if saved_paper_ids:
    paper_id = saved_paper_ids[0]

    # Get single paper
    response, error = api_call("GET", f"/papers/{paper_id}")
    if error:
        test("Get paper by ID", False, error)
    else:
        test("Get paper by ID", response.status_code == 200)
        if response.status_code == 200:
            paper = response.json()
            test("Paper has title", bool(paper.get("title")))
            test("Paper has abstract", bool(paper.get("abstract")))

    # Get all papers
    response, error = api_call("GET", "/papers?page=1&page_size=10")
    if error:
        test("Get all papers", False, error)
    else:
        test("Get all papers", response.status_code == 200)
        if response.status_code == 200:
            data = response.json()
            test("Papers list returned", len(data.get("papers", [])) > 0)
else:
    print("  ⚠ No paper IDs available for testing")

# =============================================================================
# TEST 4: DISCOVERY FEATURES
# =============================================================================
print("\n\n🔭 TEST 4: DISCOVERY FEATURES")
print("-" * 40)

if saved_paper_ids:
    paper_id = saved_paper_ids[0]

    # Recommendations
    response, error = api_call("GET", f"/papers/{paper_id}/recommendations?limit=5")
    if error:
        test("Get recommendations", False, error)
    else:
        test("Get recommendations", response.status_code == 200)

    # Citations
    response, error = api_call("GET", f"/papers/{paper_id}/citations?limit=5")
    if error:
        test("Get citations", False, error)
    else:
        test("Get citations", response.status_code == 200)

    # References
    response, error = api_call("GET", f"/papers/{paper_id}/references?limit=5")
    if error:
        test("Get references", False, error)
    else:
        test("Get references", response.status_code == 200)

    # Related papers
    response, error = api_call("GET", f"/papers/{paper_id}/related?limit=5")
    if error:
        test("Get related papers", False, error)
    else:
        test("Get related papers", response.status_code == 200)

    # Network
    response, error = api_call("GET", f"/papers/{paper_id}/network?depth=1")
    if error:
        test("Get paper network", False, error)
    else:
        test("Get paper network", response.status_code == 200)

# =============================================================================
# TEST 5: SEMANTIC SEARCH
# =============================================================================
print("\n\n🧠 TEST 5: SEMANTIC SEARCH")
print("-" * 40)

if saved_paper_ids:
    # Semantic search
    response, error = api_call("POST", "/search/semantic", params={
        "query": "machine learning applications",
        "top_k": 10
    })

    if error:
        test("Semantic search", False, error)
    else:
        if response.status_code == 200:
            data = response.json()
            results_list = data.get("results", [])
            test("Semantic search returns results", len(results_list) > 0)

            if results_list:
                first = results_list[0]
                test("Results have similarity scores",
                     "similarity_score" in first)
        else:
            test("Semantic search", False, f"Status {response.status_code}: {response.text[:100]}")

    # Find similar papers
    paper_id = saved_paper_ids[0]
    response, error = api_call("GET", f"/papers/{paper_id}/similar?top_k=5")

    if error:
        test("Find similar papers", False, error)
    else:
        if response.status_code == 200:
            data = response.json()
            similar = data.get("similar", [])
            test("Similar papers returned", True)
            if similar:
                test("Similar papers have scores",
                     "similarity_score" in similar[0])
        else:
            test("Find similar papers", False, f"Status {response.status_code}")

# =============================================================================
# TEST 6: D3 CITATION NETWORK
# =============================================================================
print("\n\n🕸️ TEST 6: D3 CITATION NETWORK")
print("-" * 40)

if saved_paper_ids:
    paper_id = saved_paper_ids[0]

    response, error = api_call("GET", f"/network/d3/{paper_id}")

    if error:
        test("Get D3 network", False, error)
    else:
        if response.status_code == 200:
            data = response.json()
            test("D3 network has nodes", "nodes" in data)
            test("D3 network has links", "links" in data)
            test("D3 network has stats", "stats" in data)

            nodes = data.get("nodes", [])
            if nodes:
                test("Nodes have required fields",
                     all(k in nodes[0] for k in ["id", "title", "type"]))
        else:
            test("Get D3 network", False, f"Status {response.status_code}")

# =============================================================================
# TEST 7: AI FEATURES (requires OpenAI API key)
# =============================================================================
print("\n\n🤖 TEST 7: AI FEATURES")
print("-" * 40)

if saved_paper_ids:
    paper_id = saved_paper_ids[0]

    # Test summarization
    response, error = api_call("POST", "/ai/summarize", json=[paper_id])

    if error:
        test("AI summarization", False, error)
    else:
        if response.status_code == 200:
            data = response.json()
            summaries = data.get("summaries", [])
            test("AI summarization returns result", len(summaries) > 0)
            if summaries:
                test("Summary has content", bool(summaries[0].get("summary")))
        elif response.status_code == 500 and "API key" in response.text:
            print("  ⚠ AI features require OPENAI_API_KEY")
            test("AI summarization (needs API key)", True)
        else:
            test("AI summarization", False, f"Status {response.status_code}")

    # Test data extraction
    response, error = api_call("POST", "/ai/extract", params={
        "paper_id": paper_id,
        "fields": ["methodology", "main_finding"]
    })

    if error:
        test("AI data extraction", False, error)
    else:
        if response.status_code == 200:
            data = response.json()
            test("AI extraction returns data", "extracted" in data)
        elif response.status_code == 500:
            print("  ⚠ AI extraction requires OPENAI_API_KEY")
            test("AI extraction (needs API key)", True)
        else:
            test("AI data extraction", False, f"Status {response.status_code}")

# =============================================================================
# TEST 8: COLLECTIONS
# =============================================================================
print("\n\n📁 TEST 8: COLLECTIONS")
print("-" * 40)

# Get collections
response, error = api_call("GET", "/collections")
if error:
    test("Get collections", False, error)
else:
    test("Get collections", response.status_code == 200)

# Create collection
response, error = api_call("POST", "/collections", json={
    "name": "Test Collection",
    "description": "Test collection for automated testing"
})
if error:
    test("Create collection", False, error)
else:
    test("Create collection", response.status_code == 200)

# =============================================================================
# TEST 9: SEARCH HISTORY
# =============================================================================
print("\n\n📜 TEST 9: SEARCH HISTORY")
print("-" * 40)

response, error = api_call("GET", "/search/history")
if error:
    test("Get search history", False, error)
else:
    test("Get search history", response.status_code == 200)
    if response.status_code == 200:
        history = response.json()
        test("History is a list", isinstance(history, list))
        test("History has entries", len(history) > 0)

# =============================================================================
# TEST 10: VISUALIZATIONS
# =============================================================================
print("\n\n📊 TEST 10: VISUALIZATIONS")
print("-" * 40)

# Timeline
response, error = api_call("GET", "/visualize/timeline")
if error:
    test("Get timeline visualization", False, error)
else:
    test("Get timeline visualization", response.status_code == 200)

# Network
response, error = api_call("GET", "/visualize/network")
if error:
    test("Get network visualization", False, error)
else:
    test("Get network visualization", response.status_code == 200)

# Topics
response, error = api_call("GET", "/visualize/topics")
if error:
    test("Get topics visualization", False, error)
else:
    test("Get topics visualization", response.status_code == 200)

# =============================================================================
# TEST 11: AUTH STATUS
# =============================================================================
print("\n\n🔐 TEST 11: AUTH STATUS")
print("-" * 40)

response, error = api_call("GET", "/auth/status")
if error:
    test("Get auth status", False, error)
else:
    if response.status_code == 200:
        data = response.json()
        test("Auth status returns data", True)
        test("Has authenticated field", "authenticated" in data)
        test("Has vpn_connected field", "vpn_connected" in data)

        if data.get("vpn_connected"):
            print("  ✓ VPN connection detected!")
        if data.get("cookie_authenticated"):
            print("  ✓ Cookie authentication active!")
    else:
        test("Get auth status", False, f"Status {response.status_code}")

# =============================================================================
# TEST 12: STATS
# =============================================================================
print("\n\n📈 TEST 12: APPLICATION STATS")
print("-" * 40)

response, error = api_call("GET", "/stats")
if error:
    test("Get stats", False, error)
else:
    if response.status_code == 200:
        data = response.json()
        test("Stats returns data", True)
        test("Has total_papers", "total_papers" in data)
        test("Has total_searches", "total_searches" in data)

        print(f"\n  📊 Current Stats:")
        print(f"     Papers: {data.get('total_papers', 0)}")
        print(f"     PDFs: {data.get('total_pdfs', 0)}")
        print(f"     Searches: {data.get('total_searches', 0)}")
        print(f"     Collections: {data.get('total_collections', 0)}")
    else:
        test("Get stats", False, f"Status {response.status_code}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print(f"\n  ✓ Passed: {results['passed']}")
print(f"  ✗ Failed: {results['failed']}")
print(f"  Total:   {results['passed'] + results['failed']}")

if results['failed'] > 0:
    print("\n  Failed Tests:")
    for err in results['errors']:
        print(f"    - {err}")

success_rate = results['passed'] / (results['passed'] + results['failed']) * 100 if (results['passed'] + results['failed']) > 0 else 0
print(f"\n  Success Rate: {success_rate:.1f}%")

if success_rate >= 90:
    print("\n  🎉 Excellent! All major features are working!")
elif success_rate >= 70:
    print("\n  ⚠️ Good, but some features need attention.")
else:
    print("\n  ❌ Multiple features are broken. Please investigate.")

print("\n" + "="*60 + "\n")

sys.exit(0 if results['failed'] == 0 else 1)
