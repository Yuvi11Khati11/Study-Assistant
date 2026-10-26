"""Retrieval evaluation and faithfulness proxy benchmark for Study Assistant."""

import json
from pathlib import Path
import re
import sys
from typing import Any
import numpy as np

# Ensure project root is in sys.path when running script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.generator import generate_answer
from src.pipeline import RAGPipeline


def split_sentences(text: str) -> list[str]:
    """Split text into individual sentences using punctuation boundary heuristics."""
    # Remove citation brackets like [sample_notes.pdf, p.1] temporarily for clean sentence splitting
    cleaned = re.sub(r"\[[^\]]+\]", "", text).strip()
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", cleaned)
    return [s.strip() for s in raw_sentences if len(s.strip()) > 5]


def evaluate_study_assistant(
    sample_pdf_path: Path,
    eval_set_path: Path,
    results_path: Path,
) -> dict[str, Any]:
    """Run retrieval evaluation and compute Hit@k, MRR, and Faithfulness Proxy."""
    pipeline = RAGPipeline()
    pipeline.reset()

    if not sample_pdf_path.exists():
        raise FileNotFoundError(f"Sample PDF not found at {sample_pdf_path}. Run eval/make_sample_pdf.py first.")

    pipeline.ingest([sample_pdf_path])

    with open(eval_set_path, "r", encoding="utf-8") as f:
        eval_set: list[dict[str, Any]] = json.load(f)

    hits_at_1: list[float] = []
    hits_at_3: list[float] = []
    hits_at_4: list[float] = []
    reciprocal_ranks: list[float] = []
    faithfulness_scores: list[float] = []
    details: list[dict[str, Any]] = []

    for item in eval_set:
        question = item["question"]
        expected_source = item["expected_source"]
        expected_page = item["expected_page"]

        retrieved = pipeline.retriever.retrieve(question, k=4)

        # Hit@k and Reciprocal Rank calculation
        hit_1 = 0.0
        hit_3 = 0.0
        hit_4 = 0.0
        rr = 0.0

        for rank, (chunk, score) in enumerate(retrieved, start=1):
            chunk_source = chunk.get("source", "")
            chunk_page = chunk.get("page", 0)

            matches = (
                chunk_source.lower() == expected_source.lower()
                and chunk_page == expected_page
            )

            if matches:
                if rank == 1:
                    hit_1 = 1.0
                if rank <= 3:
                    hit_3 = 1.0
                if rank <= 4:
                    hit_4 = 1.0
                if rr == 0.0:
                    rr = 1.0 / rank

        hits_at_1.append(hit_1)
        hits_at_3.append(hit_3)
        hits_at_4.append(hit_4)
        reciprocal_ranks.append(rr)

        # Generate answer and compute Faithfulness Proxy
        gen_result = generate_answer(question, retrieved)
        answer = gen_result["answer"]
        mode = gen_result["mode"]

        # Faithfulness Proxy:
        # Fraction of answer sentences whose max cosine similarity to any retrieved chunk is >= 0.5
        if not retrieved or mode == "no_context":
            q_faithfulness = 1.0 if mode == "no_context" else 0.0
        else:
            sentences = split_sentences(answer)
            if not sentences:
                q_faithfulness = 1.0
            else:
                chunk_texts = [c.get("text", "") for c, _ in retrieved]
                chunk_embeddings = pipeline.embedder.embed(chunk_texts)  # (N, D) normalized

                sent_embeddings = pipeline.embedder.embed(sentences)  # (M, D) normalized
                # Matrix multiplication computes cosine similarity since vectors are L2-normalized
                sim_matrix = np.matmul(sent_embeddings, chunk_embeddings.T)  # (M, N)
                max_sims = np.max(sim_matrix, axis=1)  # (M,)

                supported = np.sum(max_sims >= 0.5)
                q_faithfulness = float(supported / len(sentences))

        faithfulness_scores.append(q_faithfulness)

        details.append({
            "question": question,
            "expected": {"source": expected_source, "page": expected_page},
            "retrieved_count": len(retrieved),
            "top_retrieved": [
                {
                    "source": c.get("source"),
                    "page": c.get("page"),
                    "score": round(s, 4),
                }
                for c, s in retrieved
            ],
            "hit_at_1": hit_1,
            "hit_at_3": hit_3,
            "hit_at_4": hit_4,
            "reciprocal_rank": round(rr, 4),
            "faithfulness_proxy": round(q_faithfulness, 4),
            "mode": mode,
        })

    summary = {
        "metrics": {
            "hit_rate_at_1": round(float(np.mean(hits_at_1)), 4),
            "hit_rate_at_3": round(float(np.mean(hits_at_3)), 4),
            "hit_rate_at_4": round(float(np.mean(hits_at_4)), 4),
            "mrr": round(float(np.mean(reciprocal_ranks)), 4),
            "faithfulness_proxy": round(float(np.mean(faithfulness_scores)), 4),
        },
        "total_questions": len(eval_set),
        "details": details,
    }

    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Print results to stdout
    print("\n" + "=" * 55)
    print("        STUDY ASSISTANT - RETRIEVAL EVALUATION")
    print("=" * 55)
    print(f"Total Evaluated Questions: {summary['total_questions']}")
    print("-" * 55)
    print(f"Hit Rate @ 1       : {summary['metrics']['hit_rate_at_1'] * 100:.2f}%")
    print(f"Hit Rate @ 3       : {summary['metrics']['hit_rate_at_3'] * 100:.2f}%")
    print(f"Hit Rate @ 4       : {summary['metrics']['hit_rate_at_4'] * 100:.2f}%")
    print(f"Mean Reciprocal Rank: {summary['metrics']['mrr']:.4f}")
    print(f"Faithfulness Proxy  : {summary['metrics']['faithfulness_proxy'] * 100:.2f}%")
    print("-" * 55)
    print("NOTE: 'Faithfulness Proxy' measures the fraction of answer sentences")
    print("having >= 0.5 cosine similarity to any retrieved chunk (proxy metric).")
    print(f"Full results saved to: {results_path}")
    print("=" * 55 + "\n")

    return summary


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    sample_pdf = base_dir / "data" / "sample" / "sample_notes.pdf"
    eval_json = base_dir / "eval" / "eval_set.json"
    results_json = base_dir / "eval" / "results.json"

    evaluate_study_assistant(sample_pdf, eval_json, results_json)
