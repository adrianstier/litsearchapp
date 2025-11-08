#!/usr/bin/env python3
"""Basic test to verify the application works"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import SearchQuery, Source
from src.search.orchestrator import SearchOrchestrator


def test_basic_search():
    """Test basic search functionality"""
    print("Testing Literature Search Application\n")
    print("=" * 50)

    # Create a simple search query
    query = SearchQuery(
        query="COVID-19 vaccine",
        sources=[Source.PUBMED],
        max_results=5
    )

    print(f"Search query: {query.query}")
    print(f"Sources: {[s.value for s in query.sources]}")
    print(f"Max results: {query.max_results}\n")

    # Execute search
    print("Executing search...")
    orchestrator = SearchOrchestrator()
    results = orchestrator.search(query)

    print(f"\nResults:")
    print(f"- Papers found: {len(results.papers)}")
    print(f"- Search time: {results.search_time:.2f} seconds")
    print(f"- Sources searched: {[s.value for s in results.sources_searched]}")

    if results.errors:
        print(f"- Errors: {results.errors}")

    # Display papers
    if results.papers:
        print(f"\nTop {min(3, len(results.papers))} papers:")
        for i, paper in enumerate(results.papers[:3], 1):
            print(f"\n{i}. {paper.title}")
            if paper.authors:
                authors = ", ".join([a.name for a in paper.authors[:3]])
                if len(paper.authors) > 3:
                    authors += " et al."
                print(f"   Authors: {authors}")
            print(f"   Year: {paper.year or 'N/A'}")
            print(f"   Citations: {paper.citations}")
            if paper.doi:
                print(f"   DOI: {paper.doi}")

    print("\n" + "=" * 50)
    print("Test completed successfully!")


if __name__ == "__main__":
    test_basic_search()