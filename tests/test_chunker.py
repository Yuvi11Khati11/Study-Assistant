"""Unit tests for the chunker module."""

from pathlib import Path
import sys

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chunker import BOUNDARY_TOLERANCE, chunk_pages
from src.config import CHUNK_OVERLAP, CHUNK_SIZE


def test_chunks_do_not_exceed_chunk_size_plus_tolerance() -> None:
    """Ensure all chunks never exceed CHUNK_SIZE + BOUNDARY_TOLERANCE."""
    long_paragraph = (
        "Operating systems coordinate CPU scheduling, memory management, and file systems. "
        "Processes transition between ready, running, and waiting states. "
        "Round Robin scheduling allocates a fixed time quantum to each thread. "
        "Context switching preserves processor state in Process Control Blocks. "
    ) * 15  # ~1700 characters

    pages = [
        {"text": long_paragraph, "source": "os_notes.pdf", "page": 1}
    ]

    chunks = chunk_pages(pages, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    assert len(chunks) > 1, "Expected multiple chunks for long paragraph"
    max_allowed = CHUNK_SIZE + BOUNDARY_TOLERANCE

    for idx, chunk in enumerate(chunks):
        chunk_len = len(chunk["text"])
        assert chunk_len <= max_allowed, (
            f"Chunk {idx} length {chunk_len} exceeded maximum allowed {max_allowed}"
        )
        assert chunk["page"] == 1
        assert chunk["source"] == "os_notes.pdf"
        assert "chunk_id" in chunk


def test_chunk_overlap_works() -> None:
    """Ensure consecutive chunks from the same page share overlapping text."""
    long_text = (
        "Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau. "
        "Machine learning models identify patterns from empirical observations without explicit programming. "
        "Gradient descent minimizes the objective loss function by calculating partial derivatives. "
        "Regularization techniques such as Ridge and Lasso mitigate overfitting by penalizing complex weights. "
    ) * 8

    pages = [{"text": long_text, "source": "ml_notes.pdf", "page": 1}]
    chunks = chunk_pages(pages, chunk_size=500, chunk_overlap=100)

    assert len(chunks) >= 2, "Need at least 2 chunks to test overlap"

    # Verify that consecutive chunks share text content
    for i in range(len(chunks) - 1):
        c1_text = chunks[i]["text"]
        c2_text = chunks[i + 1]["text"]

        # Check if the start of chunk i+1 is present near the end of chunk i
        tail_c1 = c1_text[-120:]
        head_c2 = c2_text[:120]

        words_in_head = [w for w in head_c2.split() if len(w) > 4]
        overlap_found = any(word in tail_c1 for word in words_in_head)

        assert overlap_found, f"Expected overlapping words between chunk {i} and {i+1}"


def test_chunks_preserve_page_numbers_and_never_cross_pages() -> None:
    """Ensure chunks strictly retain their source page number and never cross page boundaries."""
    pages = [
        {"text": "Page one text on relational database schemas and primary keys.", "source": "db.pdf", "page": 1},
        {"text": "Page two text on ACID properties and B-tree indexing strategies.", "source": "db.pdf", "page": 2},
        {"text": "Page three text detailing SQL INNER JOIN and LEFT OUTER JOIN operations.", "source": "db.pdf", "page": 3},
    ]

    chunks = chunk_pages(pages, chunk_size=800, chunk_overlap=150)

    assert len(chunks) == 3
    for chunk, orig_page in zip(chunks, pages):
        assert chunk["page"] == orig_page["page"]
        assert chunk["source"] == orig_page["source"]
        assert chunk["text"] == orig_page["text"]
