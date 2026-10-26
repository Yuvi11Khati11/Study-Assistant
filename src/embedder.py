"""Embedding module using SentenceTransformers with model caching and L2 normalization."""

from typing import TYPE_CHECKING, Any, ClassVar
import numpy as np
from src.config import EMBED_MODEL

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


class Embedder:
    """Computes normalized dense embeddings for text passages and queries with lazy model loading."""

    _model_cache: ClassVar[dict[str, Any]] = {}

    def __init__(self, model_name: str = EMBED_MODEL) -> None:
        """Initialize embedder with lazy model loading to prevent startup latency."""
        self.model_name = model_name
        self._dimension: int | None = 384 if "MiniLM" in model_name else None

    @property
    def model(self) -> Any:
        """Lazily load and cache the SentenceTransformer model on first actual use."""
        if self.model_name not in Embedder._model_cache:
            from sentence_transformers import SentenceTransformer
            Embedder._model_cache[self.model_name] = SentenceTransformer(self.model_name)
        return Embedder._model_cache[self.model_name]

    @property
    def dimension(self) -> int:
        """Get the embedding vector dimension."""
        if self._dimension is not None:
            return self._dimension
        if hasattr(self.model, "get_embedding_dimension"):
            self._dimension = self.model.get_embedding_dimension()
        else:
            self._dimension = self.model.get_sentence_embedding_dimension()
        return self._dimension

    def embed(self, texts: list[str]) -> np.ndarray:
        """Generate normalized float32 embeddings for a list of texts.

        Args:
            texts: List of strings to embed.

        Returns:
            Normalized float32 numpy array of shape (len(texts), dimension).
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype=np.float32)
