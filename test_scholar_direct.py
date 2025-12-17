"""Direct test of Google Scholar provider with detailed logging"""

import sys
sys.path.insert(0, '/Users/adrianstiermbp2023/litsearchapp')

from src.search.scholar import GoogleScholarProvider
from src.models import SearchQuery

def test_scholar_direct():
    print("=" * 80)
    print("GOOGLE SCHOLAR DIRECT TEST")
    print("=" * 80)

    # Create provider
    provider = GoogleScholarProvider(rate_limit=0.5)

    # Create query
    query = SearchQuery(
        query="machine learning",
        sources=["scholar"],
        max_results=5
    )

    print(f"\nSearching for: '{query.query}'")
    print(f"Max results: {query.max_results}")
    print("\nStarting search with anti-detection measures...")
    print("-" * 80)

    # Search
    papers = provider.search(query)

    print("-" * 80)
    print(f"\n✅ Search completed")
    print(f"Papers retrieved: {len(papers)}")

    if papers:
        print("\nFirst paper:")
        paper = papers[0]
        print(f"  Title: {paper.title}")
        print(f"  Authors: {', '.join([a.name for a in paper.authors[:3]])}")
        print(f"  Year: {paper.year}")
        print(f"  Citations: {paper.citations}")
    else:
        print("\n⚠️ No papers retrieved")
        print("This indicates Google Scholar is likely blocking the requests")
        print("despite our anti-detection measures.")

if __name__ == "__main__":
    test_scholar_direct()
