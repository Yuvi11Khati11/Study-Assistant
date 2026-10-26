"""PDF extraction module using pypdf."""

from pathlib import Path
from typing import Any
import pypdf
from pypdf.errors import PdfReadError


def load_pdf(
    file_or_path: str | Path | Any,
    filename: str | None = None,
) -> list[dict[str, Any]]:
    """Extract text from a PDF file on a per-page basis.

    Args:
        file_or_path: Path to the PDF file or a file-like object (e.g., Streamlit UploadedFile).
        filename: Optional override for the document name used in citations.

    Returns:
        List of dicts containing 'text', 'source', and 'page' (1-indexed).

    Raises:
        ValueError: If the PDF cannot be read or contains no extractable text (e.g. scanned).
    """
    if filename:
        source = filename
    elif isinstance(file_or_path, (str, Path)):
        source = Path(file_or_path).name
    elif hasattr(file_or_path, "name") and file_or_path.name:
        source = Path(file_or_path.name).name
    else:
        source = "document.pdf"

    try:
        reader = pypdf.PdfReader(file_or_path)
    except Exception as e:
        raise ValueError(f"Failed to read PDF '{source}': {e}") from e

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as e:
            raise ValueError(f"PDF '{source}' is password protected and cannot be read.") from e

    extracted_pages: list[dict[str, Any]] = []

    try:
        total_pages = len(reader.pages)
    except Exception as e:
        raise ValueError(f"Failed to parse pages from PDF '{source}': {e}") from e

    if total_pages == 0:
        raise ValueError(f"The PDF '{source}' contains no pages.")

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        try:
            raw_text = page.extract_text() or ""
        except Exception as e:
            raw_text = ""

        cleaned_text = raw_text.strip()
        if cleaned_text:
            extracted_pages.append({
                "text": cleaned_text,
                "source": source,
                "page": page_num,
            })

    if not extracted_pages:
        # Check if Gemini API is available to attempt multimodal AI OCR on scanned PDFs
        from src.config import GEMINI_API_KEY, GEMINI_MODEL
        if GEMINI_API_KEY and GEMINI_API_KEY.strip():
            try:
                extracted_pages = _extract_via_gemini_ocr(file_or_path, source, total_pages)
            except Exception:
                extracted_pages = []

    if not extracted_pages:
        raise ValueError(
            f"The PDF '{source}' contains no extractable text. "
            "It may be scanned, image-only, or empty (no selectable digital text)."
        )

    return extracted_pages


def _extract_via_gemini_ocr(
    file_or_path: str | Path | Any,
    source: str,
    total_pages: int,
) -> list[dict[str, Any]]:
    """Use Gemini 2.0 Flash multimodal vision to extract text from scanned or non-selectable PDFs."""
    from google import genai
    from google.genai import types
    from src.config import GEMINI_API_KEY, GEMINI_MODEL

    if isinstance(file_or_path, (str, Path)):
        with open(file_or_path, "rb") as f:
            pdf_bytes = f.read()
    elif hasattr(file_or_path, "read"):
        if hasattr(file_or_path, "seek"):
            file_or_path.seek(0)
        pdf_bytes = file_or_path.read()
        if hasattr(file_or_path, "seek"):
            file_or_path.seek(0)
    else:
        return []

    client = genai.Client(api_key=GEMINI_API_KEY.strip())
    prompt = (
        "Extract all readable text, tables, and lists from this document page by page. "
        "Strictly delimit each page's content using '===PAGE_N===' where N is the 1-based page number. "
        "Do not summarize or add commentary."
    )

    candidate_models = [GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.8-flash"]
    response = None

    for candidate in dict.fromkeys(candidate_models):
        if not candidate:
            continue
        try:
            response = client.models.generate_content(
                model=candidate,
                contents=[
                    types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                    prompt,
                ],
            )
            if response and response.text and response.text.strip():
                break
        except Exception:
            continue

    if not response or not response.text:
        return []

    import re
    pages_data: list[dict[str, Any]] = []
    splits = re.split(r"===PAGE_(\d+)===", response.text)

    if len(splits) > 1:
        for i in range(1, len(splits), 2):
            page_num = int(splits[i])
            page_text = splits[i + 1].strip()
            if page_text:
                pages_data.append({"text": page_text, "source": source, "page": page_num})
    else:
        pages_data.append({"text": response.text.strip(), "source": source, "page": 1})

    return pages_data
