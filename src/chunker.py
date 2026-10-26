"""Text chunking module with page-boundary preservation and sentence-boundary trimming."""

from typing import Any
from src.config import CHUNK_OVERLAP, CHUNK_SIZE

# Allowed maximum overshoot when finding a clean sentence boundary
BOUNDARY_TOLERANCE: int = 50


def _find_cut_point(text: str, start: int, target_end: int, max_end: int) -> int:
    """Find the best cut point near target_end, preferring sentence boundaries."""
    if target_end >= len(text):
        return len(text)

    # Search window for sentence terminators
    window_start = max(start + (target_end - start) // 2, target_end - 100)
    window_end = min(len(text), max_end)
    search_region = text[window_start:window_end]

    sentence_ends = [". ", ".\n", "? ", "?\n", "! ", "!\n", "\n\n"]
    best_pos = -1

    for delim in sentence_ends:
        idx = search_region.rfind(delim)
        if idx != -1:
            abs_pos = window_start + idx + len(delim)
            if abs_pos <= max_end and abs_pos > best_pos:
                best_pos = abs_pos

    if best_pos != -1:
        return best_pos

    # Secondary preference: line break or comma/semicolon before target_end
    for delim in ["\n", "; ", ", "]:
        idx = search_region.rfind(delim)
        if idx != -1:
            abs_pos = window_start + idx + len(delim)
            if abs_pos <= target_end and abs_pos > best_pos:
                best_pos = abs_pos

    if best_pos != -1:
        return best_pos

    # Tertiary preference: word space before target_end
    space_idx = search_region.rfind(" ")
    if space_idx != -1:
        abs_pos = window_start + space_idx + 1
        if abs_pos <= target_end:
            return abs_pos

    return target_end


def chunk_pages(
    pages: list[dict[str, Any]],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    tolerance: int = BOUNDARY_TOLERANCE,
) -> list[dict[str, Any]]:
    """Chunk extracted pages into overlapping text segments without crossing page boundaries.

    Args:
        pages: List of dicts with 'text', 'source', 'page'.
        chunk_size: Target character count per chunk.
        chunk_overlap: Number of characters to overlap between adjacent chunks.
        tolerance: Maximum characters above chunk_size allowed to complete a sentence.

    Returns:
        List of dicts with 'text', 'source', 'page', and 'chunk_id'.
    """
    chunks: list[dict[str, Any]] = []

    for page_dict in pages:
        source = page_dict["source"]
        page_num = page_dict["page"]
        text = page_dict["text"].strip()

        if not text:
            continue

        if len(text) <= chunk_size + tolerance:
            chunks.append({
                "text": text,
                "source": source,
                "page": page_num,
                "chunk_id": f"{source}_p{page_num}_c0",
            })
            continue

        start = 0
        chunk_idx = 0
        total_len = len(text)

        while start < total_len:
            target_end = start + chunk_size
            max_end = min(total_len, target_end + tolerance)

            cut_end = _find_cut_point(text, start, target_end, max_end)

            chunk_text = text[start:cut_end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "source": source,
                    "page": page_num,
                    "chunk_id": f"{source}_p{page_num}_c{chunk_idx}",
                })
                chunk_idx += 1

            if cut_end >= total_len:
                break

            # Advance start with overlap, guaranteeing forward progress
            next_start = cut_end - chunk_overlap
            start = max(start + 1, next_start)

    return chunks
