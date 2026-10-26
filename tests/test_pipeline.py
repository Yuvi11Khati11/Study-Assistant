"""Integration tests for the end-to-end RAGPipeline."""

from pathlib import Path
import sys
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.make_sample_pdf import generate_sample_pdf
from src.pipeline import RAGPipeline


@pytest.fixture
def sample_pdf_path() -> Path:
    """Fixture ensuring the sample PDF is present."""
    target = Path("data") / "sample" / "sample_notes.pdf"
    if not target.exists():
        generate_sample_pdf(target)
    return target


def test_pipeline_extractive_mode_with_unset_gemini_key(
    monkeypatch: pytest.MonkeyPatch,
    sample_pdf_path: Path,
) -> None:
    """Ensure pipeline operates in extractive mode when GEMINI_API_KEY is unset."""
    # Ensure GEMINI_API_KEY is unset
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("src.generator.GEMINI_API_KEY", None)
    monkeypatch.setattr("src.config.GEMINI_API_KEY", None)

    pipeline = RAGPipeline()
    pipeline.reset()

    # 1. Ingest sample PDF
    chunk_count = pipeline.ingest([sample_pdf_path])
    assert chunk_count > 0, "Expected chunks to be indexed"

    # 2. Ask a relevant question
    result = pipeline.ask("What is supervised learning and how does it differ from unsupervised?")

    assert result["mode"] == "extractive", f"Expected mode 'extractive', got {result['mode']}"
    assert len(result["sources"]) >= 1, "Expected at least one source returned"
    assert "sample_notes.pdf" in result["sources"][0]["source"]
    assert result["sources"][0]["page"] == 1
    assert "sample_notes.pdf, p.1" in result["answer"] or "p.1" in result["answer"]
    assert len(result["answer"].strip()) > 20


def test_pipeline_returns_could_not_find_for_unrelated_query(
    monkeypatch: pytest.MonkeyPatch,
    sample_pdf_path: Path,
) -> None:
    """Ensure pipeline refuses unrelated questions falling below similarity threshold."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("src.generator.GEMINI_API_KEY", None)
    monkeypatch.setattr("src.config.GEMINI_API_KEY", None)

    pipeline = RAGPipeline()
    pipeline.reset()
    pipeline.ingest([sample_pdf_path])

    # Ask completely unrelated question
    result = pipeline.ask("What is the capital of France?")

    assert result["mode"] == "no_context", f"Expected mode 'no_context', got {result['mode']}"
    assert result["answer"] == "I could not find this in the uploaded documents."
    assert result["sources"] == []
