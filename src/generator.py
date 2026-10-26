"""Answer generation module supporting Gemini 2.0 and robust extractive fallback."""

import logging
from typing import Any
from src.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)


def _normalize_chunks(chunks: list[Any]) -> list[dict[str, Any]]:
    """Normalize input chunks whether given as dicts or (chunk, score) tuples."""
    normalized: list[dict[str, Any]] = []
    for item in chunks:
        if isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], dict):
            normalized.append(item[0])
        elif isinstance(item, dict):
            normalized.append(item)
    return normalized


def _extractive_answer(chunks: list[dict[str, Any]]) -> str:
    """Format top 2 passages as quoted text with page citations."""
    top_passages = chunks[:2]
    formatted: list[str] = []
    for ch in top_passages:
        text = ch.get("text", "").strip()
        source = ch.get("source", "document.pdf")
        page = ch.get("page", 1)
        formatted.append(f'"{text}" [{source}, p.{page}]')
    return "\n\n".join(formatted)


def generate_answer(
    question: str,
    chunks: list[Any],
    api_key: str | None = None,
    model_name: str | None = None,
) -> dict[str, str]:
    """Generate an answer grounded in retrieved chunks using Gemini or extractive fallback.

    Args:
        question: User's question.
        chunks: List of retrieved chunk dicts or (chunk_dict, score) tuples.
        api_key: Optional Gemini API key override (defaults to config.GEMINI_API_KEY).
        model_name: Optional Gemini model name override (defaults to config.GEMINI_MODEL).

    Returns:
        Dict with 'answer' string and 'mode' string ('gemini', 'extractive', or 'no_context').
    """
    normalized_chunks = _normalize_chunks(chunks)

    # 1. No context found
    if not normalized_chunks:
        return {
            "answer": "I could not find this in the uploaded documents.",
            "mode": "no_context",
        }

    active_key = api_key if api_key is not None else GEMINI_API_KEY
    active_model = model_name if model_name is not None else GEMINI_MODEL

    # 2. Attempt Gemini generation if API key is present
    if active_key and active_key.strip():
        try:
            from google import genai

            context_parts = []
            for ch in normalized_chunks:
                source = ch.get("source", "document.pdf")
                page = ch.get("page", 1)
                text = ch.get("text", "").strip()
                context_parts.append(f"[{source}, p.{page}]\n{text}")

            context_str = "\n\n".join(context_parts)

            prompt = (
                "You are an academic study assistant. Answer ONLY from the context provided below. "
                "If the answer is not in the context, say you could not find it in the uploaded documents. "
                "Cite sources as [file, p.N] directly where relevant facts are mentioned.\n\n"
                f"Context:\n{context_str}\n\n"
                f"Question: {question.strip()}\n\n"
                "Answer:"
            )

            client = genai.Client(api_key=active_key.strip())
            candidate_models = [active_model, "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]
            
            for candidate in dict.fromkeys(candidate_models):
                if not candidate:
                    continue
                try:
                    response = client.models.generate_content(
                        model=candidate,
                        contents=prompt,
                    )
                    if response and response.text and response.text.strip():
                        return {
                            "answer": response.text.strip(),
                            "mode": "gemini",
                        }
                except Exception as inner_err:
                    logger.debug("Candidate model %s failed: %s", candidate, inner_err)
        except Exception as e:
            logger.warning("Gemini generation failed; falling back to extractive mode. Error: %s", e)

    # 3. Fallback to extractive mode
    return {
        "answer": _extractive_answer(normalized_chunks),
        "mode": "extractive",
    }
