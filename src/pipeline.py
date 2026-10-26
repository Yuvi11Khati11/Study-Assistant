"""High-level RAG Pipeline coordinating ingestion, indexing, retrieval, and answering."""

from pathlib import Path
from typing import Any
from src.chunker import chunk_pages
from src.config import TOP_K
from src.embedder import Embedder
from src.generator import generate_answer
from src.pdf_loader import load_pdf
from src.retriever import Retriever
from src.vector_store import VectorStore


class RAGPipeline:
    """End-to-end Retrieval-Augmented Generation pipeline for Study Assistant."""

    def __init__(
        self,
        embedder: Embedder | None = None,
        store: VectorStore | None = None,
        retriever: Retriever | None = None,
    ) -> None:
        """Initialize pipeline components with defaults or provided instances."""
        self.embedder: Embedder = embedder or Embedder()
        self.store: VectorStore = store or VectorStore()
        self.retriever: Retriever = retriever or Retriever(self.embedder, self.store)

    def ingest(self, files: list[str | Path | Any]) -> int:
        """Ingest one or more PDF files into the vector store.

        Args:
            files: List of file paths or file-like objects (e.g., Streamlit UploadedFile).

        Returns:
            Number of new chunks added to the vector store.
        """
        all_new_chunks: list[dict[str, Any]] = []

        for file_or_path in files:
            pages = load_pdf(file_or_path)
            chunks = chunk_pages(pages)
            all_new_chunks.extend(chunks)

        if not all_new_chunks:
            return 0

        texts = [c["text"] for c in all_new_chunks]
        embeddings = self.embedder.embed(texts)
        self.store.add(embeddings, all_new_chunks)

        return len(all_new_chunks)

    def ask(self, question: str, k: int = TOP_K) -> dict[str, Any]:
        """Query the pipeline for an answer with citations and retrieved sources.

        Args:
            question: User's question.
            k: Top-k passages to retrieve.

        Returns:
            Dict containing:
                - 'answer': string answer.
                - 'mode': 'gemini' | 'extractive' | 'no_context'.
                - 'sources': list of dicts with 'source', 'page', 'score', and 'text'.
        """
        clean_q = question.strip().strip('"\'“”`')
        retrieved = self.retriever.retrieve(clean_q, k=k)

        sources: list[dict[str, Any]] = []
        for chunk, score in retrieved:
            sources.append({
                "source": chunk.get("source", "document.pdf"),
                "page": chunk.get("page", 1),
                "score": float(score),
                "text": chunk.get("text", ""),
            })

        gen_result = generate_answer(question, retrieved)

        return {
            "answer": gen_result["answer"],
            "mode": gen_result["mode"],
            "sources": sources,
        }

    def reset(self) -> None:
        """Clear all indexed documents and reset the vector store."""
        self.store.clear()
