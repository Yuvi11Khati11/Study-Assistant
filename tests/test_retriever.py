"""Integration tests for the Retriever module."""

from pathlib import Path
import sys

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.make_sample_pdf import generate_sample_pdf
from src.chunker import chunk_pages
from src.config import SIMILARITY_THRESHOLD
from src.embedder import Embedder
from src.pdf_loader import load_pdf
from src.retriever import Retriever
from src.vector_store import VectorStore


def test_retriever_finds_database_page_in_top_2_for_sql_query() -> None:
    """Ensure a query about SQL retrieves the Databases page (page 2) in the top 2 results."""
    sample_pdf = Path("data") / "sample" / "sample_notes.pdf"
    if not sample_pdf.exists():
        generate_sample_pdf(sample_pdf)

    pages = load_pdf(sample_pdf)
    chunks = chunk_pages(pages)

    embedder = Embedder()
    store = VectorStore()
    store.clear()

    texts = [c["text"] for c in chunks]
    embeddings = embedder.embed(texts)
    store.add(embeddings, chunks)

    retriever = Retriever(embedder=embedder, store=store, similarity_threshold=SIMILARITY_THRESHOLD)

    # Query about SQL and databases
    query = "How do relational SQL joins and normalization work in databases?"
    results = retriever.retrieve(query, k=2)

    assert len(results) >= 1, "Expected at least 1 retrieved chunk above similarity threshold"

    # Verify that the Databases page (page 2) is in the top 2 results
    top_pages = [chunk["page"] for chunk, score in results[:2]]
    assert 2 in top_pages, f"Expected page 2 in top 2 results, got {top_pages}"

    # Verify similarity threshold enforcement
    for chunk, score in results:
        assert score >= SIMILARITY_THRESHOLD, f"Score {score} fell below threshold {SIMILARITY_THRESHOLD}"
