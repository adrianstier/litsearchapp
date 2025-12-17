"""Semantic search service with embeddings and reranking"""

import numpy as np
from typing import List, Tuple, Optional
from fastembed import TextEmbedding
import json
from pathlib import Path

class SemanticSearchService:
    """Service for semantic search and reranking using embeddings"""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """Initialize with embedding model"""
        self._model = None
        self._model_name = model_name
        self._embedding_cache = {}
        self._cache_file = Path.home() / ".config" / "litsearch" / "embedding_cache.json"
        self._load_cache()

    @property
    def model(self):
        """Lazy load embedding model"""
        if self._model is None:
            print("Loading embedding model...")
            self._model = TextEmbedding(model_name=self._model_name)
            print(f"✓ Loaded {self._model_name}")
        return self._model

    def _load_cache(self):
        """Load embedding cache from disk"""
        try:
            if self._cache_file.exists():
                with open(self._cache_file, 'r') as f:
                    self._embedding_cache = json.load(f)
        except Exception as e:
            print(f"⚠ Failed to load embedding cache: {e}")
            self._embedding_cache = {}

    def _save_cache(self):
        """Save embedding cache to disk"""
        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._cache_file, 'w') as f:
                json.dump(self._embedding_cache, f)
        except Exception as e:
            print(f"⚠ Failed to save embedding cache: {e}")

    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text, using cache if available"""
        # Create cache key from first 100 chars
        cache_key = text[:100]

        if cache_key in self._embedding_cache:
            return np.array(self._embedding_cache[cache_key])

        # Generate embedding
        embeddings = list(self.model.embed([text]))
        embedding = embeddings[0]

        # Cache it
        self._embedding_cache[cache_key] = embedding.tolist()

        # Periodically save cache
        if len(self._embedding_cache) % 100 == 0:
            self._save_cache()

        return embedding

    def get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Get embeddings for multiple texts efficiently"""
        # Check cache first
        results = []
        texts_to_embed = []
        indices_to_embed = []

        for i, text in enumerate(texts):
            cache_key = text[:100]
            if cache_key in self._embedding_cache:
                results.append(np.array(self._embedding_cache[cache_key]))
            else:
                results.append(None)
                texts_to_embed.append(text)
                indices_to_embed.append(i)

        # Embed remaining texts
        if texts_to_embed:
            new_embeddings = list(self.model.embed(texts_to_embed))

            for idx, embedding in zip(indices_to_embed, new_embeddings):
                results[idx] = embedding
                cache_key = texts[idx][:100]
                self._embedding_cache[cache_key] = embedding.tolist()

        self._save_cache()
        return results

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def rerank_papers(self, query: str, papers: List[dict],
                      text_field: str = "abstract",
                      top_k: Optional[int] = None) -> List[Tuple[dict, float]]:
        """
        Rerank papers by semantic similarity to query

        Args:
            query: Search query
            papers: List of paper dictionaries
            text_field: Field to use for similarity (default: abstract)
            top_k: Return only top k results (None for all)

        Returns:
            List of (paper, similarity_score) tuples sorted by score
        """
        if not papers:
            return []

        # Get query embedding
        query_embedding = self.get_embedding(query)

        # Get paper embeddings
        paper_texts = []
        for paper in papers:
            # Combine title and abstract for better matching
            title = paper.get('title', '')
            abstract = paper.get(text_field, '') or paper.get('abstract', '')
            text = f"{title} {abstract}".strip()
            paper_texts.append(text if text else "No content available")

        paper_embeddings = self.get_embeddings_batch(paper_texts)

        # Calculate similarities
        scored_papers = []
        for paper, embedding in zip(papers, paper_embeddings):
            similarity = self.cosine_similarity(query_embedding, embedding)
            scored_papers.append((paper, similarity))

        # Sort by similarity
        scored_papers.sort(key=lambda x: x[1], reverse=True)

        if top_k:
            scored_papers = scored_papers[:top_k]

        return scored_papers

    def hybrid_score(self, query: str, papers: List[dict],
                     keyword_weight: float = 0.3,
                     semantic_weight: float = 0.7) -> List[Tuple[dict, float]]:
        """
        Calculate hybrid score combining keyword relevance and semantic similarity

        Args:
            query: Search query
            papers: List of papers with existing relevance_score
            keyword_weight: Weight for keyword-based score
            semantic_weight: Weight for semantic score

        Returns:
            List of (paper, hybrid_score) tuples
        """
        if not papers:
            return []

        # Get semantic scores
        semantic_results = self.rerank_papers(query, papers)
        semantic_scores = {id(p): score for p, score in semantic_results}

        # Calculate hybrid scores
        hybrid_results = []
        for paper in papers:
            # Get existing relevance score (normalized to 0-1)
            keyword_score = paper.get('relevance_score', 0.5)
            if keyword_score > 1:
                keyword_score = keyword_score / 100  # Normalize if percentage

            semantic_score = semantic_scores.get(id(paper), 0.5)

            # Combine scores
            hybrid = (keyword_weight * keyword_score +
                     semantic_weight * semantic_score)

            hybrid_results.append((paper, hybrid))

        # Sort by hybrid score
        hybrid_results.sort(key=lambda x: x[1], reverse=True)

        return hybrid_results

    def find_similar_papers(self, paper: dict, all_papers: List[dict],
                           top_k: int = 5) -> List[Tuple[dict, float]]:
        """
        Find papers similar to a given paper

        Args:
            paper: Reference paper
            all_papers: List of papers to search through
            top_k: Number of similar papers to return

        Returns:
            List of (similar_paper, similarity_score) tuples
        """
        # Create text from reference paper
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        ref_text = f"{title} {abstract}"

        # Get reference embedding
        ref_embedding = self.get_embedding(ref_text)

        # Get embeddings for all papers
        paper_texts = []
        for p in all_papers:
            text = f"{p.get('title', '')} {p.get('abstract', '')}"
            paper_texts.append(text)

        paper_embeddings = self.get_embeddings_batch(paper_texts)

        # Calculate similarities (excluding self)
        scored_papers = []
        for p, embedding in zip(all_papers, paper_embeddings):
            # Skip self
            if p.get('id') == paper.get('id') or p.get('paper_id') == paper.get('paper_id'):
                continue

            similarity = self.cosine_similarity(ref_embedding, embedding)
            scored_papers.append((p, similarity))

        # Sort and return top k
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        return scored_papers[:top_k]


# Global instance
_semantic_service = None

def get_semantic_service() -> SemanticSearchService:
    """Get or create semantic search service singleton"""
    global _semantic_service
    if _semantic_service is None:
        _semantic_service = SemanticSearchService()
    return _semantic_service
