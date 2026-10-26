"""In-memory and persistent FAISS vector store using inner product for cosine similarity."""

import json
from pathlib import Path
from typing import Any
import faiss
import numpy as np


class VectorStore:
    """FAISS-backed vector store for normalized passage embeddings."""

    def __init__(self, dimension: int | None = None) -> None:
        """Initialize empty vector store."""
        self.dimension: int | None = dimension
        self.index: faiss.IndexFlatIP | None = (
            faiss.IndexFlatIP(dimension) if dimension is not None else None
        )
        self.chunks: list[dict[str, Any]] = []

    def add(self, embeddings: np.ndarray, chunks: list[dict[str, Any]]) -> None:
        """Add normalized embeddings and their corresponding chunks with deduplication.

        Args:
            embeddings: Float32 array of shape (N, dimension).
            chunks: List of chunk metadata dicts of length N.
        """
        if len(chunks) == 0 or len(embeddings) == 0:
            return

        # Deduplicate incoming chunks against existing index entries by chunk_id
        existing_ids = {c.get("chunk_id") for c in self.chunks if "chunk_id" in c}
        keep_indices: list[int] = []
        keep_chunks: list[dict[str, Any]] = []

        for i, c in enumerate(chunks):
            cid = c.get("chunk_id")
            if not cid or cid not in existing_ids:
                keep_chunks.append(c)
                keep_indices.append(i)
                if cid:
                    existing_ids.add(cid)

        if not keep_chunks:
            return

        filtered_embeddings = np.ascontiguousarray(embeddings[keep_indices], dtype=np.float32)

        if self.index is None:
            self.dimension = filtered_embeddings.shape[1]
            self.index = faiss.IndexFlatIP(self.dimension)

        self.index.add(filtered_embeddings)
        self.chunks.extend(keep_chunks)

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 4,
    ) -> list[tuple[dict[str, Any], float]]:
        """Search the top-k most similar chunks.

        Args:
            query_embedding: Normalized 1D or 2D float32 numpy array.
            k: Maximum number of neighbors to return.

        Returns:
            List of (chunk_dict, score) tuples ordered by descending similarity.
        """
        if self.index is None or self.index.ntotal == 0 or len(self.chunks) == 0:
            return []

        query = np.ascontiguousarray(query_embedding, dtype=np.float32)
        if query.ndim == 1:
            query = query.reshape(1, -1)

        k_search = min(k, self.index.ntotal)
        scores, indices = self.index.search(query, k_search)

        results: list[tuple[dict[str, Any], float]] = []
        for idx, score in zip(indices[0], scores[0]):
            if 0 <= idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))

        return results

    def save(self, dir_path: str | Path) -> None:
        """Save the FAISS index and chunk metadata to a directory."""
        directory = Path(dir_path)
        directory.mkdir(parents=True, exist_ok=True)

        index_file = directory / "index.faiss"
        chunks_file = directory / "chunks.json"

        if self.index is not None:
            faiss.write_index(self.index, str(index_file))
        else:
            if index_file.exists():
                index_file.unlink()

        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)

    def load(self, dir_path: str | Path) -> None:
        """Load the FAISS index and chunk metadata from a directory."""
        directory = Path(dir_path)
        index_file = directory / "index.faiss"
        chunks_file = directory / "chunks.json"

        if index_file.exists():
            self.index = faiss.read_index(str(index_file))
            self.dimension = self.index.d
        else:
            self.index = None
            self.dimension = None

        if chunks_file.exists():
            with open(chunks_file, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
        else:
            self.chunks = []

    def clear(self) -> None:
        """Reset the index and stored chunk metadata."""
        self.index = None
        self.dimension = None
        self.chunks = []

    @property
    def total_chunks(self) -> int:
        """Return total number of chunks currently indexed."""
        return len(self.chunks)
