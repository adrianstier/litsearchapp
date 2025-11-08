"""Deduplicate papers from multiple sources"""

from typing import List, Dict, Set
from difflib import SequenceMatcher
from src.models import Paper, Source


class Deduplicator:
    """Deduplicate papers from multiple sources"""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize deduplicator

        Args:
            similarity_threshold: Minimum similarity for title matching
        """
        self.similarity_threshold = similarity_threshold

    def deduplicate(self, papers: List[Paper]) -> List[Paper]:
        """
        Deduplicate list of papers

        Strategy:
        1. Group by DOI (exact match)
        2. Group by PMID (exact match)
        3. Group by title similarity
        4. Merge metadata from duplicates

        Args:
            papers: List of papers to deduplicate

        Returns:
            List of unique papers with merged metadata
        """
        if not papers:
            return []

        # Build indices
        doi_index: Dict[str, List[Paper]] = {}
        pmid_index: Dict[str, List[Paper]] = {}
        arxiv_index: Dict[str, List[Paper]] = {}
        no_id_papers: List[Paper] = []

        for paper in papers:
            if paper.doi:
                doi_index.setdefault(paper.doi, []).append(paper)
            elif paper.pmid:
                pmid_index.setdefault(paper.pmid, []).append(paper)
            elif paper.arxiv_id:
                arxiv_index.setdefault(paper.arxiv_id, []).append(paper)
            else:
                no_id_papers.append(paper)

        # Merge papers with same DOI
        merged_papers = []
        processed_ids = set()

        # Process DOI groups
        for doi, group in doi_index.items():
            merged = self._merge_paper_group(group)
            merged_papers.append(merged)
            processed_ids.add(f"doi:{doi}")

        # Process PMID groups (excluding those already processed via DOI)
        for pmid, group in pmid_index.items():
            # Check if any paper in group was already processed
            if not any(p.doi and f"doi:{p.doi}" in processed_ids for p in group):
                merged = self._merge_paper_group(group)
                merged_papers.append(merged)
                processed_ids.add(f"pmid:{pmid}")

        # Process arXiv groups
        for arxiv_id, group in arxiv_index.items():
            # Check if any paper in group was already processed
            if not any(
                (p.doi and f"doi:{p.doi}" in processed_ids) or
                (p.pmid and f"pmid:{p.pmid}" in processed_ids)
                for p in group
            ):
                merged = self._merge_paper_group(group)
                merged_papers.append(merged)
                processed_ids.add(f"arxiv:{arxiv_id}")

        # Process papers without IDs (match by title)
        title_groups = self._group_by_title_similarity(no_id_papers)
        for group in title_groups:
            # Check if this paper might be a duplicate of an already processed paper
            is_duplicate = False
            for processed in merged_papers:
                if self._titles_similar(group[0].title, processed.title):
                    # Merge with existing paper
                    self._merge_into(processed, group)
                    is_duplicate = True
                    break

            if not is_duplicate:
                merged = self._merge_paper_group(group)
                merged_papers.append(merged)

        return merged_papers

    def _merge_paper_group(self, papers: List[Paper]) -> Paper:
        """
        Merge a group of duplicate papers

        Args:
            papers: Group of duplicate papers

        Returns:
            Single merged paper
        """
        if len(papers) == 1:
            return papers[0]

        # Start with the first paper as base
        merged = papers[0].model_copy()

        # Merge data from other papers
        for paper in papers[1:]:
            self._merge_into(merged, [paper])

        return merged

    def _merge_into(self, target: Paper, papers: List[Paper]):
        """
        Merge papers into target paper

        Args:
            target: Target paper to merge into
            papers: Papers to merge
        """
        for paper in papers:
            # Merge sources
            for source in paper.sources:
                if source not in target.sources:
                    target.sources.append(source)

            # Prefer non-empty fields
            if not target.abstract and paper.abstract:
                target.abstract = paper.abstract
            elif paper.abstract and len(paper.abstract) > len(target.abstract or ""):
                target.abstract = paper.abstract

            if not target.doi and paper.doi:
                target.doi = paper.doi

            if not target.pmid and paper.pmid:
                target.pmid = paper.pmid

            if not target.pmcid and paper.pmcid:
                target.pmcid = paper.pmcid

            if not target.arxiv_id and paper.arxiv_id:
                target.arxiv_id = paper.arxiv_id

            if not target.pdf_url and paper.pdf_url:
                target.pdf_url = paper.pdf_url

            if not target.url and paper.url:
                target.url = paper.url

            # Take maximum citation count
            if paper.citations > target.citations:
                target.citations = paper.citations

            # Merge keywords
            for keyword in paper.keywords:
                if keyword not in target.keywords:
                    target.keywords.append(keyword)

            # Update paper type if unknown
            if target.paper_type == "unknown" and paper.paper_type != "unknown":
                target.paper_type = paper.paper_type

            # Prefer more complete author lists
            if len(paper.authors) > len(target.authors):
                target.authors = paper.authors

    def _group_by_title_similarity(self, papers: List[Paper]) -> List[List[Paper]]:
        """
        Group papers by title similarity

        Args:
            papers: Papers to group

        Returns:
            List of paper groups
        """
        if not papers:
            return []

        groups = []
        processed = set()

        for i, paper in enumerate(papers):
            if i in processed:
                continue

            group = [paper]
            processed.add(i)

            # Find similar papers
            for j, other in enumerate(papers[i+1:], i+1):
                if j in processed:
                    continue

                if self._titles_similar(paper.title, other.title):
                    group.append(other)
                    processed.add(j)

            groups.append(group)

        return groups

    def _titles_similar(self, title1: str, title2: str) -> bool:
        """
        Check if two titles are similar enough to be the same paper

        Args:
            title1: First title
            title2: Second title

        Returns:
            True if titles are similar
        """
        if not title1 or not title2:
            return False

        # Normalize titles
        t1 = self._normalize_title(title1)
        t2 = self._normalize_title(title2)

        # Check exact match after normalization
        if t1 == t2:
            return True

        # Check similarity
        similarity = SequenceMatcher(None, t1, t2).ratio()
        return similarity >= self.similarity_threshold

    def _normalize_title(self, title: str) -> str:
        """
        Normalize title for comparison

        Args:
            title: Title to normalize

        Returns:
            Normalized title
        """
        # Convert to lowercase
        title = title.lower()

        # Remove punctuation and extra whitespace
        import re
        title = re.sub(r'[^\w\s]', ' ', title)
        title = ' '.join(title.split())

        return title