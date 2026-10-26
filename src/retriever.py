"""Retriever module connecting query embedding, FAISS search, and threshold filtering."""

from typing import Any
from src.config import SIMILARITY_THRESHOLD, TOP_K
from src.embedder import Embedder
from src.vector_store import VectorStore


class Retriever:
    """Retrieves relevant text chunks for a query using dense semantic search."""

    def __init__(
        self,
        embedder: Embedder,
        store: VectorStore,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
    ) -> None:
        """Initialize the retriever with an embedder and vector store."""
        self.embedder: Embedder = embedder
        self.store: VectorStore = store
        self.similarity_threshold: float = similarity_threshold

    def retrieve(
        self,
        query: str,
        k: int = TOP_K,
    ) -> list[tuple[dict[str, Any], float]]:
        """Retrieve top-k chunks exceeding the similarity threshold.

        Args:
            query: User's question or search query.
            k: Maximum number of chunks to return.

        Returns:
            List of (chunk_dict, score) tuples for matches with score >= SIMILARITY_THRESHOLD.
        """
        # Clean query and strip accidental wrapping quotes that distort embedding vectors
        clean_q = query.strip().strip('"\'“”`')
        if not clean_q or self.store.total_chunks == 0:
            return []

        query_emb = self.embedder.embed([clean_q])
        raw_results = self.store.search(query_emb, k=k)

        # Drop results below the similarity threshold
        filtered = [
            (chunk, score)
            for chunk, score in raw_results
            if score >= self.similarity_threshold
        ]
        return filtered
